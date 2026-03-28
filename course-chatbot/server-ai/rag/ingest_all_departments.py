import os
import json
import shutil
from typing import List, Dict

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


RAG_DIR = os.path.abspath(os.path.dirname(__file__))     # app/rag
APP_DIR = os.path.abspath(os.path.join(RAG_DIR, ".."))   # app
DATA_DIR = os.path.join(APP_DIR, "data")                 # app/data
CHROMA_ROOT = os.path.join(APP_DIR, "chroma_db")         # app/chroma_db


DEPARTMENT_FILES = {
    "BT": "biotechnology_2563_production.json",
    "AS": "applied_statistics_production.json",
    "ASB": "business_statistics_and_actuarial_science_production.json",
    "SDA": "statistical_data_science_and_analytics_production.json",
    "AM": "applied_mathematics_production.json",
    "CS": "computer_science_full.json",
    "EST": "environmental_science_and_technology_full.json",
    "FST": "food_science_and_technology_full.json",
    "MWCS": "mathematics_with_computer_science_2568_production.json",
    "HBS": "health_and_beauty_science_2567_production.json",
}


def load_courses(json_path: str) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        if "courses" in data:
            return data["courses"]
        return [data]

    if isinstance(data, list):
        if len(data) > 0 and not isinstance(data[0], dict):
            return [{"description": str(x)} for x in data]
        return data

    return [{"description": str(data)}]


def safe_join_list(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value) if value else ""


def convert_course_to_text(course: Dict) -> str:
    return f"""
Department: {course.get('department', '')}
Course Code: {course.get('course_code', '')}
Course Name (TH): {course.get('course_name_th', '')}
Course Name (EN): {course.get('course_name_en', '')}
Description: {course.get('description', '')}
Skills: {safe_join_list(course.get('skills', []))}
Related Careers: {safe_join_list(course.get('careers', []))}
Related Courses: {safe_join_list(course.get('related_courses', []))}
Recommended Next: {safe_join_list(course.get('recommended_next', []))}
Keywords: {safe_join_list(course.get('keywords', []))}
""".strip()


def build_metadata(course: Dict) -> Dict:
    return {
        "department": course.get("department", ""),
        "course_code": course.get("course_code", ""),
        "course_name_th": course.get("course_name_th", ""),
        "course_name_en": course.get("course_name_en", ""),
        "description": course.get("description", ""),
        "skills": safe_join_list(course.get("skills", [])),
        "careers": safe_join_list(course.get("careers", [])),
        "related_courses": safe_join_list(course.get("related_courses", [])),
        "recommended_next": safe_join_list(course.get("recommended_next", [])),
        "keywords": safe_join_list(course.get("keywords", [])),
    }


def ingest_department(department: str, json_filename: str, embedding_model) -> None:
    json_path = os.path.join(DATA_DIR, json_filename)

    if not os.path.exists(json_path):
        print(f"[SKIP] {department}: file not found -> {json_path}")
        return

    courses = load_courses(json_path)
    if not courses:
        print(f"[SKIP] {department}: no data in file")
        return

    print(f"[DEBUG] {department} -> total items: {len(courses)}")
    print(f"[DEBUG] {department} -> courses type: {type(courses)}")
    print(f"[DEBUG] {department} -> first item type: {type(courses[0])}")

    texts = []
    metadatas = []

    for course in courses:
        if not isinstance(course, dict):
            continue

        if "department" not in course or not course["department"]:
            course["department"] = department

        texts.append(convert_course_to_text(course))
        metadatas.append(build_metadata(course))

    if not texts:
        print(f"[SKIP] {department}: no valid course dict items")
        return

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

    print("DATA_DIR =", DATA_DIR)
    print("Files in DATA_DIR =", os.listdir(DATA_DIR))

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    for department, filename in DEPARTMENT_FILES.items():
        ingest_department(department, filename, embedding)

    print("\nAll department vector databases created successfully.")


if __name__ == "__main__":
    main()