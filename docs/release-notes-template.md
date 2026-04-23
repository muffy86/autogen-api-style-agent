# Release vX.Y.Z — <short headline>

_Release date: YYYY-MM-DD_

## TL;DR

<!-- One-paragraph summary. What shipped, who it matters to, why. -->

## Highlights

- **Feature A** — what it is and why users care.
- **Feature B** — what it is and why users care.
- **Performance** — measurable wins (latency, throughput, bundle size).

## New Features

- `#<pr>` — <title>. <one-line description>.

## Improvements

- `#<pr>` — <title>.

## Bug Fixes

- `#<pr>` — <title>. Fixes #<issue>.

## Breaking Changes

<!-- If none, write "None." -->

- `#<pr>` — <description>. **Migration**: <how to migrate>.

## Security

<!-- CVEs patched, deps bumped, auth changes. -->

- `#<pr>` — <description>.

## Dependencies

- Bumped `<pkg>` `<old>` → `<new>`.

## Infrastructure / CI

- `#<pr>` — <description>.

## Docs

- `#<pr>` — <description>.

## Contributors

Thanks to everyone who shipped this release:

- @<handle>

## Upgrade Guide

```bash
git pull origin main
pip install -e ".[dev]"
pnpm install --frozen-lockfile
pnpm run build
```

If upgrading from < vA.B.C, see breaking-changes section above.

## Rollback

If this release misbehaves:

- **Frontend (Vercel)**: promote the previous deployment from the Vercel dashboard.
- **Backend (Docker)**: redeploy the previous image tag: `docker pull ghcr.io/muffy86/autogen-api-style-agent:<previous-sha>`.
- **Git**: `git revert <merge-commit>` and re-deploy.

## Full Changelog

https://github.com/muffy86/autogen-api-style-agent/compare/v<previous>...v<this>
