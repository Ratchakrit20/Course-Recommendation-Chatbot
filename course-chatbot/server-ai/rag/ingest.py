import json
import os
import re
from typing import Any, Dict, List

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

RAG_DIR = os.path.abspath(os.path.dirname(__file__))     # app/rag
APP_DIR = os.path.abspath(os.path.join(RAG_DIR, ".."))   # app
JSONL_PATH = "./data2/kmutnb_courses_rag_ready_final_patched.jsonl"
CHROMA_DIR = os.path.join(APP_DIR, "chroma_db2") # app/chroma_db
COLLECTION_NAME = "kmutnb_courses"
EMBED_MODEL = "nomic-embed-text-v2-moe"


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    records = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[WARN] Skip line {i}: invalid JSON ({e})")
    return records


def safe_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "faculty": str(record.get("faculty", "")),
        "program": str(record.get("program", "")),
        "program_year": str(record.get("program_year", "")),
        "course_code": str(record.get("course_code", "")),
        "course_name_th": str(record.get("course_name_th", "")),
        "course_name_en": str(record.get("course_name_en", "")),
        "category": str(record.get("category", "")),
        "credits": str(record.get("credits", "")),
        "source_major": str(record.get("source_major", "")),
        "search_priority": float(record.get("search_priority", 0.0)),
        "primary_roles": " | ".join(record.get("primary_roles", [])),
        "intent_tags": " | ".join(record.get("intent_tags", [])),
        "skills": " | ".join(record.get("skills", [])),
        "keywords": " | ".join(record.get("keywords", [])),
    }


def slugify(text: str) -> str:
    text = str(text or "").strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9ก-๙_:-]", "", text)
    return text


def make_unique_id(rec: dict, idx: int) -> str:
    program = slugify(rec.get("program") or "unknown_program")
    code = slugify(rec.get("course_code") or "unknown_code")
    name = slugify(rec.get("course_name_en") or rec.get("course_name_th") or f"course_{idx}")
    return f"{program}::{code}::{name}::{idx}"


def check_duplicate_ids(ids):
    seen = set()
    dup = set()

    for x in ids:
        if x in seen:
            dup.add(x)
        seen.add(x)

    if dup:
        print(f"[ERROR] Found duplicate ids: {len(dup)}")
        for d in list(dup)[:20]:
            print(" -", d)
        raise ValueError("Duplicate IDs still exist. Please fix ID generation.")


def build_documents(records):
    texts = []
    metadatas = []
    ids = []

    for idx, rec in enumerate(records):
        text = rec.get("retrieval_text", "").strip()
        if not text:
            print(f"[WARN] Skip record {idx}: no retrieval_text")
            continue

        rec_id = make_unique_id(rec, idx)

        texts.append(text)
        metadatas.append(safe_metadata(rec))
        ids.append(rec_id)

    return texts, metadatas, ids


def main():
    print("[INFO] Loading JSONL...")
    records = load_jsonl(JSONL_PATH)
    print(f"[INFO] Loaded records: {len(records)}")

    print("[INFO] Preparing documents...")
    texts, metadatas, ids = build_documents(records)
    print(f"[INFO] Ready for ingest: {len(texts)}")

    check_duplicate_ids(ids)

    print(f"[INFO] Loading embeddings model: {EMBED_MODEL}")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    print("[INFO] Creating Chroma vector DB...")
    db = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        ids=ids,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )

    print("[INFO] Persisting DB...")
    db.persist()

    print("[DONE] Ingest complete.")
    print(f"[DONE] Collection: {COLLECTION_NAME}")
    print(f"[DONE] Saved at: {CHROMA_DIR}")


if __name__ == "__main__":
    main()