"""
Train the Uzbek spam classifier (char n-gram TF-IDF + logistic regression).

Small, CPU-only and fast: trains in seconds, predicts in well under a
millisecond, and copes with Latin/Cyrillic mixing and Uzbek suffixes because
it works on character n-grams of normalized text.

Data:
  * HF dataset sukhrobnurali/uzbek_spam_dataset (2000 synthetic messages)
  * real Uzbek Telegram/news lines from tahrirchi/uz-crawl as extra
    "normal" examples, so the model sees how people actually write
  * uzspam_model/data/*.jsonl - hand-written seed examples by spam category
    (jobs, crypto, betting, loans, adult, documents, giveaways, phishing,
    promo) plus tricky normal messages that talk about money and work
  * any number of JSONL files exported from the bot's own moderation
    (scripts/export_spam_dataset.py) - this is what will make it good

Usage (from the repository root):
    pip install -r uzspam_model/requirements-train.txt
    python -m uzspam_model.train
    python -m uzspam_model.train --data exports/spam_2026-11.jsonl --real-normal 8000

Writes uzspam_model/model.joblib and prints held-out metrics.
"""
from __future__ import annotations

import argparse
import io
import json
import random
import sys
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from libs.uztext.features import prepare  # noqa: E402

HF_DATASET = "sukhrobnurali/uzbek_spam_dataset"
REAL_DATASET = "tahrirchi/uz-crawl"
DEFAULT_OUT = ROOT / "uzspam_model" / "model.joblib"
# hand-written seed examples (and anything else dropped here) are always used
DATA_DIR = ROOT / "uzspam_model" / "data"
# promo lines inside channel posts would be label noise as "normal"
_PROMO_MARKERS = ("obuna", "t.me", "http", "@", "reklama", "реклама", "обуна")


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def load_hf() -> tuple[pd.DataFrame, pd.DataFrame]:
    base = f"https://huggingface.co/api/datasets/{HF_DATASET}/parquet/default"
    train = pd.read_parquet(io.BytesIO(_fetch(f"{base}/train/0.parquet")))
    test = pd.read_parquet(io.BytesIO(_fetch(f"{base}/test/0.parquet")))
    for df in (train, test):
        df["label"] = (df["label"] == "spam").astype(int)
        df["source"] = "hf"
    return train[["text", "label", "source"]], test[["text", "label", "source"]]


def load_real_normal(limit: int, seed: int) -> pd.DataFrame:
    """Short lines from real Uzbek Telegram blogs and news, labelled normal."""
    lines: list[str] = []
    per_split = max(100, limit)
    for split in ("telegram_blogs", "news"):
        for offset in range(0, per_split, 100):
            url = (
                "https://datasets-server.huggingface.co/rows?"
                f"dataset={REAL_DATASET}&config=default&split={split}"
                f"&offset={offset}&length=100"
            )
            try:
                rows = json.loads(_fetch(url))["rows"]
            except Exception as exc:  # rate limits etc. - keep what we have
                print(f"  ! {split}@{offset}: {exc}")
                break
            for row in rows:
                for line in row["row"]["text"].split("\n"):
                    line = line.strip()
                    low = line.lower()
                    if 12 <= len(line) <= 400 and not any(m in low for m in _PROMO_MARKERS):
                        lines.append(line)
            time.sleep(0.2)
    random.Random(seed).shuffle(lines)
    lines = list(dict.fromkeys(lines))[:limit]
    return pd.DataFrame({"text": lines, "label": 0, "source": "uz-crawl"})


def load_jsonl(paths: list[Path]) -> pd.DataFrame:
    records = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            label = item["label"]
            if isinstance(label, str):
                label = label.lower() in ("spam", "1", "true")
            records.append({"text": item["text"], "label": int(bool(label)), "source": path.name})
    return pd.DataFrame(records, columns=["text", "label", "source"])


