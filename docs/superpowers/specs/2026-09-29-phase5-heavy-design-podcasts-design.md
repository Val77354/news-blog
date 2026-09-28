# Phase 5: Heavy Design, Denser Posts, Podcasts — Design Spec

Date: 2026-09-29

## Purpose

Requested directly by the project owner: make the site's design heavier
and more animated (same color palette), add more information to the
bottom of every news post, grow the amount of seeded news content
substantially, and add a new "Podcasts" section with full backend CRUD,
covering links to podcasts on YouTube and other platforms. Builds on
the existing dark editorial design system (Phases 1-4) — no new colors,
no new frontend dependencies.

## 1. Heavier, layered background

A fixed, full-viewport background stack, purely decorative
(`aria-hidden`, `pointer-events: none`), sits behind all page content —
it never adds scrollable page height, so it doesn't fight the "no empty
space" goal, it fills what's already there.

- **Dot-grid texture** — a `body::before` radial-gradient dot pattern
  (`var(--border)` dots, low opacity) tiled at 28px, `z-index: -2`.
- **Grain texture** — a `body::after` tiny inline SVG noise data-URI,
  `mix-blend-mode: overlay`, opacity ~0.05, `z-index: -1`, for editorial
  print-like weight.
- **Drifting accent orbs** — a new always-mounted `Backdrop` component
  (mounted once in `App.jsx`, same pattern as `Ticker`) rendering three
  large blurred `var(--accent)` radial shapes, each with its own size,
  position, and `drift`-keyframe animation delay/duration (reusing the
  existing `drift` keyframe from Phase 3, scaled up), `z-index: -3`,
  opacity ~0.12-0.18, `filter: blur(80px)`.

All three layers freeze under `prefers-reduced-motion: reduce` (the dot
grid and grain are already static; `Backdrop`'s orbs get a scoped
override alongside the existing global one, same pattern `Ticker` used
in Phase 4).

## 2. Denser posts — more information per post

No new `Post` database columns (adding one previously required a manual
`ALTER TABLE` on the dev DB — Phase 2 — since this project doesn't use
migrations; everything below is computed client-side from data already
on the post).

New shared module `frontend/src/utils/postMeta.js`:
- `getTags(post)` — `[category, country, descriptor]`, where descriptor
  cycles through a fixed pool (`Analysis`, `Report`, `Feature`,
  `Briefing`, `Opinion`) keyed off `post.id` — deterministic, no
  randomness on re-render.
- `getReadTime(content)` — word count / 200wpm, rounded, `"N min read"`.
- `getStats(post)` — deterministic pseudo-random view/comment counts
  seeded from `post.id` (same formula every render/reload, not real
  analytics — decorative density, same tradeoff already accepted for
  Picsum photos).

**`PostCard`** gets a footer row: tag chips + read time + views/comments,
below the existing author/date meta line.

**`PostDetail`** gets the same tags/read-time/stats block after the
article body, plus:
- **Share buttons** — copy-link (clipboard + brief "Copied!" state,
  reusing the save-toast fade pattern), X, Facebook, and mailto intent
  links.
- **Related posts** — a "More like this" strip of up to 4 other posts
  sharing the same category or country, computed client-side from the
  already-fetched post list.

Edit/Delete actions stay at the very bottom, after the new content.

## 3. A lot more news

`SAMPLE_POSTS` grows from 12 to 40 entries (28 new), same tone/quality,
spread across the existing 5 categories and 12 countries, unique Picsum
seeds `newsblog-13` through `newsblog-40`.

## 4. Podcasts — full backend CRUD feature

**Backend** — new `Podcast` model (`backend/app/models.py`):
`id, title, host, description, cover_image_url (nullable), source,
external_url, created_at`. `source` is a plain string (no enum/FK,
consistent with `category`/`country`), constrained by a fixed frontend
`<select>` list: YouTube, Spotify, Apple Podcasts, SoundCloud, Other.
New `schemas.py` entries (`PodcastBase/Create/Update/Out`) and a new
`backend/app/routers/podcasts.py` with the same five-endpoint CRUD shape
as `posts.py` (no image-upload integration — `cover_image_url` is a
plain text field, not a file upload, since podcast art is sourced
externally). `main.py` includes the new router. `seed.py` gets a
`SAMPLE_PODCASTS` list (10 entries) seeded idempotently, independent of
the existing post-count check.

**On external links:** seeded entries cannot honestly link to specific
real YouTube videos or Spotify episodes that don't exist, so each
points at its platform's real general homepage
(`youtube.com`, `open.spotify.com`, `podcasts.apple.com`,
`soundcloud.com`) rather than a fabricated specific URL — the same
honesty tradeoff already made with Picsum stand-in photography.

**Frontend** — a new, dedicated `frontend/src/podcasts/` folder (per the
explicit request for "another folder for that"):
- `PodcastsPage.jsx`/`.css` — route `/podcasts`, grid of `PodcastCard`,
  "Add Podcast" button, loading/empty/error states matching `Home.jsx`.
- `PodcastCard.jsx`/`.css` — cover image, source badge (emoji per
  platform, no new icon dependency — same convention as country flags),
  title, host, description excerpt, "Listen on `<source>`" external
  link (`target="_blank" rel="noopener noreferrer"`), inline Edit/Delete.
- `PodcastForm.jsx`/`.css` — shared create/edit form (title, host,
  description, cover_image_url, source `<select>`, external_url).
- `NewPodcast.jsx`, `EditPodcast.jsx` — thin pages wrapping the form,
  mirroring `NewPost.jsx`/`EditPost.jsx`.

New `frontend/src/api/podcasts.js` (list/get/create/update/delete),
following the existing per-file `handleResponse` pattern used in
`api/uploads.js` rather than introducing a shared HTTP helper.

`constants.js` gains `PODCAST_SOURCES` (the five-item list) and
`PODCAST_SOURCE_ICONS` (emoji map). `Navbar` gains a "Podcasts" link.
`App.jsx` gains three routes: `/podcasts`, `/podcasts/new`,
`/podcasts/:id/edit`.

## 5. Footer

A new site-wide `Footer` component (`frontend/src/components/Footer.jsx`
/`.css`), mounted once in `App.jsx` after `<Routes>`, so it appears on
every page. Multi-column layout (wraps to one column on narrow
viewports): brand blurb, a Categories link list, a Countries link list
(with flags) that both set the Home page's existing URL filter params,
a quick-links column (Home/Podcasts/New Post), and a bottom bar with a
copyright line and the stack credit. This is what fills the empty space
at the bottom of every page, not just Home.

## Out of scope

Real file-upload for podcast cover art (external URL field only, like
the honesty tradeoff above). A `PodcastDetail` page — the external link
*is* the detail view, there's nothing more to show in-app. Real
analytics/comments (the stats block is decorative, clearly seeded, same
tradeoff as Picsum). Fake social-media icon links in the footer.

## Testing

Manual/browser verification, consistent with the rest of this project:
confirm the background layers render and don't introduce page scroll or
layout shift; confirm reduced-motion freezes the orbs; confirm tags/read
time/stats show on every card and the detail page; confirm share buttons
produce correct URLs and copy-link works; confirm related posts only
show relevant matches and none when there aren't any; confirm all 40
seeded posts load; confirm the Podcasts page lists, creates, edits, and
deletes podcasts against the live backend, and that "Listen on X" opens
the right platform in a new tab; confirm the footer appears on every
route and its links work.
