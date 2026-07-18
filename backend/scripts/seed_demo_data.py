"""
Demo data seed script.

Populates the database with a couple of demo authors and a handful of
short-story "novels" (each with 2-3 chapters) so the app doesn't look
empty on a fresh install. Safe to re-run: it checks for existing rows
by unique slug/username and skips anything already present.

Usage (from inside the backend container):
    python -m scripts.seed_demo_data
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, UserRole, Novel, NovelStatus, Chapter, ChapterStatus, Genre, Tag, NovelGenre, NovelTag
from app.utils import hash_password, slugify


DEMO_AUTHORS = [
    {
        "username": "elena_marsh",
        "display_name": "Elena Marsh",
        "email": "elena.marsh@taledrop-demo.com",
        "bio": "Writes quiet, character-driven short fiction about memory and distance.",
    },
    {
        "username": "raghav_iyer",
        "display_name": "Raghav Iyer",
        "email": "raghav.iyer@taledrop-demo.com",
        "bio": "Speculative fiction writer exploring near-future technology and identity.",
    },
]

GENRES = ["Fantasy", "Science Fiction", "Drama", "Mystery", "Romance", "Horror"]
TAGS = ["short-story", "slice-of-life", "demo"]

NOVELS = [
    {
        "title": "The Lighthouse Keeper's Daughter",
        "description": (
            "When Mira inherits her late father's lighthouse on a remote coastline, "
            "she finds his logbooks full of entries about a ship that was never "
            "reported missing — and a light that keeps turning on by itself."
        ),
        "author": "elena_marsh",
        "genres": ["Mystery", "Drama"],
        "chapters": [
            (
                "The Inheritance",
                "Mira had not set foot on the island since she was twelve, and the "
                "ferry captain did not recognize her until she said her father's name.\n\n"
                "\"Old Tom's girl,\" he said, like it explained everything. In a way, it did.\n\n"
                "The lighthouse stood the way she remembered it: white paint gone grey, "
                "the lamp room dark even though it was barely dusk. She had the key her "
                "father's lawyer had mailed her, still warm from her pocket, and she stood "
                "at the door for a long moment before she used it.\n\n"
                "Inside, the air smelled of salt and old paper. Stacks of logbooks lined "
                "the stairwell, each one dated in her father's cramped handwriting. She "
                "picked up the most recent one, dated only three weeks before he died, "
                "and the first entry stopped her cold: *Saw her again tonight. The Amara "
                "Jane. Lights on, nobody aboard.*"
            ),
            (
                "The Amara Jane",
                "Mira spent the next morning at the harbor office, asking about a ship "
                "called the Amara Jane. The clerk, a young man who looked like he wanted "
                "to be anywhere else, finally admitted there was a record — a fishing "
                "vessel that went down in a storm eleven years ago. All hands lost. No "
                "survivors, no wreckage ever found.\n\n"
                "\"Your dad used to ask about it too,\" the clerk said. \"Every few months. "
                "We stopped putting it in the file after a while.\"\n\n"
                "That night, Mira climbed to the lamp room for the first time since she "
                "was a child. The old mechanism was dead, disconnected, exactly as the "
                "estate papers had said it would be. And yet, at eleven minutes past "
                "midnight, by her watch, the light came on."
            ),
            (
                "What the Light Remembers",
                "She did not sleep. She sat at the base of the lamp housing and watched "
                "the beam sweep across black water, searching for a source of power that, "
                "by every wire and switch she could find, did not exist.\n\n"
                "At dawn, exhausted, she found the last thing her father had written, "
                "tucked into the final logbook, not dated: *I don't think it's asking to "
                "be found anymore. I think it's just making sure nobody else goes looking "
                "for them.*\n\n"
                "Mira closed the book. Outside, the light kept turning, faithful and "
                "patient, the way it had for eleven years, the way — she understood now — "
                "it might for eleven more. She decided, standing there, that she would "
                "stay and keep it running herself."
            ),
        ],
    },
    {
        "title": "Signal Drift",
        "description": (
            "A communications tech on a generation ship picks up a message that "
            "shouldn't exist — transmitted from a planet the ship's records say was "
            "never surveyed."
        ),
        "author": "raghav_iyer",
        "genres": ["Science Fiction", "Mystery"],
        "chapters": [
            (
                "Anomaly",
                "Kel had listened to eleven years of static in this chair, and she knew "
                "the difference between noise and signal the way a sailor knows weather. "
                "So when the pattern came through at 0340 ship-time, she didn't dismiss "
                "it — she woke the duty officer.\n\n"
                "\"It's structured,\" she said, pulling up the waveform. \"Repeating. "
                "Thirty-one second cycle.\"\n\n"
                "\"From where?\"\n\n"
                "She hesitated before answering, because the coordinates made no sense. "
                "\"Kepler-9c. The system we're not supposed to reach for another forty "
                "years. The one nobody's ever sent a probe to.\""
            ),
            (
                "Forty Years Early",
                "The captain called it equipment failure. The science officer called it "
                "a natural phenomenon, some quirk of the system's star throwing off a "
                "false signal. Kel ran the numbers three more times and got the same "
                "result: the transmission was artificial, and it was arriving from "
                "exactly where the ship's charts said there was nothing but an unmapped "
                "rock.\n\n"
                "On the fourth night, the signal changed. It stopped repeating and, for "
                "nine seconds, resolved into something almost like a voice — compressed, "
                "warped, but unmistakably a voice, speaking words Kel didn't recognize in "
                "a rhythm that felt uncomfortably human."
            ),
            (
                "Who's Listening",
                "She brought the recording to the ship's linguist, who went pale before "
                "the second playback finished.\n\n"
                "\"That's Old Fenrisi,\" he said. \"Nobody's spoken it in three hundred "
                "years. It died out on the first colony ships — before this one even "
                "launched.\"\n\n"
                "Kel looked at the coordinates again, at the planet with no probes and no "
                "survey data and no reason, on paper, to hold anyone at all. Somewhere "
                "out there, something was still transmitting in a dead language, thirty-one "
                "seconds at a time, to whoever might still be listening. She reached over "
                "and opened a return channel."
            ),
        ],
    },
    {
        "title": "Recipe for Rain",
        "description": (
            "A short, quiet story about a grandmother teaching her granddaughter to cook "
            "during the last summer they'll spend in the family kitchen before the house "
            "is sold."
        ),
        "author": "elena_marsh",
        "genres": ["Drama", "Romance"],
        "chapters": [
            (
                "Flour on the Counter",
                "Grandma Nell measured nothing. Priya had brought a notebook for exactly "
                "this reason, and it sat closed on the counter while Nell threw handfuls "
                "of flour into a bowl by feel.\n\n"
                "\"You can't write down a handful,\" Nell said, not unkindly, when Priya "
                "protested. \"You have to know what it looks like. Come here, put your "
                "hand in.\"\n\n"
                "Outside, the FOR SALE sign had gone up that morning. Neither of them "
                "mentioned it. The dough came together slowly under both their hands, and "
                "for an hour, the house was just a kitchen again, and not a thing about "
                "to be lost."
            ),
            (
                "The Last Batch",
                "By August they had made the bread a dozen times, and Priya's notebook "
                "stayed empty, filled instead with flour-fingerprints and the smell of "
                "rain through an open window. On the last night before the movers came, "
                "Nell handed her the wooden spoon.\n\n"
                "\"Your turn to lead,\" she said.\n\n"
                "Priya's hands remembered what her notebook never could. She measured "
                "nothing, and it came out right, and when she looked up her grandmother "
                "was crying and smiling at the same time, in the way of someone who has "
                "successfully given something away."
            ),
        ],
    },
    {
        "title": "The House on Corvid Lane",
        "description": (
            "A horror short story about a new homeowner who keeps finding the same crow "
            "painted into every room, in a house that was supposedly never renovated."
        ),
        "author": "raghav_iyer",
        "genres": ["Horror", "Mystery"],
        "chapters": [
            (
                "Fresh Paint",
                "The realtor had called it \"move-in ready,\" which Dev now understood to "
                "mean someone had painted over everything in a hurry. He found the first "
                "crow while sanding a doorframe in the study — a small black shape beneath "
                "three layers of white, wings spread, painted directly onto the wood.\n\n"
                "He found the second one in the pantry. The third, in the space behind the "
                "bathroom mirror, where no one would ever think to look, painted with the "
                "same careful, deliberate hand."
            ),
            (
                "Thirteen Rooms",
                "The house had thirteen rooms, and Dev found a crow in each of them, "
                "always hidden, always facing the same direction — toward the cellar door "
                "he had not yet opened. The previous owner's forwarding address bounced "
                "back undeliverable. The neighbors changed the subject whenever he brought "
                "up the house's history.\n\n"
                "On the thirteenth night, he finally went down to the cellar with a "
                "flashlight and found the thirteenth crow was not painted at all."
            ),
        ],
    },
]


def get_or_create_genre(db, name):
    genre = db.query(Genre).filter(Genre.name == name).first()
    if genre:
        return genre
    genre = Genre(name=name, slug=slugify(name))
    db.add(genre)
    db.flush()
    return genre


def get_or_create_tag(db, name):
    tag = db.query(Tag).filter(Tag.name == name).first()
    if tag:
        return tag
    tag = Tag(name=name, slug=slugify(name))
    db.add(tag)
    db.flush()
    return tag


def get_or_create_author(db, data):
    user = db.query(User).filter(User.username == data["username"]).first()
    if user:
        return user
    user = User(
        username=data["username"],
        display_name=data["display_name"],
        email=data["email"],
        password=hash_password("DemoPass123!"),
        bio=data["bio"],
        role=UserRole.AUTHOR,
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def seed():
    db = SessionLocal()
    try:
        authors = {a["username"]: get_or_create_author(db, a) for a in DEMO_AUTHORS}
        genres = {name: get_or_create_genre(db, name) for name in GENRES}
        tags = {name: get_or_create_tag(db, name) for name in TAGS}
        db.commit()

        created, skipped = 0, 0
        for novel_data in NOVELS:
            slug = slugify(novel_data["title"])
            existing = db.query(Novel).filter(Novel.slug == slug).first()
            if existing:
                skipped += 1
                continue

            novel = Novel(
                title=novel_data["title"],
                slug=slug,
                description=novel_data["description"],
                language="en",
                status=NovelStatus.PUBLISHED,
                is_premium=False,
                price=0.0,
                views=0,
                likes=0,
                average_rating=0.0,
                author_id=authors[novel_data["author"]].id,
            )
            db.add(novel)
            db.flush()

            for genre_name in novel_data["genres"]:
                db.add(NovelGenre(novel_id=novel.id, genre_id=genres[genre_name].id))
            for tag_name in TAGS:
                db.add(NovelTag(novel_id=novel.id, tag_id=tags[tag_name].id))

            for i, (chapter_title, content) in enumerate(novel_data["chapters"], start=1):
                db.add(
                    Chapter(
                        novel_id=novel.id,
                        chapter_number=i,
                        title=chapter_title,
                        content=content,
                        is_premium=False,
                        price=0.0,
                        views=0,
                        status=ChapterStatus.PUBLISHED,
                    )
                )

            db.commit()
            created += 1
            print(f"Created: {novel_data['title']} ({len(novel_data['chapters'])} chapters)")

        print(f"\nDone. {created} novel(s) created, {skipped} already existed.")
        print("Demo author login (for either demo author's email above): password 'DemoPass123!'")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
