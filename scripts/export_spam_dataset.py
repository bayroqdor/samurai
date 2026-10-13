"""
Export moderated spam decisions as training data for the Uzbek spam model.

Every message the bot (or an owner via !spam) flagged is stored in the
`spam` table; the review buttons in the logs channel set the final label.

    python -m scripts.export_spam_dataset exports/spam.jsonl
    python -m uzspam_model.train --data exports/spam.jsonl

Only reviewed rows are exported unless --all is given (unreviewed rows carry
the model's own guess, and training on those just teaches it its mistakes).
"""
import argparse
import asyncio
import json
from pathlib import Path

from db.database import close_db, init_db
from db.models import Spam


async def export(out: Path, include_unreviewed: bool) -> tuple[int, int]:
    await init_db()
    try:
        query = Spam.objects if include_unreviewed else Spam.objects.filter(is_reviewed=True)
        rows = await query.all()
    finally:
        await close_db()

    out.parent.mkdir(parents=True, exist_ok=True)
    spam_count = 0
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            spam_count += bool(row.is_spam)
            handle.write(json.dumps({
                "text": row.message,
                "label": "spam" if row.is_spam else "normal",
                "source": row.source,
                "score": row.score,
                "reviewed": row.is_reviewed,
                "date": row.date.isoformat() if row.date else None,
            }, ensure_ascii=False) + "\n")
    return len(rows), spam_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("out", type=Path, help="output .jsonl file")
    parser.add_argument("--all", action="store_true", help="include rows nobody reviewed yet")
    args = parser.parse_args()
    total, spam_count = asyncio.run(export(args.out, args.all))
    print(f"Exported {total} messages ({spam_count} spam, {total - spam_count} normal) to {args.out}")


if __name__ == "__main__":
    main()
