# Phase 5: Heavy Design, Denser Posts, Podcasts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the site's design heavier and more animated (same colors), add more information to the bottom of every post, grow the seeded news volume from 12 to 40 posts, and add a full backend-CRUD "Podcasts" section with its own frontend folder.

**Architecture:** Backend gains a second resource (`Podcast`) following the exact CRUD shape already established by `Post`. Frontend gains a self-contained `frontend/src/podcasts/` feature folder, a shared `postMeta.js` utility for client-computed post metadata (no new DB columns), an always-mounted decorative `Backdrop` component, and a site-wide `Footer`.

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite (backend); React 19, React Router v7, plain CSS (frontend). No new dependencies.

**Spec:** `docs/superpowers/specs/2026-09-29-phase5-heavy-design-podcasts-design.md`

## Global Constraints

- Same color tokens only (`--bg`, `--bg-elevated`, `--border`, `--text`, `--text-dim`, `--accent`, `--accent-dim`) — no new colors.
- No new `Post` database columns — all new per-post info (tags, read time, stats) is computed client-side from existing fields, to avoid repeating the manual `ALTER TABLE` dev-DB pain from Phase 2.
- No new npm or pip dependencies.
- Every new decorative/animated element must freeze under `prefers-reduced-motion: reduce`.
- Seeded podcast `external_url` values must be real, honest platform homepages (youtube.com, open.spotify.com, podcasts.apple.com, soundcloud.com) — never a fabricated specific video/episode URL.
- Follow the existing per-file API pattern: each `api/*.js` file duplicates its own `handleResponse` rather than importing a shared helper (matches `api/posts.js` vs `api/uploads.js` today).
- All commits use `git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit ...`.
- Verify backend freshness via `GET /openapi.json` (check the new paths appear) rather than trusting a bare `GET /` 200, per this project's established convention.

---

### Task 1: Backend — Podcast model, schema, CRUD router

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Create: `backend/app/routers/podcasts.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Produces: `models.Podcast` (id, title, host, description, cover_image_url, source, external_url, created_at); `schemas.PodcastCreate/Update/Out`; `GET/POST /podcasts`, `GET/PUT/DELETE /podcasts/{id}`.
- Consumes: nothing new (mirrors the existing `Post`/`posts.py` pattern in this codebase).

- [ ] **Step 1: Add the `Podcast` model**

Append to `backend/app/models.py` (after the existing `Post` class):

```python
class Podcast(Base):
    __tablename__ = "podcasts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    host: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(50))
    external_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

No new imports needed — `String`, `Text`, `DateTime`, `func`, `Mapped`, `mapped_column`, `datetime` are already imported at the top of this file for `Post`.

- [ ] **Step 2: Add Podcast schemas**

Append to `backend/app/schemas.py`:

```python
class PodcastBase(BaseModel):
    title: str
    host: str
    description: str
    cover_image_url: str | None = None
    source: str
    external_url: str


class PodcastCreate(PodcastBase):
    pass


class PodcastUpdate(PodcastBase):
    pass


class PodcastOut(PodcastBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 3: Create the podcasts router**

Create `backend/app/routers/podcasts.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


@router.get("", response_model=list[schemas.PodcastOut])
def list_podcasts(db: Session = Depends(get_db)):
    return db.query(models.Podcast).order_by(models.Podcast.created_at.desc()).all()


@router.get("/{podcast_id}", response_model=schemas.PodcastOut)
def get_podcast(podcast_id: int, db: Session = Depends(get_db)):
    podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if podcast is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")
    return podcast


@router.post("", response_model=schemas.PodcastOut, status_code=status.HTTP_201_CREATED)
def create_podcast(podcast: schemas.PodcastCreate, db: Session = Depends(get_db)):
    db_podcast = models.Podcast(**podcast.model_dump())
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast


@router.put("/{podcast_id}", response_model=schemas.PodcastOut)
def update_podcast(podcast_id: int, podcast: schemas.PodcastUpdate, db: Session = Depends(get_db)):
    db_podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if db_podcast is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")
    for field, value in podcast.model_dump().items():
        setattr(db_podcast, field, value)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast


@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_podcast(podcast_id: int, db: Session = Depends(get_db)):
    db_podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if db_podcast is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")
    db.delete(db_podcast)
    db.commit()
    return None
```

- [ ] **Step 4: Wire the router into the app**

In `backend/app/main.py`, change:

```python
from .routers import posts, uploads
```

to:

```python
from .routers import posts, podcasts, uploads
```

and change:

```python
app.include_router(posts.router)
```

to:

```python
app.include_router(posts.router)
app.include_router(podcasts.router)
```

(Leave the uploads/StaticFiles ordering and its comment untouched — `podcasts.router` has no path overlap with `/uploads`, so it can be included anywhere relative to that pair.)

- [ ] **Step 5: Verify**

Restart the backend (kill any stale process on port 8000 first — this project has repeatedly hit stale dev-server processes; confirm with `GET http://localhost:8000/openapi.json` that a `/podcasts` path now appears before trusting anything else). Then:

```bash
curl -s -X POST http://localhost:8000/podcasts -H "Content-Type: application/json" -d "{\"title\":\"Test Show\",\"host\":\"Test Host\",\"description\":\"desc\",\"cover_image_url\":null,\"source\":\"YouTube\",\"external_url\":\"https://www.youtube.com\"}"
curl -s http://localhost:8000/podcasts
curl -s http://localhost:8000/podcasts/1
curl -s -X PUT http://localhost:8000/podcasts/1 -H "Content-Type: application/json" -d "{\"title\":\"Updated Show\",\"host\":\"Test Host\",\"description\":\"desc\",\"cover_image_url\":null,\"source\":\"YouTube\",\"external_url\":\"https://www.youtube.com\"}"
curl -s -X DELETE http://localhost:8000/podcasts/1 -o /dev/null -w "%{http_code}\n"
curl -s http://localhost:8000/podcasts/1 -o /dev/null -w "%{http_code}\n"
```

Expected: POST returns 201 with the created object; GET list includes it; GET by id returns it; PUT returns the updated object; DELETE returns 204; the final GET returns 404.

- [ ] **Step 6: Commit**

```bash
git add backend/app/models.py backend/app/schemas.py backend/app/routers/podcasts.py backend/app/main.py
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add Podcast model and CRUD router"
```

---

### Task 2: Backend — expand seed data (40 posts, 10 podcasts)

**Files:**
- Modify: `backend/seed.py`

**Interfaces:**
- Consumes: `models.Post`, `models.Podcast` (Task 1).
- Produces: an idempotently-seeded dev DB with 40 posts and 10 podcasts.

- [ ] **Step 1: Append 28 new posts to `SAMPLE_POSTS`**

In `backend/seed.py`, insert the following 28 dicts into the `SAMPLE_POSTS` list, immediately after the existing 12th entry (Switzerland/Lukas Meier) and before the closing `]`:

