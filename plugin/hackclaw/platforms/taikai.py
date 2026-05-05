"""TAIKAI platform adapter.

Two routes:
- mcp (default): dispatches to the TAIKAI MCP that Hermes has configured.
- graphql (fallback): direct GraphQL with TAIKAI_TOKEN.

Toggle with HACKCLAW_TAIKAI_VIA=mcp|graphql.

URL parsing: https://taikai.network/{org_slug}/hackathons/{challenge_slug}

Implementation note: the MCP route assumes Hermes exposes a way for plugin
tools to invoke a configured MCP source. The exact API for that varies by
Hermes version. If the MCP route raises NotImplementedError on your install,
set HACKCLAW_TAIKAI_VIA=graphql to fall back.
"""

import os
import re

import httpx

from hackclaw.platforms.base import (
    Brief,
    HackathonPlatform,
    ProjectDraft,
    ProjectUpdates,
    Submission,
    SubmissionResult,
)

TAIKAI_URL_RE = re.compile(
    r"https?://taikai\.network/(?:en/)?(?P<org>[^/]+)/hackathons/(?P<slug>[^/?#]+)"
)
GRAPHQL_ENDPOINT = "https://taikai.network/api/graphql"


def parse_taikai_url(url: str) -> tuple[str, str]:
    """Extract (org_slug, challenge_slug) from a TAIKAI hackathon URL."""
    m = TAIKAI_URL_RE.search(url)
    if not m:
        raise ValueError(f"Not a recognizable TAIKAI hackathon URL: {url}")
    return m.group("org"), m.group("slug")


