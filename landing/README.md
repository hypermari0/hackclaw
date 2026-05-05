# HackClaw landing

Static marketing page for HackClaw. Plain HTML, no build step.

## Files

- `index.html` — single-page site
- `style.css` — design tokens and layout
- `profile.svg` — square logo, used for app icons and TAIKAI project avatar
- `cover.svg` — wide hero cover, used for OG image and TAIKAI project banner
- `favicon.svg` — favicon
- `vercel.json` — clean URLs and asset cache headers

## Deploy

```sh
cd landing
vercel deploy --prod
```

The first deploy links the directory to a Vercel project. Subsequent deploys
reuse the link. No framework preset is required, Vercel detects this as a
static project.

## Brand tokens

| Token       | Hex        | Usage              |
|-------------|------------|--------------------|
| claw        | `#FF3B47`  | primary, links     |
| claw soft   | `#FF5560`  | hover              |
| mint        | `#00F0B5`  | terminal accent    |
| carbon      | `#0B0B0F`  | background         |
| carbon-2    | `#15151D`  | surface            |
| carbon-3    | `#1F1F28`  | borders            |
| bone        | `#F4F4F0`  | foreground         |

Monospace face for kickers, code, and the wordmark. Sans-serif for body.
