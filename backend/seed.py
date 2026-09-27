from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

SAMPLE_POSTS = [
    {
        "title": "AI Chip Startups Race to Challenge Nvidia's Dominance",
        "content": (
            "A wave of well-funded startups is betting that specialized silicon "
            "can chip away at Nvidia's grip on AI training hardware. Investors "
            "have poured billions into custom accelerator designs over the past "
            "year, wagering that no single company can serve every workload.\n\n"
            "Analysts remain split on the timeline, but agree the market is no "
            "longer a one-horse race."
        ),
        "author": "Lena Ortiz",
        "category": "Technology",
    },
    {
        "title": "Global Markets Steady After Central Bank Rate Decision",
        "content": (
            "Stocks closed mostly flat Thursday after the central bank held "
            "interest rates steady for a third consecutive meeting, matching "
            "analyst expectations. Bond yields dipped slightly as traders parsed "
            "the accompanying statement for hints about the path ahead.\n\n"
            "Officials reiterated that future moves would depend on incoming "
            "inflation data."
        ),
        "author": "Marcus Webb",
        "category": "Business",
    },
    {
        "title": "Coastal Cities Accelerate Flood Defense Projects",
        "content": (
            "Municipal governments in a dozen coastal cities announced expanded "
            "funding for sea walls, tidal gates, and wetland restoration this "
            "week, citing accelerating erosion data from the past three years.\n\n"
            "Engineers say the projects, some already underway, aim to protect "
            "low-lying neighborhoods well ahead of projected worst-case "
            "flooding scenarios."
        ),
        "author": "Priya Nandakumar",
        "category": "World",
    },
    {
        "title": "Researchers Map Deep-Sea Coral Reef Untouched by Bleaching",
        "content": (
            "A survey team using autonomous submersibles has documented a "
            "previously uncharted coral reef more than 400 meters below the "
            "surface, far deeper than reefs typically studied for bleaching "
            "damage.\n\n"
            "The team says the reef's depth may have shielded it from the "
            "warming surface waters blamed for recent bleaching events "
            "elsewhere."
        ),
        "author": "Tomás Herrera",
        "category": "Science",
    },
    {
        "title": "Underdog Club Reaches Cup Final After Historic Run",
        "content": (
            "A second-division side stunned the football world Tuesday, "
            "eliminating a three-time champion on penalties to reach its first "
            "major cup final in club history.\n\n"
            "Fans flooded the streets after the final whistle, and the club's "
            "manager called it 'the proudest night of my career.'"
        ),
        "author": "Diego Falcone",
        "category": "Sports",
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