```python
    {
        "title": "British AI Startup Unveils Chip Designed for On-Device Language Models",
        "content": (
            "A London-based chip startup unveiled a processor purpose-built for "
            "running language models directly on phones and laptops, cutting "
            "reliance on cloud servers.\n\n"
            "The company says early partners have reported meaningfully lower "
            "latency in on-device assistants, though independent benchmarks "
            "have yet to confirm the claimed efficiency gains."
        ),
        "author": "Oliver Hastings",
        "category": "Technology",
        "country": "United Kingdom",
        "image_url": "https://picsum.photos/seed/newsblog-13/800/450",
    },
    {
        "title": "UK and Nordic Allies Deepen Joint Air-Defense Patrols Over the North Sea",
        "content": (
            "The United Kingdom and its Nordic allies announced expanded joint "
            "air-defense patrols over the North Sea, citing a rise in "
            "unidentified aircraft near shared waters.\n\n"
            "Defense officials described the move as routine coordination "
            "rather than an escalation, though neighboring states have "
            "requested further briefings."
        ),
        "author": "Priya Anand",
        "category": "World",
        "country": "United Kingdom",
        "image_url": "https://picsum.photos/seed/newsblog-14/800/450",
    },
    {
        "title": "High Street Retailers Report Cautious Holiday Spending Forecasts",
        "content": (
            "Major British retailers issued cautious forecasts for holiday "
            "spending, pointing to squeezed household budgets despite easing "
            "inflation.\n\n"
            "Several chains said they were leaning on earlier discounting to "
            "protect footfall, a strategy some analysts warn could pressure "
            "margins heading into the new year."
        ),
        "author": "Daniel Cross",
        "category": "Business",
        "country": "United Kingdom",
        "image_url": "https://picsum.photos/seed/newsblog-15/800/450",
    },
    {
        "title": "German Physicists Report Progress on Room-Temperature Superconductor Trials",
        "content": (
            "German physicists reported incremental progress toward a "
            "room-temperature superconductor, achieving stable conductivity "
            "at slightly higher temperatures than previous trials.\n\n"
            "The team cautioned that reproducing the results at scale remains "
            "an open challenge, and called for independent replication before "
            "drawing broader conclusions."
        ),
        "author": "Jonas Richter",
        "category": "Science",
        "country": "Germany",
        "image_url": "https://picsum.photos/seed/newsblog-16/800/450",
    },
    {
        "title": "Bundesliga Clubs Trial New Concussion Protocol After Player Injuries",
        "content": (
            "Several Bundesliga clubs began trialing a revised concussion "
            "protocol following a string of head injuries earlier this "
            "season.\n\n"
            "The new procedure adds a mandatory sideline evaluation window, a "
            "change player unions have pushed for despite some coaches' "
            "concerns about disrupting match flow."
        ),
        "author": "Anke Weber",
        "category": "Sports",
        "country": "Germany",
        "image_url": "https://picsum.photos/seed/newsblog-17/800/450",
    },
    {
        "title": "Munich Robotics Lab Opens Public Testbed for Warehouse Automation",
        "content": (
            "A Munich robotics lab opened a public testbed allowing local "
            "logistics firms to trial warehouse automation systems before "
            "committing to full deployment.\n\n"
            "Organizers say the facility is meant to lower the barrier for "
            "mid-sized companies wary of the upfront cost of automation."
        ),
        "author": "Felix Braun",
        "category": "Technology",
        "country": "Germany",
        "image_url": "https://picsum.photos/seed/newsblog-18/800/450",
    },
    {
        "title": "French Cycling Federation Proposes Reforms to Grand Tour Scheduling",
        "content": (
            "France's cycling federation proposed reforms to the Grand Tour "
            "calendar aimed at reducing back-to-back stage demands on "
            "riders.\n\n"
            "Team managers have broadly welcomed the plan, though some race "
            "organizers worry it could shorten marquee events."
        ),
        "author": "Camille Laurent",
        "category": "Sports",
        "country": "France",
        "image_url": "https://picsum.photos/seed/newsblog-19/800/450",
    },
    {
        "title": "French Oceanographers Map Deep-Sea Coral Reefs Off Brittany Coast",
        "content": (
            "French oceanographers completed a detailed survey of deep-sea "
            "coral reefs off the Brittany coast, identifying several "
            "previously undocumented colonies.\n\n"
            "Researchers say the findings will inform new proposals for "
            "protected marine zones in the area."
        ),
        "author": "Antoine Rousseau",
        "category": "Science",
        "country": "France",
        "image_url": "https://picsum.photos/seed/newsblog-20/800/450",
    },
    {
        "title": "Paris Startup Hub Reports Surge in Climate-Tech Applications",
        "content": (
            "A Paris startup hub reported a sharp rise in applications from "
            "climate-technology founders this cycle, outpacing every other "
            "sector it tracks.\n\n"
            "Organizers attributed the surge to new public funding programs "
            "aimed at accelerating emissions-reduction ventures."
        ),
        "author": "Élise Fontaine",
        "category": "Technology",
        "country": "France",
        "image_url": "https://picsum.photos/seed/newsblog-21/800/450",
    },
    {
        "title": "Ukrainian Grain Exporters Adjust Routes Amid Black Sea Shipping Risks",
        "content": (
            "Ukrainian grain exporters said they were adjusting shipping "
            "routes in response to renewed risks along Black Sea corridors, "
            "favoring longer but more secure paths.\n\n"
            "Industry groups warned the added costs could weigh on already "
            "thin margins through the coming season."
        ),
        "author": "Andriy Kovalenko",
        "category": "Business",
        "country": "Ukraine",
        "image_url": "https://picsum.photos/seed/newsblog-22/800/450",
    },
    {
        "title": "Kyiv Software Firms See Rising Demand for Cybersecurity Contracts Abroad",
        "content": (
            "Software firms based in Kyiv reported rising demand for "
            "cybersecurity contracts from clients abroad, as international "
            "companies seek experienced teams accustomed to operating under "
            "strained conditions.\n\n"
            "Founders say the sector has become an unexpected bright spot for "
            "the country's tech exports."
        ),
        "author": "Iryna Shevchenko",
        "category": "Technology",
        "country": "Ukraine",
        "image_url": "https://picsum.photos/seed/newsblog-23/800/450",
    },
    {
        "title": "Ukrainian Researchers Study Soil Recovery in War-Affected Farmland",
        "content": (
            "Researchers began a multi-year study of soil recovery in "
            "farmland affected by the ongoing conflict, tracking "
            "contamination and long-term fertility.\n\n"
            "Early results suggest recovery timelines vary widely by region, "
            "complicating replanting plans for returning farmers."
        ),
        "author": "Pavlo Marchenko",
        "category": "Science",
        "country": "Ukraine",
        "image_url": "https://picsum.photos/seed/newsblog-24/800/450",
    },
    {
        "title": "Italian Fashion Houses Report Resilient Demand From Asian Markets",
        "content": (
            "Italian fashion houses reported resilient demand from Asian "
            "markets despite a broader slowdown in luxury spending "
            "elsewhere.\n\n"
            "Executives credited targeted regional marketing and a steady "
            "flow of new store openings for the sector's relative strength."
        ),
        "author": "Marco Bianchi",
        "category": "Business",
        "country": "Italy",
        "image_url": "https://picsum.photos/seed/newsblog-25/800/450",
    },
    {
        "title": "Rome Summit Addresses Mediterranean Fishing Quota Disputes",
        "content": (
            "A summit in Rome brought together Mediterranean nations to "
            "address long-running disputes over shared fishing quotas.\n\n"
            "Delegates agreed to a temporary framework for monitoring catch "
            "data, though a permanent quota system remains under "
            "negotiation."
        ),
        "author": "Sofia Conti",
        "category": "World",
        "country": "Italy",
        "image_url": "https://picsum.photos/seed/newsblog-26/800/450",
    },
    {
        "title": "Barcelona Tech Cluster Attracts New Wave of Remote-Work Relocators",
        "content": (
            "Barcelona's tech cluster continued to attract remote workers "
            "relocating from higher-cost cities, according to new residency "
            "data.\n\n"
            "Local officials say the influx has boosted demand for "
            "co-working spaces but also strained housing availability in "
            "central neighborhoods."
        ),
        "author": "Lucía Navarro",
        "category": "Technology",
        "country": "Spain",
        "image_url": "https://picsum.photos/seed/newsblog-27/800/450",
    },
    {
        "title": "Spain Expands Diplomatic Outreach to Latin American Trade Partners",
        "content": (
            "Spain announced expanded diplomatic outreach to Latin American "
            "trade partners, framing the effort as part of a broader push to "
            "diversify export markets.\n\n"
            "Officials pointed to shared language and cultural ties as a "
            "natural advantage over competing European exporters."
        ),
        "author": "Diego Serrano",
        "category": "World",
        "country": "Spain",
        "image_url": "https://picsum.photos/seed/newsblog-28/800/450",
    },
    {
        "title": "Dutch Startup Develops Sensor Network for Urban Flood Warnings",
        "content": (
            "A Dutch startup unveiled a sensor network designed to give "
            "cities earlier warning of urban flooding, building on lessons "
            "from recent storm seasons.\n\n"
            "Municipal partners say pilot deployments will begin in "
            "low-lying districts before a wider rollout."
        ),
        "author": "Bram Jansen",
        "category": "Technology",
        "country": "Netherlands",
        "image_url": "https://picsum.photos/seed/newsblog-29/800/450",
    },
    {
        "title": "Amsterdam Researchers Publish Findings on North Sea Wind Farm Ecology",
        "content": (
            "Researchers in Amsterdam published new findings on how offshore "
            "wind farms in the North Sea are affecting local marine "
            "ecosystems.\n\n"
            "The study found mixed effects, with some fish populations "
            "increasing near turbine bases while others shifted migration "
            "patterns."
        ),
        "author": "Lotte Visser",
        "category": "Science",
        "country": "Netherlands",
        "image_url": "https://picsum.photos/seed/newsblog-30/800/450",
    },
    {
        "title": "Polish Volleyball Federation Reports Record Youth League Enrollment",
        "content": (
            "Poland's volleyball federation reported record enrollment in "
            "its youth leagues this season, crediting a surge in interest "
            "following recent national team successes.\n\n"
            "Officials say new regional training centers are being planned "
            "to keep pace with demand."
        ),
        "author": "Agnieszka Nowak",
        "category": "Sports",
        "country": "Poland",
        "image_url": "https://picsum.photos/seed/newsblog-31/800/450",
    },
    {
        "title": "Warsaw Institute Advances Battery Recycling Technique",
        "content": (
            "A Warsaw research institute announced progress on a battery "
            "recycling technique that recovers a higher share of lithium "
            "than current industrial methods.\n\n"
            "The team said commercial partners have expressed interest, "
            "though scaling the process remains a hurdle."
        ),
        "author": "Piotr Zieliński",
        "category": "Science",
        "country": "Poland",
        "image_url": "https://picsum.photos/seed/newsblog-32/800/450",
    },
    {
        "title": "Sweden Hosts Regional Talks on Arctic Shipping Regulation",
        "content": (
            "Sweden hosted regional talks on Arctic shipping regulation as "
            "melting sea ice opens new northern trade routes.\n\n"
            "Participating nations discussed shared environmental standards, "
            "though disagreements over enforcement authority left key "
            "questions unresolved."
        ),
        "author": "Oskar Lindqvist",
        "category": "World",
        "country": "Sweden",
        "image_url": "https://picsum.photos/seed/newsblog-33/800/450",
    },
    {
        "title": "Swedish Ice Hockey League Expands With Two New Franchises",
        "content": (
            "Sweden's top ice hockey league confirmed plans to add two new "
            "franchises, expanding the competition for the first time in "
            "over a decade.\n\n"
            "League officials cited strong regional fan interest and new "
            "arena investment as deciding factors."
        ),
        "author": "Freja Sandberg",
        "category": "Sports",
        "country": "Sweden",
        "image_url": "https://picsum.photos/seed/newsblog-34/800/450",
    },
    {
        "title": "Greek Shipping Firms Modernize Fleets Amid New Emissions Rules",
        "content": (
            "Greek shipping firms began modernizing portions of their fleets "
            "ahead of stricter international emissions rules taking effect "
            "in coming years.\n\n"
            "Industry groups said the transition costs would be substantial "
            "but necessary to retain competitiveness in global freight "
            "markets."
        ),
        "author": "Nikos Papadopoulos",
        "category": "Business",
        "country": "Greece",
        "image_url": "https://picsum.photos/seed/newsblog-35/800/450",
    },
    {
        "title": "Athens Tech Incubator Backs Wave of Tourism-Tech Startups",
        "content": (
            "An Athens technology incubator backed a new wave of startups "
            "focused on modernizing the country's tourism sector, from "
            "booking platforms to sustainability tracking tools.\n\n"
            "Organizers say the cohort reflects growing investor interest in "
            "travel-adjacent technology."
        ),
        "author": "Eleni Georgiou",
        "category": "Technology",
        "country": "Greece",
        "image_url": "https://picsum.photos/seed/newsblog-36/800/450",
    },
    {
        "title": "Portugal Deepens Trade Ties With Lusophone African Nations",
        "content": (
            "Portugal announced deepened trade ties with several Lusophone "
            "African nations, framing the agreements as part of a long-term "
            "strategy to strengthen historic ties.\n\n"
            "Officials said the deals would expand market access for both "
            "agricultural exports and services."
        ),
        "author": "Ines Carvalho",
        "category": "World",
        "country": "Portugal",
        "image_url": "https://picsum.photos/seed/newsblog-37/800/450",
    },
    {
        "title": "Lisbon Startup Scene Draws Record Foreign Investment This Year",
        "content": (
            "Lisbon's startup scene drew record foreign investment this "
            "year, according to new figures from the national trade "
            "agency.\n\n"
            "Founders point to competitive operating costs and "
            "English-speaking talent as key draws for international "
            "investors."
        ),
        "author": "Miguel Santos",
        "category": "Business",
        "country": "Portugal",
        "image_url": "https://picsum.photos/seed/newsblog-38/800/450",
    },
    {
        "title": "Swiss Research Consortium Advances Precision Medicine Trials",
        "content": (
            "A Swiss research consortium reported advances in precision "
            "medicine trials targeting rare genetic conditions, with early "
            "results showing promising patient response rates.\n\n"
            "Researchers cautioned that regulatory approval would likely "
            "take several more years of study."
        ),
        "author": "Nadia Frei",
        "category": "Science",
        "country": "Switzerland",
        "image_url": "https://picsum.photos/seed/newsblog-39/800/450",
    },
    {
        "title": "Geneva Hosts Renewed Talks on Cross-Border Data Privacy Standards",
        "content": (
            "Geneva hosted renewed international talks on cross-border data "
            "privacy standards, as governments seek common ground amid "
            "diverging national regulations.\n\n"
            "Negotiators described the discussions as constructive but "
            "acknowledged a binding agreement remains distant."
        ),
        "author": "Thomas Roth",
        "category": "World",
        "country": "Switzerland",
        "image_url": "https://picsum.photos/seed/newsblog-40/800/450",
    },
```

