from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

SAMPLE_POSTS = [
    {
        "title": "London Fintech Startups Report Record Funding Quarter",
        "content": (
            "London's fintech sector posted its strongest quarter in three "
            "years, with early-stage startups pulling in significantly more "
            "venture capital than the same period last year, according to "
            "industry trackers.\n\n"
            "Founders point to renewed investor confidence following a "
            "stretch of high interest rates, though some warn the rebound "
            "remains concentrated in a handful of well-connected firms."
        ),
        "author": "Emma Whitfield",
        "category": "Technology",
        "country": "United Kingdom",
        "image_url": "https://picsum.photos/seed/newsblog-1/800/450",
    },
    {
        "title": "Paris Hosts Emergency Summit on Mediterranean Migration Routes",
        "content": (
            "Leaders from a dozen countries met in Paris this week to "
            "discuss a coordinated response to a sharp rise in crossings "
            "along Mediterranean migration routes.\n\n"
            "The summit produced a joint statement on expanded "
            "search-and-rescue funding but stopped short of agreeing on a "
            "shared resettlement quota, a sticking point in similar talks "
            "for years."
        ),
        "author": "Marc Dubois",
        "category": "World",
        "country": "France",
        "image_url": "https://picsum.photos/seed/newsblog-2/800/450",
    },
    {
        "title": "German Manufacturers Warn of Energy Cost Squeeze Heading Into Winter",
        "content": (
            "Industry groups representing German manufacturers cautioned "
            "that rising energy costs could force some smaller producers "
            "to cut shifts or relocate production abroad.\n\n"
            "The warning comes as the government weighs new subsidies "
            "aimed at keeping energy-intensive industries competitive "
            "against producers in lower-cost regions."
        ),
        "author": "Klara Hoffmann",
        "category": "Business",
        "country": "Germany",
        "image_url": "https://picsum.photos/seed/newsblog-3/800/450",
    },
    {
        "title": "Italian Researchers Track Volcanic Activity With New Seismic Network",
        "content": (
            "A newly deployed network of seismic sensors around southern "
            "Italy's volcanic region is giving researchers their most "
            "detailed picture yet of underground magma movement.\n\n"
            "Scientists say the denser sensor coverage could extend "
            "eruption warning times from hours to potentially days in some "
            "scenarios."
        ),
        "author": "Giulia Romano",
        "category": "Science",
        "country": "Italy",
        "image_url": "https://picsum.photos/seed/newsblog-4/800/450",
    },
    {
        "title": "Spanish League Clubs Push Back Against Expanded Tournament Calendar",
        "content": (
            "Several top-flight Spanish clubs have formally objected to "
            "proposals that would add more mid-week fixtures to an already "
            "crowded football calendar.\n\n"
            "Player welfare groups have echoed the concern, citing rising "
            "injury rates linked to insufficient recovery time between "
            "matches."
        ),
        "author": "Javier Moreno",
        "category": "Sports",
        "country": "Spain",
        "image_url": "https://picsum.photos/seed/newsblog-5/800/450",
    },
    {
        "title": "Dutch Ports Expand Capacity Amid Shifting European Trade Routes",
        "content": (
            "Rotterdam and other major Dutch ports are investing heavily "
            "in new capacity as shipping routes adjust to ongoing "
            "disruptions elsewhere in Europe.\n\n"
            "Port authorities say the expansion is intended to secure the "
            "Netherlands' position as a primary gateway for goods entering "
            "the continent."
        ),
        "author": "Sanne de Vries",
        "category": "World",
        "country": "Netherlands",
        "image_url": "https://picsum.photos/seed/newsblog-6/800/450",
    },
    {
        "title": "Polish Manufacturing Rebounds as Nearshoring Trend Accelerates",
        "content": (
            "Poland's manufacturing sector posted its fastest growth in "
            "over a year, driven partly by Western European companies "
            "relocating supply chains closer to home.\n\n"
            "Economists say the nearshoring trend has been a consistent "
            "tailwind for the country's industrial base since global "
            "shipping costs began climbing."
        ),
        "author": "Tomasz Kowalski",
        "category": "Business",
        "country": "Poland",
        "image_url": "https://picsum.photos/seed/newsblog-7/800/450",
    },
    {
        "title": "Swedish Battery Startup Secures Funding for Gigafactory Expansion",
        "content": (
            "A Swedish battery manufacturer announced new funding to "
            "expand production capacity, positioning itself as a key "
            "supplier for the region's growing electric vehicle industry.\n\n"
            "The company said the expansion would roughly double its "
            "annual output once completed, though it declined to give a "
            "firm timeline."
        ),
        "author": "Elin Berg",
        "category": "Technology",
        "country": "Sweden",
        "image_url": "https://picsum.photos/seed/newsblog-8/800/450",
    },
    {
        "title": "Reconstruction Efforts Continue in Eastern Regions Amid Funding Gaps",
        "content": (
            "Local officials in several eastern towns say reconstruction "
            "of housing and infrastructure remains slow, with available "
            "funding falling well short of estimated needs.\n\n"
            "International donors have pledged continued support, though "
            "disbursement timelines remain a source of frustration for "
            "regional administrators."
        ),
        "author": "Olena Petrenko",
        "category": "World",
        "country": "Ukraine",
        "image_url": "https://picsum.photos/seed/newsblog-9/800/450",
    },
    {
        "title": "Greek Marine Biologists Document Rare Coral Recovery in Aegean Sea",
        "content": (
            "A survey team monitoring reef health in the Aegean Sea "
            "reported unexpected signs of coral recovery in areas "
            "previously damaged by warming waters.\n\n"
            "Researchers caution the recovery is localized and likely "
            "dependent on specific current patterns that keep water "
            "temperatures lower than surrounding areas."
        ),
        "author": "Dimitra Alexiou",
        "category": "Science",
        "country": "Greece",
        "image_url": "https://picsum.photos/seed/newsblog-10/800/450",
    },
    {
        "title": "Portuguese Youth Academies Draw International Scouting Interest",
        "content": (
            "A wave of international scouts has been visiting Portuguese "
            "youth academies this season, drawn by a string of standout "
            "performances in regional tournaments.\n\n"
            "Club officials say the increased attention has already led "
            "to several transfer inquiries for players as young as "
            "sixteen."
        ),
        "author": "Rui Fernandes",
        "category": "Sports",
        "country": "Portugal",
        "image_url": "https://picsum.photos/seed/newsblog-11/800/450",
    },
    {
        "title": "Swiss Banks Tighten Lending Standards Amid Regional Uncertainty",
        "content": (
            "Several major Swiss banks have quietly tightened lending "
            "standards for commercial borrowers, citing caution around "
            "broader economic uncertainty in the region.\n\n"
            "Small business groups say the shift has made it harder for "
            "growing companies to secure the credit lines they'd relied "
            "on in previous years."
        ),
        "author": "Lukas Meier",
        "category": "Business",
        "country": "Switzerland",
        "image_url": "https://picsum.photos/seed/newsblog-12/800/450",
    },
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
]

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


if __name__ == "__main__":
    seed()
