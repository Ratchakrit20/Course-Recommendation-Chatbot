
import os
import json
import shutil
from typing import List, Dict

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

RAG_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.abspath(os.path.join(RAG_DIR, ".."))
DATA_DIR = os.path.join(APP_DIR, "data")
CHROMA_ROOT = os.path.join(APP_DIR, "chroma_db")

DEPARTMENT_FILES = {
    "AM": "applied_mathematics_production.json",
    "AS": "applied_statistics_production.json",
    "BT": "biotechnology_2563_production.json",
    "ASB": "business_statistics_and_actuarial_science_production.json",
    "EST": "environmental_science_and_technology_full.json",
    "FST": "food_science_and_technology_full.json",
}

def load_courses(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "courses" in data:
        return data["courses"]
    if isinstance(data, list):
        return data
    return []

def safe_join_list(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if str(v).strip())
    return str(value).strip() if value else ""

def convert_course_to_text(course: Dict) -> str:
    return f"""
[COURSE]
Department: {course.get('department', '')}
Program Domain: {course.get('domain', '')}
Retrieval Group: {course.get('retrieval_group', '')}

[IDENTITY]
Course Code: {course.get('course_code', '')}
Course Name (TH): {course.get('course_name_th', '')}
Course Name (EN): {course.get('course_name_en', '')}
Category: {course.get('category', '')}
Credits: {course.get('credits', '')}

[DESCRIPTION]
{course.get('description', '')}

[SKILLS]
{safe_join_list(course.get('skills', []))}

[TOOLS]
{safe_join_list(course.get('tools', []))}

[LEARNING_OUTCOMES]
{safe_join_list(course.get('learning_outcomes', []))}

[CAREER_TRACKS]
{safe_join_list(course.get('career_tracks', []))}
{safe_join_list(course.get('career_tags', []))}

[MAJOR_FOCUS]
{safe_join_list(course.get('major_focus', []))}

[KEYWORDS]
{safe_join_list(course.get('keywords', []))}

[QUERY_ALIASES]
{safe_join_list(course.get('query_aliases', []))}

[RELATIONS]
Prerequisites: {safe_join_list(course.get('prerequisites', []))}
Related Courses: {safe_join_list(course.get('related_courses', []))}
Recommended Next: {safe_join_list(course.get('recommended_next', []))}

[SEARCH_BOOST]
{course.get('search_boost_text', '')}
""".strip()

def build_metadata(course: Dict) -> Dict:
    return {
        "department": course.get("department", ""),
        "domain": course.get("domain", ""),
        "retrieval_group": course.get("retrieval_group", ""),
        "course_code": course.get("course_code", ""),
        "course_name_th": course.get("course_name_th", ""),
        "course_name_en": course.get("course_name_en", ""),
        "category": course.get("category", ""),
        "credits": str(course.get("credits", "")),
        "description": course.get("description", ""),
        "skills": safe_join_list(course.get("skills", [])),
        "tools": safe_join_list(course.get("tools", [])),
        "career_tracks": safe_join_list(course.get("career_tracks", [])),
        "career_tags": safe_join_list(course.get("career_tags", [])),
        "major_focus": safe_join_list(course.get("major_focus", [])),
        "keywords": safe_join_list(course.get("keywords", [])),
        "query_aliases": safe_join_list(course.get("query_aliases", [])),
        "search_priority": str(course.get("search_priority", "")),
        "recommended_for_default_search": str(course.get("recommended_for_default_search", "")),
    }

def ingest_department(department: str, json_filename: str, embedding_model) -> None:
    json_path = os.path.join(DATA_DIR, json_filename)
    if not os.path.exists(json_path):
        print(f"[SKIP] {department}: file not found -> {json_path}")
        return

    courses = load_courses(json_path)
    if not courses:
        print(f"[SKIP] {department}: no course data")
        return

    texts, metadatas = [], []
    for course in courses:
        if not isinstance(course, dict):
            continue
        texts.append(convert_course_to_text(course))
        metadatas.append(build_metadata(course))

    persist_dir = os.path.join(CHROMA_ROOT, department)
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        persist_directory=persist_dir,
        collection_name=f"{department.lower()}_courses"
    )
    vectordb.persist()
    print(f"[DONE] {department}: {len(texts)} courses -> {persist_dir}")

def main():
    os.makedirs(CHROMA_ROOT, exist_ok=True)
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    for department, filename in DEPARTMENT_FILES.items():
        ingest_department(department, filename, embedding)

if __name__ == "__main__":
    main()