Confirm `SAMPLE_POSTS` now has exactly 40 entries after this edit.

- [ ] **Step 2: Add `SAMPLE_PODCASTS`**

Add this new list to `backend/seed.py`, directly after the `SAMPLE_POSTS = [...]` list closes:

```python
SAMPLE_PODCASTS = [
    {
        "title": "The Current Brief",
        "host": "Daily Current Newsroom",
        "description": (
            "A fast-paced daily rundown of the headlines shaping Europe, "
            "delivered in under fifteen minutes."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-1/500/500",
        "source": "YouTube",
        "external_url": "https://www.youtube.com",
    },
    {
        "title": "Deep Markets",
        "host": "Elena Vasquez",
        "description": (
            "Weekly deep dives into the economic stories behind the "
            "business headlines, from trade routes to central bank policy."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-2/500/500",
        "source": "Spotify",
        "external_url": "https://open.spotify.com",
    },
    {
        "title": "World in Focus",
        "host": "Tariq Hassan",
        "description": (
            "A weekly look at the diplomatic and geopolitical stories "
            "moving between capitals, with context beyond the wire copy."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-3/500/500",
        "source": "Apple Podcasts",
        "external_url": "https://podcasts.apple.com",
    },
    {
        "title": "Field Notes: Science Weekly",
        "host": "Dr. Priya Nair",
        "description": (
            "Researchers and journalists unpack the science stories of the "
            "week, from lab results to what they actually mean."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-4/500/500",
        "source": "SoundCloud",
        "external_url": "https://soundcloud.com",
    },
    {
        "title": "Fulltime Whistle",
        "host": "Marco Silva",
        "description": (
            "A lively roundup of the week in European sport, from transfer "
            "rumors to match analysis."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-5/500/500",
        "source": "YouTube",
        "external_url": "https://www.youtube.com",
    },
    {
        "title": "Startup Signal",
        "host": "Jonas Kessler",
        "description": (
            "Conversations with founders and investors building the next "
            "wave of European tech companies."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-6/500/500",
        "source": "Spotify",
        "external_url": "https://open.spotify.com",
    },
    {
        "title": "Borders & Ballots",
        "host": "Camille Novak",
        "description": (
            "Analysis of elections, coalitions, and policy fights shaping "
            "politics across the continent."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-7/500/500",
        "source": "Apple Podcasts",
        "external_url": "https://podcasts.apple.com",
    },
    {
        "title": "The Long Read",
        "host": "Helena Brandt",
        "description": (
            "Long-form storytelling and narrative journalism on the people "
            "and places behind the news."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-8/500/500",
        "source": "YouTube",
        "external_url": "https://www.youtube.com",
    },
    {
        "title": "Climate Desk",
        "host": "Ravi Chandran",
        "description": (
            "Reporting on the policies, technologies, and disasters shaping "
            "the climate conversation in Europe."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-9/500/500",
        "source": "SoundCloud",
        "external_url": "https://soundcloud.com",
    },
    {
        "title": "After Hours",
        "host": "The Daily Current Staff",
        "description": (
            "An informal weekly chat from The Daily Current's own newsroom "
            "on the stories they couldn't fit in print."
        ),
        "cover_image_url": "https://picsum.photos/seed/newsblog-podcast-10/500/500",
        "source": "Spotify",
        "external_url": "https://open.spotify.com",
    },
]
```

