# Phase 1: Country + Category Filters — Design Spec

Date: 2026-09-27

## Purpose

Phase 1 of a 3-phase feature expansion to the News Blog:
- **Phase 1 (this spec):** country field + category tabs + country filter.
- **Phase 2 (future):** image upload/display on posts.
- **Phase 3 (future):** visual redesign with heavier animations, incorporating
  images once Phase 2 exists.

This spec covers Phase 1 only. Phases 2-3 get their own specs later.

## Goal

Let a reader narrow the post feed by category (single-select tabs, like a
news site's top nav) and by country (multi-select checklist), starting
with a fixed set of European countries. The country list is not hardcoded
in the schema — it's just whatever values exist in the `country` column —
so adding countries from other continents later is a data change, not a
schema change.

## Data model

Add one column to the existing `Post` model:
- `country: str` — plain string, same pattern as the existing `category`
  column. No enum, no separate `countries` table, no foreign key.

No other model changes.

## Seed data

The dev SQLite database (`backend/news_blog.db`, gitignored, disposable)
gets dropped and reseeded. `seed.py` is updated so every sample post gets
a `country` value drawn from this fixed list of 12 European countries:

```
United Kingdom, France, Germany, Italy, Spain, Netherlands, Poland,
Sweden, Ukraine, Greece, Portugal, Switzerland
```

This same list is also the single source of truth for the frontend's
country dropdown (in the post form) and checklist (in the filter) — it
lives in one shared frontend constants file, not duplicated.

Existing categories (already in use, unchanged): Technology, Business,
World, Science, Sports.

## Backend API changes

`GET /posts` gains two optional query parameters, both filtering
server-side:
- `?category=Technology` — exact match on `category`.
- `?countries=France,Germany` — comma-separated list; matches posts whose
  `country` is any of the listed values.

Both params are optional and combine with AND logic when both are
present. Omitting both returns all posts (current behavior, unchanged).
No other endpoints change. `PostCreate`/`PostUpdate`/`PostOut` schemas
gain the required `country: str` field alongside the existing fields.

## Frontend changes

**New shared constant:** `frontend/src/constants.js` exporting
`CATEGORIES` (the 5 existing category strings) and `COUNTRIES` (the 12
country strings above) — single source of truth for both the filter UI
and the post form's dropdowns.

**New component: `CategoryTabs`** — a single-select horizontal tab bar
(All + the 5 categories) rendered above the post grid on the Home page.
Clicking a tab sets the active category and re-fetches `listPosts` with
the `category` query param (or omits it for "All").

**New component: `CountryFilter`** — a checklist of the 12 countries
(all unchecked by default = no country filter applied) rendered
alongside `CategoryTabs` on the Home page. Checking any countries
re-fetches `listPosts` with the `countries` query param (comma-joined);
unchecking all countries removes the filter.

**`Home.jsx`** — owns the active category + selected countries as state,
passes them to `CategoryTabs`/`CountryFilter`, and re-fetches whenever
either changes (via a `useEffect` dependency on both).

**`api/posts.js`** — `listPosts` gains an optional params object:
`listPosts({ category, countries })`, building the query string only for
params that are actually set.

**`PostCard`/`PostDetail`** — both already show a category pill; add a
second badge for `country` right next to it, same visual treatment
(reuse the existing pill styling, not a new component).

**`PostForm`** — the free-text `category` and `author`-adjacent inputs
gain a `country` field. Both `category` and the new `country` field
become `<select>` dropdowns populated from `CATEGORIES`/`COUNTRIES`
(replacing category's current free-text input) rather than free text —
this keeps filtering reliable (no typos causing a post to silently not
match any filter).

## Error handling

Unchanged from the existing app — a failed fetch (e.g. bad query
params, though none are validated beyond FastAPI's normal type checking)
surfaces the existing error-message pattern already used throughout.

## Testing

Manual verification, consistent with the rest of this project (no
automated test suite): curl the new query-param combinations against the
backend directly, then browser-verify category tab switching, country
checkbox filtering, and combined filtering, plus creating a post via the
new dropdowns.

## Out of scope (this phase)

Images (Phase 2). Visual redesign/animations (Phase 3). Multi-country
posts (rejected during brainstorming — one country per post). Country
tabs as single-select (rejected — country is multi-select checklist,
category is the single-select tab bar). Any continent other than Europe
(future data addition, not a schema change).