def build_pipeline() -> Pipeline:
    features = FeatureUnion([
        ("char", TfidfVectorizer(
            preprocessor=prepare, analyzer="char_wb", ngram_range=(2, 5),
            min_df=2, max_features=60000, sublinear_tf=True,
        )),
        ("word", TfidfVectorizer(
            preprocessor=prepare, analyzer="word", ngram_range=(1, 2),
            token_pattern=r"(?u)\b\w[\w']+\b", min_df=2, max_features=30000,
            sublinear_tf=True,
        )),
    ])
    return Pipeline([
        ("features", features),
        ("clf", LogisticRegression(C=4.0, class_weight="balanced", max_iter=2000)),
    ])


def pick_threshold(scores: np.ndarray, labels: np.ndarray, max_fpr: float) -> float:
    """Lowest threshold (>= 0.5) whose false-positive rate stays under max_fpr."""
    normal = np.sort(scores[labels == 0])
    if len(normal) == 0:
        return 0.5
    allowed = int(np.floor(max_fpr * len(normal)))
    # scores strictly above the threshold are flagged
    cutoff = normal[-(allowed + 1)] if allowed < len(normal) else 0.0
    return float(max(0.5, min(0.99, cutoff + 1e-6)))


def report(name: str, scores: np.ndarray, labels: np.ndarray, threshold: float) -> dict:
    predicted = (scores > threshold).astype(int)
    normal = labels == 0
    spam = labels == 1
    metrics = {
        "n": int(len(labels)),
        "false_positive_rate": float(predicted[normal].mean()) if normal.any() else None,
        "recall": float(predicted[spam].mean()) if spam.any() else None,
    }
    print(f"\n== {name} (threshold {threshold:.3f}) {metrics}")
    if normal.any() and spam.any():
        print(classification_report(labels, predicted, target_names=["normal", "spam"], digits=3))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, nargs="*", default=[], help="JSONL files with text/label")
    parser.add_argument("--real-normal", type=int, default=4000, help="real Uzbek lines to add as normal (0 = off)")
    parser.add_argument("--max-fpr", type=float, default=0.01, help="target false-positive rate for the threshold")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    print("Loading datasets...")
    hf_train, hf_test = load_hf()
    parts_train, parts_test = [hf_train], [hf_test]

    if args.real_normal:
        real = load_real_normal(args.real_normal, args.seed)
        real_train, real_test = train_test_split(real, test_size=0.25, random_state=args.seed)
        parts_train.append(real_train)
        parts_test.append(real_test)
        print(f"  real normal lines: {len(real)}")

    data_files = sorted(DATA_DIR.glob("*.jsonl")) + list(args.data)
    if data_files:
        own = load_jsonl(data_files)
        if len(own):
            stratify = own["label"] if own["label"].nunique() > 1 and own["label"].value_counts().min() > 1 else None
            own_train, own_test = train_test_split(own, test_size=0.2, random_state=args.seed, stratify=stratify)
            parts_train.append(own_train)
            parts_test.append(own_test)
        print(f"  labelled JSONL messages: {len(own)} (spam={int(own['label'].sum())})")

    train = pd.concat(parts_train, ignore_index=True).drop_duplicates("text")
    test = pd.concat(parts_test, ignore_index=True).drop_duplicates("text")
    test = test[~test["text"].isin(set(train["text"]))]
    print(f"train={len(train)} (spam={int(train.label.sum())})  test={len(test)} (spam={int(test.label.sum())})")

    pipeline = build_pipeline()
    pipeline.fit(train["text"].tolist(), train["label"].to_numpy())

    scores = pipeline.predict_proba(test["text"].tolist())[:, 1]
    labels = test["label"].to_numpy()
    threshold = pick_threshold(scores, labels, args.max_fpr)

    metrics = {"all": report("held-out, all sources", scores, labels, threshold)}
    for source in sorted(test["source"].unique()):
        mask = (test["source"] == source).to_numpy()
        metrics[source] = report(f"held-out, {source}", scores[mask], labels[mask], threshold)

    artifact = {
        "pipeline": pipeline,
        "threshold": threshold,
        "trained_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "train_size": int(len(train)),
        "metrics": metrics,
        "sources": sorted(train["source"].unique().tolist()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, args.out, compress=3)
    size_kb = args.out.stat().st_size // 1024
    print(f"\nSaved {args.out} ({size_kb} KB), threshold={threshold:.3f}")


if __name__ == "__main__":
    main()