- [ ] **Step 3: Seed podcasts independently of posts**

Replace the existing `seed()` function in `backend/seed.py`:

```python
def seed():
    db = SessionLocal()
    try:
        if db.query(models.Post).count() > 0:
            print("Posts already exist, skipping seed.")
            return
        for data in SAMPLE_POSTS:
            db.add(models.Post(**data))
        db.commit()
        print(f"Seeded {len(SAMPLE_POSTS)} posts.")
    finally:
        db.close()
```

with:

```python
def seed():
    db = SessionLocal()
    try:
        if db.query(models.Post).count() == 0:
            for data in SAMPLE_POSTS:
                db.add(models.Post(**data))
            db.commit()
            print(f"Seeded {len(SAMPLE_POSTS)} posts.")
        else:
            print("Posts already exist, skipping post seed.")

        if db.query(models.Podcast).count() == 0:
            for data in SAMPLE_PODCASTS:
                db.add(models.Podcast(**data))
            db.commit()
            print(f"Seeded {len(SAMPLE_PODCASTS)} podcasts.")
        else:
            print("Podcasts already exist, skipping podcast seed.")
    finally:
        db.close()
```

- [ ] **Step 4: Verify**

The dev DB already has 12 posts seeded from earlier phases, and `seed()` only seeds an empty table, so re-running it as-is won't add the new 28. This project doesn't use migrations (confirmed in Phase 2) — delete the gitignored dev DB file so `create_all()` + `seed()` rebuild it from scratch with all 40 posts and 10 podcasts:

```bash
# from backend/, with the backend server stopped
rm -f news_blog.db  # or whatever the actual sqlite filename is — check backend/app/database.py if unsure
python seed.py
```

Restart the backend, then:

```bash
curl -s http://localhost:8000/posts | python -c "import sys,json; print(len(json.load(sys.stdin)))"
curl -s http://localhost:8000/podcasts | python -c "import sys,json; print(len(json.load(sys.stdin)))"
```

Expected: `40` and `10`.

- [ ] **Step 5: Commit**

```bash
git add backend/seed.py
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Expand seed data to 40 posts and 10 podcasts"
```

(Do not commit the local `.db` file — it's gitignored and disposable.)

---

### Task 3: Frontend — podcasts data layer and shared form

**Files:**
- Create: `frontend/src/api/podcasts.js`
- Modify: `frontend/src/constants.js`
- Create: `frontend/src/podcasts/PodcastForm.jsx`
- Create: `frontend/src/podcasts/PodcastForm.css`

**Interfaces:**
- Consumes: `API_URL` from `frontend/src/api/posts.js`; `resolveImageUrl` from the same file.
- Produces: `listPodcasts/getPodcast/createPodcast/updatePodcast/deletePodcast` (used by Task 4); `PODCAST_SOURCES`, `PODCAST_SOURCE_ICONS` (used by Task 4); `<PodcastForm initialValues? onSubmit submitLabel? />` (used by Task 4's New/Edit pages).

- [ ] **Step 1: Create the podcasts API client**

Create `frontend/src/api/podcasts.js`:

```js
import { API_URL } from './posts'

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      const d = data.detail
      detail = Array.isArray(d) ? d.map((e) => e.msg).join(', ') : d || detail
    } catch {
      // response had no JSON body
    }
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

export function listPodcasts() {
  return fetch(`${API_URL}/podcasts`).then(handleResponse)
}

export function getPodcast(id) {
  return fetch(`${API_URL}/podcasts/${id}`).then(handleResponse)
}

export function createPodcast(podcast) {
  return fetch(`${API_URL}/podcasts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(podcast),
  }).then(handleResponse)
}