class TaikaiPlatform(HackathonPlatform):
    """TAIKAI hackathon platform adapter.

    Route is selected at construction time from HACKCLAW_TAIKAI_VIA env var.
    """

    def __init__(self) -> None:
        self.route = os.environ.get("HACKCLAW_TAIKAI_VIA", "mcp")
        self._challenge_id_cache: dict[str, str] = {}
        if self.route == "graphql":
            token = os.environ.get("TAIKAI_TOKEN")
            if not token:
                raise RuntimeError(
                    "HACKCLAW_TAIKAI_VIA=graphql but TAIKAI_TOKEN is not set"
                )
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={"Authorization": f"Bearer {token}"},
            )
        elif self.route != "mcp":
            raise ValueError(
                f"HACKCLAW_TAIKAI_VIA must be 'mcp' or 'graphql', got: {self.route}"
            )

    # ---------- MCP route ----------

    async def _mcp_call(self, tool_name: str, args: dict) -> dict:
        """Dispatch a call to the TAIKAI MCP via Hermes.

        TODO: replace this stub with the actual Hermes MCP-dispatch API once
        confirmed against the upstream Hermes plugin authoring docs. The
        likely shape is something like:

            from hermes.mcp import call_mcp
            return await call_mcp("taikai", tool_name, args)

        Until that's confirmed, this raises NotImplementedError so the user
        can see the failure mode and switch to HACKCLAW_TAIKAI_VIA=graphql.
        """
        raise NotImplementedError(
            "MCP route not yet wired to Hermes's MCP-dispatch API. "
            "Set HACKCLAW_TAIKAI_VIA=graphql as a fallback. "
            f"(Wanted to call taikai.{tool_name} with {list(args.keys())})"
        )

    # ---------- GraphQL route ----------

    async def _gql(self, query: str, variables: dict) -> dict:
        r = await self._client.post(
            GRAPHQL_ENDPOINT, json={"query": query, "variables": variables}
        )
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            raise RuntimeError(f"TAIKAI GraphQL error: {data['errors']}")
        return data["data"]

    async def _resolve_challenge_id(self, hackathon_url: str) -> tuple[str, str, str]:
        org, slug = parse_taikai_url(hackathon_url)
        cache_key = f"{org}/{slug}"
        if cache_key in self._challenge_id_cache:
            return self._challenge_id_cache[cache_key], org, slug

        if self.route == "mcp":
            data = await self._mcp_call("taikai_get_challenge", {
                "organizationSlug": org,
                "slug": slug,
            })
            cid = data["challengeBySlug"]["id"]
        else:
            query = """
            query ChallengeBySlug($organizationSlug: String!, $slug: String!) {
              challengeBySlug(organizationSlug: $organizationSlug, slug: $slug) {
                id name shortDescription
              }
            }"""
            data = await self._gql(query, {"organizationSlug": org, "slug": slug})
            cid = data["challengeBySlug"]["id"]

        self._challenge_id_cache[cache_key] = cid
        return cid, org, slug

    # ---------- HackathonPlatform implementation ----------

    async def get_brief(self, hackathon_url: str) -> Brief:
        org, slug = parse_taikai_url(hackathon_url)
        if self.route == "mcp":
            data = await self._mcp_call("taikai_get_challenge", {
                "organizationSlug": org,
                "slug": slug,
            })
            c = data["challengeBySlug"]
        else:
            query = """
            query Brief($organizationSlug: String!, $slug: String!) {
              challengeBySlug(organizationSlug: $organizationSlug, slug: $slug) {
                id name shortDescription
                steps { name startDate }
              }
            }"""
            data = await self._gql(query, {"organizationSlug": org, "slug": slug})
            c = data["challengeBySlug"]

        return Brief(
            title=c["name"],
            short_description=c.get("shortDescription") or "",
            full_description=None,
            theme_tags=[],
            timeline={},
            prizes=[],
            rules=[],
            raw_url=hackathon_url,
        )

    async def list_existing_submissions(self, hackathon_url: str) -> list[Submission]:
        cid, _, _ = await self._resolve_challenge_id(hackathon_url)
        if self.route == "mcp":
            data = await self._mcp_call("taikai_list_projects", {
                "challengeId": cid,
                "page": 0,
            })
            projects = data.get("projects", [])
        else:
            query = """
            query Projects($challengeId: String!, $page: Int) {
              projects(challengeId: $challengeId, page: $page) {
                id name teaser
                author { username fullName }
              }
            }"""
            data = await self._gql(query, {"challengeId": cid, "page": 0})
            projects = data.get("projects", [])

        return [
            Submission(
                name=p["name"],
                teaser=p.get("teaser") or "",
                author=(p.get("author") or {}).get("fullName"),
            )
            for p in projects
        ]

    async def create_draft_project(self, hackathon_url: str, draft: ProjectDraft) -> str:
        cid, _, _ = await self._resolve_challenge_id(hackathon_url)
        if self.route == "mcp":
            data = await self._mcp_call("taikai_create_project", {
                "challengeId": cid,
                "name": draft.name,
                "teaser": draft.teaser,
                "industries": None,
                "members": None,
            })
            return data["createProject"]["id"]
        else:
            mutation = """
            mutation Create($challengeId: String!, $name: String!, $teaser: String!) {
              createProject(input: { challengeId: $challengeId, name: $name, teaser: $teaser }) {
                id
              }
            }"""
            data = await self._gql(
                mutation,
                {"challengeId": cid, "name": draft.name, "teaser": draft.teaser},
            )
            return data["createProject"]["id"]

    async def update_project(self, project_id: str, updates: ProjectUpdates) -> None:
        if self.route == "mcp":
            await self._mcp_call("taikai_update_project", {
                "projectId": project_id,
                "description": updates.description_html,
                "name": None,
                "teaser": None,
                "state": None,
            })
        else:
            mutation = """
            mutation Update($projectId: String!, $description: String) {
              updateProject(input: { id: $projectId, description: $description }) {
                id
              }
            }"""
            await self._gql(
                mutation,
                {"projectId": project_id, "description": updates.description_html},
            )

    async def submit(self, project_id: str) -> SubmissionResult:
        if self.route == "mcp":
            data = await self._mcp_call("taikai_update_project", {
                "projectId": project_id,
                "state": "ACTIVE",
                "name": None,
                "teaser": None,
                "description": None,
            })
            new_state = data["updateProject"]["state"]
        else:
            mutation = """
            mutation Publish($projectId: String!) {
              updateProject(input: { id: $projectId, state: ACTIVE }) {
                id state
              }
            }"""
            data = await self._gql(mutation, {"projectId": project_id})
            new_state = data["updateProject"]["state"]

        return SubmissionResult(
            project_id=project_id,
            state=new_state,
            public_url=None,
        )
