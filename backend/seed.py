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
    },
]


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


if __name__ == "__main__":
    seed()