export function updatePodcast(id, podcast) {
  return fetch(`${API_URL}/podcasts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(podcast),
  }).then(handleResponse)
}

export function deletePodcast(id) {
  return fetch(`${API_URL}/podcasts/${id}`, { method: 'DELETE' }).then(handleResponse)
}
```

- [ ] **Step 2: Add podcast constants**

Append to `frontend/src/constants.js`:

```js
export const PODCAST_SOURCES = ['YouTube', 'Spotify', 'Apple Podcasts', 'SoundCloud', 'Other']

export const PODCAST_SOURCE_ICONS = {
  YouTube: '▶️',
  Spotify: '🎧',
  'Apple Podcasts': '🎙️',
  SoundCloud: '☁️',
  Other: '🔗',
}
```

- [ ] **Step 3: Create the podcasts folder and the shared form**

Create `frontend/src/podcasts/PodcastForm.jsx`:

```jsx
import { useState } from 'react'
import { PODCAST_SOURCES } from '../constants'
import { resolveImageUrl } from '../api/posts'
import './PodcastForm.css'

const EMPTY = {
  title: '',
  host: '',
  description: '',
  cover_image_url: '',
  source: '',
  external_url: '',
}

export default function PodcastForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Add Podcast' }) {
  const [values, setValues] = useState(initialValues)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  function update(field) {
    return (e) => setValues((v) => ({ ...v, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await onSubmit({ ...values, cover_image_url: values.cover_image_url || null })
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  const preview = resolveImageUrl(values.cover_image_url)

  return (
    <form className="podcast-form" onSubmit={handleSubmit}>
      <label>
        Title
        <input value={values.title} onChange={update('title')} required />
      </label>
      <div className="podcast-form-row">
        <label>
          Host
          <input value={values.host} onChange={update('host')} required />
        </label>
        <label>
          Source
          <select value={values.source} onChange={update('source')} required>
            <option value="" disabled>
              Select a source
            </option>
            {PODCAST_SOURCES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        Description
        <textarea value={values.description} onChange={update('description')} required />
      </label>
      <label>
        Cover image URL (optional)
        <input
          type="url"
          value={values.cover_image_url ?? ''}
          onChange={update('cover_image_url')}
          placeholder="https://..."
        />
      </label>
      {preview && <img src={preview} alt="" className="podcast-form-image-preview" />}
      <label>
        External link
        <input type="url" value={values.external_url} onChange={update('external_url')} required />
      </label>
      <div className="podcast-form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        {error && <span className="state-message error">{error}</span>}
      </div>
    </form>
  )
}
```

Create `frontend/src/podcasts/PodcastForm.css`:

```css
.podcast-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 640px;
}

.podcast-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.podcast-form textarea {
  min-height: 140px;
  resize: vertical;
  font-family: var(--font-body);
}

.podcast-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.podcast-form-row label {
  flex: 1 1 160px;
}

.podcast-form-image-preview {
  width: 96px;
  height: 96px;
  object-fit: cover;
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.podcast-form-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-1);
}
```

- [ ] **Step 4: Verify**

This task has no reachable UI yet (no route mounts `PodcastForm`) — verify with a build/lint check instead:

```bash
cd frontend
npm run build
```

Expected: build succeeds with no errors referencing `podcasts.js`, `constants.js`, or `PodcastForm.jsx`.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/podcasts.js frontend/src/constants.js frontend/src/podcasts/PodcastForm.jsx frontend/src/podcasts/PodcastForm.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add podcasts API client, constants, and shared form"
```

---

### Task 4: Frontend — podcasts pages, routes, nav link

**Files:**
- Create: `frontend/src/podcasts/PodcastCard.jsx`
- Create: `frontend/src/podcasts/PodcastCard.css`
- Create: `frontend/src/podcasts/PodcastsPage.jsx`
- Create: `frontend/src/podcasts/PodcastsPage.css`
- Create: `frontend/src/podcasts/NewPodcast.jsx`
- Create: `frontend/src/podcasts/EditPodcast.jsx`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/components/Navbar.jsx`
- Modify: `frontend/src/components/Navbar.css`

**Interfaces:**
- Consumes: `listPodcasts/getPodcast/createPodcast/updatePodcast/deletePodcast` and `PodcastForm` (Task 3); `resolveImageUrl` (existing); `PODCAST_SOURCE_ICONS` (Task 3).
- Produces: routes `/podcasts`, `/podcasts/new`, `/podcasts/:id/edit`; a "Podcasts" nav link.

- [ ] **Step 1: Create `PodcastCard`**

Create `frontend/src/podcasts/PodcastCard.jsx`:

```jsx
import { Link } from 'react-router-dom'
import { resolveImageUrl } from '../api/posts'
import { PODCAST_SOURCE_ICONS } from '../constants'
import './PodcastCard.css'

function excerpt(text, length = 120) {
  const flat = text.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PodcastCard({ podcast, onDelete }) {
  const cover = resolveImageUrl(podcast.cover_image_url)

  function handleDelete() {
    if (!window.confirm('Delete this podcast? This cannot be undone.')) return
    onDelete(podcast.id)
  }

  return (
    <div className="podcast-card">
      {cover && <img src={cover} alt="" className="podcast-card-image" />}
      <span className="podcast-source-badge">
        {PODCAST_SOURCE_ICONS[podcast.source] ?? '🔗'} {podcast.source}
      </span>
      <h2>{podcast.title}</h2>
      <p className="podcast-card-host">{podcast.host}</p>
      <p className="podcast-card-description">{excerpt(podcast.description)}</p>
      <div className="podcast-card-actions">
        <a
          href={podcast.external_url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          Listen on {podcast.source}
        </a>
        <Link to={`/podcasts/${podcast.id}/edit`} className="btn">
          Edit
        </Link>
        <button className="btn btn-danger" onClick={handleDelete} type="button">
          Delete
        </button>
      </div>
    </div>
  )
}
```

Create `frontend/src/podcasts/PodcastCard.css`:

```css
.podcast-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  position: relative;
  overflow: hidden;
  transition: border-color 0.15s ease, translate 0.15s ease;
}

.podcast-card:hover {
  border-color: var(--accent);
  translate: 0 -2px;
  box-shadow: 0 0 0 1px var(--accent), 0 12px 24px -8px var(--accent-dim);
}

.podcast-card-image {
  display: block;
  width: calc(100% + var(--space-3) * 2);
  margin: calc(var(--space-3) * -1) calc(var(--space-3) * -1) var(--space-2);
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: var(--radius) var(--radius) 0 0;
  transition: transform var(--dur-base) var(--ease-out);
}

.podcast-card:hover .podcast-card-image {
  transform: scale(1.05);
}

.podcast-source-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  align-self: flex-start;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 3px 10px;
  border-radius: 999px;
}

.podcast-card h2 {
  font-size: 1.25rem;
  margin: var(--space-1) 0 0;
}

.podcast-card-host {
  font-size: 0.85rem;
  color: var(--text-dim);
  font-weight: 500;
  margin-bottom: 0;
}

.podcast-card-description {
  color: var(--text-dim);
  margin-bottom: 0;
}

.podcast-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-top: var(--space-1);
}
```

- [ ] **Step 2: Create `PodcastsPage`**

Create `frontend/src/podcasts/PodcastsPage.jsx`:

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPodcasts, deletePodcast } from '../api/podcasts'
import PodcastCard from './PodcastCard'
import './PodcastsPage.css'

export default function PodcastsPage() {
  const [podcasts, setPodcasts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    setStatus('loading')
    listPodcasts()
      .then((data) => {
        if (!ignore) {
          setPodcasts(data)
          setStatus('ready')
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message)
          setStatus('error')
        }
      })
    return () => {
      ignore = true
    }
  }, [])

  async function handleDelete(id) {
    try {
      await deletePodcast(id)
      setPodcasts((current) => current.filter((p) => p.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page container">
      <header className="podcasts-header">
        <div>
          <h1>Listen</h1>
          <p>Podcasts and shows from The DailyCurrent and other networks, all in one place.</p>
        </div>
        <Link to="/podcasts/new" className="btn btn-primary">
          Add Podcast
        </Link>
      </header>

      {status === 'loading' && (
        <div className="podcast-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="podcast-skeleton-card" />
          ))}
        </div>
      )}
      {status === 'error' && <p className="state-message error">Couldn't load podcasts: {error}</p>}
      {status === 'ready' && podcasts.length === 0 && (
        <p className="state-message">No podcasts yet — add the first one.</p>
      )}
      {status === 'ready' && podcasts.length > 0 && (
        <div className="podcast-grid">
          {podcasts.map((podcast) => (
            <PodcastCard key={podcast.id} podcast={podcast} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
```

Create `frontend/src/podcasts/PodcastsPage.css`:

```css
.podcasts-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-2);
  padding-bottom: var(--space-4);
  margin-bottom: var(--space-4);
  border-bottom: 1px solid var(--border);
}

.podcasts-header p {
  max-width: 480px;
}

.podcast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-3);
}

.podcast-skeleton-card {
  height: 260px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: linear-gradient(100deg, var(--bg-elevated) 30%, #232327 50%, var(--bg-elevated) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}
```

- [ ] **Step 3: Create `NewPodcast` and `EditPodcast`**

Create `frontend/src/podcasts/NewPodcast.jsx`:

```jsx
import { useNavigate } from 'react-router-dom'
import { createPodcast } from '../api/podcasts'
import PodcastForm from './PodcastForm'

export default function NewPodcast() {
  const navigate = useNavigate()

  async function handleSubmit(values) {
    await createPodcast(values)
    navigate('/podcasts')
  }

  return (
    <div className="page container">
      <h1>Add Podcast</h1>
      <PodcastForm onSubmit={handleSubmit} submitLabel="Add Podcast" />
    </div>
  )
}
```

Create `frontend/src/podcasts/EditPodcast.jsx`:

```jsx
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getPodcast, updatePodcast } from '../api/podcasts'
import PodcastForm from './PodcastForm'

export default function EditPodcast() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [podcast, setPodcast] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    getPodcast(id)
      .then((data) => {
        setPodcast(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  async function handleSubmit(values) {
    await updatePodcast(id, values)
    navigate('/podcasts')
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading podcast…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load podcast: {error}</p>
      </div>
    )
  }

  return (
    <div className="page container">
      <h1>Edit Podcast</h1>
      <PodcastForm initialValues={podcast} onSubmit={handleSubmit} submitLabel="Save Changes" />
    </div>
  )
}
```

- [ ] **Step 4: Wire routes into `App.jsx`**

Replace the full contents of `frontend/src/App.jsx` with:

```jsx
import { Routes, Route } from 'react-router-dom'
import Ticker from './components/Ticker'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import PostDetail from './pages/PostDetail'
import NewPost from './pages/NewPost'
import EditPost from './pages/EditPost'
import PodcastsPage from './podcasts/PodcastsPage'
import NewPodcast from './podcasts/NewPodcast'
import EditPodcast from './podcasts/EditPodcast'

export default function App() {
  return (
    <>
      <Ticker />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/posts/new" element={<NewPost />} />
        <Route path="/posts/:id" element={<PostDetail />} />
        <Route path="/posts/:id/edit" element={<EditPost />} />
        <Route path="/podcasts" element={<PodcastsPage />} />
        <Route path="/podcasts/new" element={<NewPodcast />} />
        <Route path="/podcasts/:id/edit" element={<EditPodcast />} />
      </Routes>
    </>
  )
}
```

(This only adds the three podcast routes and their imports — `Backdrop` and `Footer` are not part of this task and will be added by Tasks 5 and 7.)

- [ ] **Step 5: Add the nav link**

Replace the full contents of `frontend/src/components/Navbar.jsx` with:

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 24)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <nav className={`navbar${scrolled ? ' navbar-scrolled' : ''}`}>
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          The Daily<span>Current</span>
        </Link>
        <div className="navbar-actions">
          <Link to="/podcasts" className="btn">
            Podcasts
          </Link>
          <Link to="/posts/new" className="btn btn-primary">
            New Post
          </Link>
        </div>
      </div>
    </nav>
  )
}
```

Add to `frontend/src/components/Navbar.css`:

```css
.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
```

- [ ] **Step 6: Verify**

With both servers running and fresh (backend serving 10 seeded podcasts from Task 2), in the browser:
1. Visit `/podcasts` — 10 podcast cards render with cover images, source badges, and descriptions.
2. Click "Listen on `<source>`" on any card — it opens the platform's homepage in a new tab.
3. Click "Add Podcast", fill the form, submit — redirected to `/podcasts`, the new entry appears.
4. Click "Edit" on a card, change the title, submit — the change is reflected in the list.
5. Click "Delete" on a card, confirm — the card disappears and the count drops.
6. Confirm the "Podcasts" link is visible in the navbar on every page and navigates correctly.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/podcasts frontend/src/App.jsx frontend/src/components/Navbar.jsx frontend/src/components/Navbar.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add podcasts pages, routes, and nav link"
```

---

### Task 5: Frontend — heavy layered background

**Files:**
- Create: `frontend/src/components/Backdrop.jsx`
- Create: `frontend/src/components/Backdrop.css`
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Consumes: the existing `drift` keyframe and `--accent`/`--border` tokens from `index.css`.
- Produces: an always-mounted `<Backdrop />` component; two new `body::before`/`body::after` global layers.

- [ ] **Step 1: Create `Backdrop`**

Create `frontend/src/components/Backdrop.jsx`:

```jsx
import './Backdrop.css'

export default function Backdrop() {
  return (
    <div className="backdrop" aria-hidden="true">
      <span className="backdrop-orb backdrop-orb-1" />
      <span className="backdrop-orb backdrop-orb-2" />
      <span className="backdrop-orb backdrop-orb-3" />
    </div>
  )
}
```

Create `frontend/src/components/Backdrop.css`:

```css
.backdrop {
  position: fixed;
  inset: 0;
  z-index: -3;
  overflow: hidden;
  pointer-events: none;
}

.backdrop-orb {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
  filter: blur(80px);
  opacity: 0.16;
  animation: drift 26s ease-in-out infinite;
}

.backdrop-orb-1 {
  width: 480px;
  height: 480px;
  top: -120px;
  left: -100px;
}

.backdrop-orb-2 {
  width: 560px;
  height: 560px;
  top: 40%;
  right: -180px;
  animation-duration: 32s;
  animation-delay: -8s;
  opacity: 0.12;
}

.backdrop-orb-3 {
  width: 400px;
  height: 400px;
  bottom: -140px;
  left: 30%;
  animation-duration: 28s;
  animation-delay: -14s;
  opacity: 0.14;
}

@media (prefers-reduced-motion: reduce) {
  .backdrop-orb {
    animation: none !important;
  }
}
```

- [ ] **Step 2: Add the dot-grid and grain layers**

Append to `frontend/src/index.css` (at the end of the file, after the Phase 3 reduced-motion blocks):

```css
/* ---- Phase 5: heavy layered background ---- */

body::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  background-image: radial-gradient(var(--border) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.35;
}

body::after {
  content: '';
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: 0.05;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

.tag-chip {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--text-dim);
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 2px 8px;
  border-radius: 999px;
}
```

(`.tag-chip` is added here now, alongside the other cross-component badge classes like `.category-pill`/`.country-badge`, because Task 6 needs it in both `PostCard` and `PostDetail`.)

- [ ] **Step 3: Mount `Backdrop`**

In `frontend/src/App.jsx`, add the import:

```jsx
import Backdrop from './components/Backdrop'
```

and render it as the first child, before `<Ticker />`:

```jsx
    <>
      <Backdrop />
      <Ticker />
      <Navbar />
```

- [ ] **Step 4: Verify**

In the browser: confirm the dot-grid and drifting orbs are visible behind the page content on every route, confirm no new scrollbar appears (the layers are all `position: fixed`), and confirm the page still loads and functions normally. Then verify reduced-motion handling — inject the following via the browser console (this project's established workaround for environments where the DevTools emulation toggle isn't reliably drivable):

```js
const style = document.createElement('style')
style.textContent = '@media (prefers-reduced-motion: no-preference) { .backdrop-orb { animation: none !important; } }'
```

Or, more directly, confirm the `@media (prefers-reduced-motion: reduce)` rule in `Backdrop.css` matches the existing reduced-motion rules elsewhere in the codebase and freezes `.backdrop-orb`.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Backdrop.jsx frontend/src/components/Backdrop.css frontend/src/index.css frontend/src/App.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add heavy layered background (dot grid, grain, drifting orbs)"
```

---

### Task 6: Frontend — denser posts (tags, read time, stats, share, related)

**Files:**
- Create: `frontend/src/utils/postMeta.js`
- Modify: `frontend/src/components/PostCard.jsx`
- Modify: `frontend/src/components/PostCard.css`
- Modify: `frontend/src/pages/PostDetail.jsx`
- Modify: `frontend/src/pages/PostDetail.css`

**Interfaces:**
- Consumes: `.tag-chip` (Task 5, in `index.css`); `listPosts` from `api/posts.js` (existing).
- Produces: `getTags(post)`, `getReadTime(content)`, `getStats(post)` from `postMeta.js`.

- [ ] **Step 1: Create the shared post-metadata utility**

Create `frontend/src/utils/postMeta.js`:

```js
const DESCRIPTORS = ['Analysis', 'Report', 'Feature', 'Briefing', 'Opinion']

export function getTags(post) {
  const descriptor = DESCRIPTORS[post.id % DESCRIPTORS.length]
  return [post.category, post.country, descriptor]
}

export function getReadTime(content) {
  const words = content.trim().split(/\s+/).filter(Boolean).length
  const minutes = Math.max(1, Math.round(words / 200))
  return `${minutes} min read`
}

function seededNumber(seed, min, max) {
  const x = Math.sin(seed * 9973) * 10000
  const frac = x - Math.floor(x)
  return Math.floor(frac * (max - min)) + min
}

export function getStats(post) {
  const views = seededNumber(post.id * 7 + 1, 800, 48000)
  const comments = seededNumber(post.id * 13 + 3, 4, 260)
  return {
    views: views >= 1000 ? `${(views / 1000).toFixed(1)}K` : `${views}`,
    comments,
  }
}
```

- [ ] **Step 2: Add the footer row to `PostCard`**

Replace the full contents of `frontend/src/components/PostCard.jsx` with:

```jsx
import { Link } from 'react-router-dom'
import { useInView } from '../hooks/useInView'
import { resolveImageUrl } from '../api/posts'
import { COUNTRY_FLAGS } from '../constants'
import { getTags, getReadTime, getStats } from '../utils/postMeta'
import './PostCard.css'

function excerpt(content, length = 140) {
  const flat = content.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PostCard({ post, index = 0 }) {
  const [ref, inView] = useInView()
  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
  const stats = getStats(post)

  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect()
    e.currentTarget.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
    e.currentTarget.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
  }

  return (
    <Link
      to={`/posts/${post.id}`}
      className={`post-card${inView ? ' fade-up-item' : ''}`}
      style={inView ? { animationDelay: `${Math.min(index, 8) * 60}ms` } : { opacity: 0 }}
      ref={ref}
      onMouseMove={handleMouseMove}
    >
      {post.image_url && (
        <img
          src={resolveImageUrl(post.image_url)}
          alt=""
          className="post-card-image"
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      )}
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">
          {COUNTRY_FLAGS[post.country]} {post.country}
        </span>
      </div>
      <h2>{post.title}</h2>
      <p className="post-card-excerpt">{excerpt(post.content)}</p>
      <div className="post-card-meta">
        {post.author} · {date}
      </div>
      <div className="post-card-tags">
        {getTags(post).map((tag) => (
          <span key={tag} className="tag-chip">
            {tag}
          </span>
        ))}
      </div>
      <div className="post-card-stats">
        <span>{getReadTime(post.content)}</span>
        <span>{stats.views} views</span>
        <span>{stats.comments} comments</span>
      </div>
    </Link>
  )
}
```

Append to `frontend/src/components/PostCard.css`:

```css
/* ---- Phase 5: tags + stats footer ---- */

.post-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: var(--space-1);
}

.post-card-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-top: 6px;
}
```

- [ ] **Step 3: Add tags/stats/share/related to `PostDetail`**

Replace the full contents of `frontend/src/pages/PostDetail.jsx` with:

```jsx
import { useEffect, useState } from 'react'
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom'
import { resolveImageUrl, getPost, deletePost, listPosts } from '../api/posts'
import { COUNTRY_FLAGS } from '../constants'
import { getTags, getReadTime, getStats } from '../utils/postMeta'
import './PostDetail.css'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [showToast, setShowToast] = useState(Boolean(location.state?.justSaved))
  const [toastMessage] = useState(location.state?.message || 'Saved!')
  const [relatedPosts, setRelatedPosts] = useState([])
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    setStatus('loading')
    getPost(id)
      .then((data) => {
        setPost(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  useEffect(() => {
    if (!post) return
    let ignore = false
    listPosts()
      .then((all) => {
        if (ignore) return
        const related = all
          .filter((p) => p.id !== post.id && (p.category === post.category || p.country === post.country))
          .slice(0, 4)
        setRelatedPosts(related)
      })
      .catch(() => {
        // related posts are a nice-to-have; failing silently keeps the page usable
      })
    return () => {
      ignore = true
    }
  }, [post])

  useEffect(() => {
    if (!showToast) return
    const timer = setTimeout(() => setShowToast(false), 2500)
    return () => clearTimeout(timer)
  }, [showToast])

  useEffect(() => {
    if (location.state?.justSaved) {
      navigate(location.pathname, { replace: true, state: {} })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleDelete() {
    if (!window.confirm('Delete this post? This cannot be undone.')) return
    try {
      await deletePost(id)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  function handleCopyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading post…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load post: {error}</p>
      </div>
    )
  }

  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
  const stats = getStats(post)
  const shareText = encodeURIComponent(post.title)
  const shareUrl = encodeURIComponent(window.location.href)

  return (
    <div className="page container post-detail">
      {showToast && (
        <div className="save-toast">
          <svg viewBox="0 0 16 16" className="save-toast-check">
            <polyline points="3,8 7,12 13,4" />
          </svg>
          {toastMessage}
        </div>
      )}
      {post.image_url && (
        <img
          src={resolveImageUrl(post.image_url)}
          alt=""
          className="post-detail-image"
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      )}
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">
          {COUNTRY_FLAGS[post.country]} {post.country}
        </span>
      </div>
      <h1>{post.title}</h1>
      <div className="post-detail-meta state-message">
        {post.author} · {date}
      </div>
      <p className="post-detail-body">{post.content}</p>

      <div className="post-detail-extras">
        <div className="post-detail-tags">
          {getTags(post).map((tag) => (
            <span key={tag} className="tag-chip">
              {tag}
            </span>
          ))}
        </div>
        <div className="post-detail-stats">
          <span>{getReadTime(post.content)}</span>
          <span>{stats.views} views</span>
          <span>{stats.comments} comments</span>
        </div>
        <div className="post-detail-share">
          <span className="post-detail-share-label">Share:</span>
          <button type="button" className="btn" onClick={handleCopyLink}>
            {copied ? 'Copied!' : 'Copy link'}
          </button>
          <a
            className="btn"
            href={`https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            X
          </a>
          <a
            className="btn"
            href={`https://www.facebook.com/sharer/sharer.php?u=${shareUrl}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Facebook
          </a>
          <a className="btn" href={`mailto:?subject=${shareText}&body=${shareUrl}`}>
            Email
          </a>
        </div>
      </div>

      {relatedPosts.length > 0 && (
        <div className="related-posts">
          <h2 className="related-posts-title">More like this</h2>
          <div className="related-posts-grid">
            {relatedPosts.map((related) => (
              <Link key={related.id} to={`/posts/${related.id}`} className="related-post-card">
                {related.image_url && (
                  <img src={resolveImageUrl(related.image_url)} alt="" className="related-post-image" />
                )}
                <span className="related-post-title">{related.title}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="post-detail-actions">
        <Link to={`/posts/${post.id}/edit`} className="btn">
          Edit
        </Link>
        <button className="btn btn-danger" onClick={handleDelete}>
          Delete
        </button>
      </div>
      {error && <p className="state-message error">{error}</p>}
    </div>
  )
}
```

Append to `frontend/src/pages/PostDetail.css`:

```css
/* ---- Phase 5: post extras (tags, stats, share) ---- */

.post-detail-extras {
  max-width: 680px;
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.post-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.post-detail-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  font-size: 0.85rem;
  color: var(--text-dim);
}

.post-detail-share {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-1);
}

.post-detail-share-label {
  font-size: 0.85rem;
  color: var(--text-dim);
  margin-right: 4px;
}

/* ---- Phase 5: related posts ---- */

.related-posts {
  max-width: 680px;
  margin-top: var(--space-4);
}

.related-posts-title {
  font-size: 1.3rem;
  margin-bottom: var(--space-2);
}

.related-posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-2);
}

.related-post-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: border-color 0.15s ease, translate 0.15s ease;
}

.related-post-card:hover {
  border-color: var(--accent);
  translate: 0 -2px;
  text-decoration: none;
}

.related-post-image {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.related-post-title {
  padding: var(--space-1) var(--space-2) var(--space-2);
  font-size: 0.9rem;
  color: var(--text);
  font-weight: 500;
}
```

- [ ] **Step 4: Verify**

In the browser: on the Home grid, confirm every `PostCard` shows tag chips and a read-time/views/comments line. Open a post's detail page: confirm the same block appears after the article body, confirm "Copy link" copies the URL and shows "Copied!" briefly, confirm the X/Facebook/Email buttons build correct URLs (inspect `href`), and confirm a "More like this" strip appears with posts sharing the same category or country (and does not appear/crash when there are none — unlikely at 40 posts, but the code path should degrade gracefully).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/utils/postMeta.js frontend/src/components/PostCard.jsx frontend/src/components/PostCard.css frontend/src/pages/PostDetail.jsx frontend/src/pages/PostDetail.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add tags, read time, stats, share buttons, and related posts"
```

---

### Task 7: Frontend — site-wide footer

**Files:**
- Create: `frontend/src/components/Footer.jsx`
- Create: `frontend/src/components/Footer.css`
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Consumes: `CATEGORIES`, `COUNTRIES`, `COUNTRY_FLAGS` from `constants.js` (existing).
- Produces: a `<Footer />` mounted on every route.

- [ ] **Step 1: Create `Footer`**

Create `frontend/src/components/Footer.jsx`:

```jsx
import { Link } from 'react-router-dom'
import { CATEGORIES, COUNTRIES, COUNTRY_FLAGS } from '../constants'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner container">
        <div className="site-footer-grid">
          <div className="site-footer-brand">
            <span className="site-footer-brand-name">
              The Daily<span>Current</span>
            </span>
            <p>
              Independent reporting on technology, business, science, and the world beyond your
              feed.
            </p>
          </div>
          <div className="site-footer-column">
            <h3>Categories</h3>
            <ul>
              {CATEGORIES.map((c) => (
                <li key={c}>
                  <Link to={`/?category=${encodeURIComponent(c)}`}>{c}</Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="site-footer-column">
            <h3>Countries</h3>
            <ul>
              {COUNTRIES.map((c) => (
                <li key={c}>
                  <Link to={`/?countries=${encodeURIComponent(c)}`}>
                    {COUNTRY_FLAGS[c]} {c}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="site-footer-column">
            <h3>Explore</h3>
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/podcasts">Podcasts</Link>
              </li>
              <li>
                <Link to="/posts/new">New Post</Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="site-footer-bottom">
          <span>© 2026 The DailyCurrent. Fictional demo publication, built for portfolio purposes only.</span>
          <span>Built with FastAPI, SQLAlchemy &amp; React.</span>
        </div>
      </div>
    </footer>
  )
}
```

Create `frontend/src/components/Footer.css`:

```css
.site-footer {
  margin-top: var(--space-5);
  border-top: 1px solid var(--border);
  background: var(--bg-elevated);
}

.site-footer-inner {
  padding-top: var(--space-4);
  padding-bottom: var(--space-4);
}

.site-footer-grid {
  display: grid;
  grid-template-columns: 2fr repeat(3, 1fr);
  gap: var(--space-4);
}

.site-footer-brand-name {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
}

.site-footer-brand-name span {
  color: var(--accent);
}

.site-footer-brand p {
  margin-top: var(--space-1);
  max-width: 320px;
}

.site-footer-column h3 {
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: var(--space-2);
}

.site-footer-column ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.site-footer-column a {
  color: var(--text-dim);
  font-size: 0.9rem;
}

.site-footer-column a:hover {
  color: var(--accent);
}

.site-footer-bottom {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: var(--space-1);
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--text-dim);
}

@media (max-width: 640px) {
  .site-footer-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Mount `Footer`**

In `frontend/src/App.jsx`, add the import:

```jsx
import Footer from './components/Footer'
```

and render it as the last child, after `<Routes>...</Routes>` and before the closing `</>`:

```jsx
      </Routes>
      <Footer />
    </>
```

- [ ] **Step 3: Verify**

In the browser, visit Home, a post detail page, and `/podcasts`: confirm the footer renders at the bottom of every one of them, confirm its Categories/Countries links navigate to Home with the right filter applied (check the URL query params), and confirm the layout collapses to one column at narrow widths (~400px).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Footer.jsx frontend/src/components/Footer.css frontend/src/App.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add site-wide footer"
```

---

## Final Review

After Task 7, dispatch the whole-branch final code review (superpowers:subagent-driven-development's final-review step) on the most capable available model, covering: color-token discipline (no new colors introduced anywhere), reduced-motion coverage for every new animation, the `App.jsx` merge across Tasks 4/5/7 (imports and mount order), the `.tag-chip` class living in `index.css` and being consumed correctly by both `PostCard` and `PostDetail`, backend `Podcast` CRUD parity with `Post`, seed-data idempotency, and general spec compliance against `docs/superpowers/specs/2026-09-29-phase5-heavy-design-podcasts-design.md`.
