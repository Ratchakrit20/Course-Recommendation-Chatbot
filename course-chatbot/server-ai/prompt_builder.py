from typing import List, Dict, Any, Optional


SYSTEM_PROMPT_TH = """
คุณคือผู้ช่วยแนะนำรายวิชามหาวิทยาลัย

ภารกิจ:
- วิเคราะห์คำถามของผู้ใช้โดยอ้างอิงจากข้อมูลรายวิชาใน context เท่านั้น
- เลือกเฉพาะวิชาที่เหมาะสมที่สุดไม่เกิน 5 วิชา จากข้อมูลที่มีอยู่ และมีความเกี่ยวข้องกับคำถามของผู้ใช้มากที่สุด
- จัดเรียงลำดับการเรียนรู้ของวิชาที่เลือกให้สัมพันธ์กับเป้าหมายอาชีพที่สอดคล้องกับคำถามของผู้ใช้
- ตอบกลับเป็น JSON object เดียวเท่านั้น

กฎสำคัญ:
1. ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอื่นใด ๆ แม้แต่คำเดียว หากพบว่าตอบเป็นภาษาอื่น ให้ถือว่าผิดกฎ
2. ใช้เฉพาะข้อมูลที่อยู่ใน context เท่านั้น
3. ทุก field ใน JSON รวมถึง summary, target_career, career_paths, note ต้องเป็นภาษาไทยเท่านั้น
3. ห้ามแต่งชื่อวิชา รหัสวิชา ทักษะ สายอาชีพ หรือรายละเอียดที่ไม่มีใน context
4. ห้ามมี markdown, ห้ามมี ```json, ห้ามมีข้อความก่อนหรือหลัง JSON
5. ต้องใช้ double quotes (") ให้เป็น JSON ที่ valid เท่านั้น
6. ถ้าข้อมูลใน context ระบุว่าไม่พบผลลัพธ์ คำถามไม่ชัดเจน หรือคำถามไม่สอดคล้องกับสาขา ห้ามฝืนแนะนำวิชา
7. ถ้าไม่ควรแนะนำวิชา ให้ตอบเชิงแนะนำว่าผู้ใช้ควรทำอะไรต่อ เช่น ควรระบุอาชีพ เป้าหมาย ทักษะ หรือเปลี่ยนสาขา
8. ห้ามใช้ index ที่ไม่มีอยู่จริงใน context
9. ถ้ามีข้อมูลรายวิชาที่เกี่ยวข้องชัดเจน ให้เลือก 5 วิชา และเรียงลำดับการเรียนจากพื้นฐานไปต่อยอด
10. สำหรับคำถามกว้าง ๆ ให้เน้นวิชาพื้นฐานที่ต่อยอดได้หลายสายก่อน
11. ถ้าข้อมูลไม่ชัดเจนพอ ให้ตอบว่าควรถามอย่างไรใหม่ให้ชัดขึ้น

ถ้า context เป็นกรณีไม่พบข้อมูลหรือไม่ควรตอบเชิงแนะนำวิชา ให้ใช้รูปแบบนี้:
{
  "summary": "ยังไม่สามารถแนะนำวิชาได้อย่างมั่นใจ",
  "target_career": "ยังไม่ชัดเจน",
  "selected_course_indexes": [],
  "learning_order_indexes": [],
  "career_paths": [],
  "note": "อธิบายสั้น ๆ ว่าทำไมยังแนะนำไม่ได้ และผู้ใช้ควรทำอะไรต่อ"
}

ถ้ามีข้อมูลรายวิชาที่เพียงพอ ให้ใช้รูปแบบนี้:
{
  "summary": "สรุปภาพรวมของวิชาที่เลือกและเหตุผลที่เลือก โดยอธิบายให้สัมพันธ์กับคำถามของผู้ใช้",
  "target_career": "เป้าหมายอาชีพ",
  "selected_course_indexes": [1, 2, 3, 4, 5],
  "learning_order_indexes": [1, 2, 3, 4, 5],
  "career_paths": ["อาชีพ1", "อาชีพ2", "อาชีพ3"],
  "note": "ข้อสังเกตเพิ่มเติมหรือแนวทางต่อยอด"
}
""".strip()


def clean_text(value: Any, max_len: Optional[int] = None) -> str:
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    text = " ".join(text.split())

    if max_len and len(text) > max_len:
        text = text[: max_len - 3].rstrip() + "..."
    return text


def limit_items(value: Any, max_items: int = 5) -> str:
    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        cleaned = []
        seen = set()

        for item in value:
            text = clean_text(item)
            key = text.lower()
            if text and key not in seen:
                seen.add(key)
                cleaned.append(text)

        return ", ".join(cleaned[:max_items])

    return clean_text(value)


def is_special_no_result_case(courses: List[Dict[str, Any]]) -> bool:
    if not courses:
        return True

    first = courses[0]
    return (
        first.get("category") == "no_result"
        or first.get("retrieval_group") == "no_result"
        or bool(first.get("search_status"))
    )


def format_course_block(index: int, course: Dict[str, Any]) -> str:
    course_code = clean_text(course.get("course_code"))
    course_name_th = clean_text(course.get("course_name_th"))
    course_name_en = clean_text(course.get("course_name_en"))
    display_name = course_name_th or course_name_en or "ไม่ระบุชื่อวิชา"

    category = clean_text(course.get("category"))
    description = clean_text(course.get("description"), max_len=220)
    keywords = limit_items(course.get("keywords"), max_items=5)
    major_focus = limit_items(course.get("major_focus"), max_items=4)
    skills = limit_items(course.get("skills"), max_items=5)
    career_tracks = limit_items(course.get("career_tracks"), max_items=4)
    recommended_next = limit_items(course.get("recommended_next"), max_items=3)
    score = course.get("final_score", course.get("score", 0))

    fields = [
        f"[วิชา {index}]",
        f"ชื่อวิชา: {display_name}",
        f"รหัสวิชา: {course_code or '-'}",
        f"หมวดหมู่: {category or '-'}",
        f"คะแนนความเกี่ยวข้อง: {score}",
        f"คำอธิบาย: {description or '-'}",
        f"คีย์เวิร์ดสำคัญ: {keywords or '-'}",
        f"จุดเน้น: {major_focus or '-'}",
    ]

    if skills:
        fields.append(f"ทักษะที่เกี่ยวข้อง: {skills}")
    if career_tracks:
        fields.append(f"สายอาชีพที่เกี่ยวข้อง: {career_tracks}")
    if recommended_next:
        fields.append(f"วิชาที่ควรเรียนต่อ: {recommended_next}")

    return "\n".join(fields)


def build_context(courses: List[Dict[str, Any]], max_courses: int = 5) -> str:
    if not courses:
        return "ไม่พบข้อมูลรายวิชาที่เกี่ยวข้อง"

    if is_special_no_result_case(courses):
        item = courses[0]
        suggestion = clean_text(item.get("suggestion"))
        search_status = clean_text(item.get("search_status"))
        program = clean_text(item.get("program") or item.get("source_major"))

        return f"""
[สถานะการค้นหา]
สาขา: {program or '-'}
สถานะ: {search_status or 'no_result'}
คำแนะนำ: {suggestion or 'กรุณาระบุคำถามให้ชัดเจนขึ้น'}
""".strip()

    sorted_courses = sorted(
        courses,
        key=lambda c: c.get("final_score", c.get("score", 0)),
        reverse=True,
    )
    selected_courses = sorted_courses[:max_courses]
    blocks = [format_course_block(i, c) for i, c in enumerate(selected_courses, start=1)]
    return "\n\n".join(blocks)


def build_user_prompt(
    user_query: str,
    department: str,
    courses: List[Dict[str, Any]],
    max_courses: int = 5,
) -> str:
    department_clean = clean_text(department) or "ไม่ระบุสาขา"
    user_query_clean = clean_text(user_query, max_len=300) or "ไม่ได้ระบุคำถาม"
    context = build_context(courses, max_courses=max_courses)

    if not courses or is_special_no_result_case(courses):
        suggestion = ""
        if courses and is_special_no_result_case(courses):
            suggestion = clean_text(courses[0].get("suggestion"))

        return f"""
สาขา: {department_clean}
คำถามของผู้ใช้: {user_query_clean}

ผลการค้นหา:
{context}

ให้ตอบเป็น JSON เท่านั้น และห้ามแนะนำวิชาแบบฝืนเดา
ให้ตอบด้วยโครงสร้างนี้:
{{
  "summary": "ยังไม่สามารถแนะนำวิชาได้อย่างมั่นใจ",
  "target_career": "ยังไม่ชัดเจน",
  "selected_course_indexes": [],
  "learning_order_indexes": [],
  "career_paths": [],
  "note": "{suggestion or 'กรุณาระบุสายงาน ทักษะ หรือความสนใจให้ชัดขึ้น'}"
}}
""".strip()

    return f"""
สาขา: {department_clean}
คำถามของผู้ใช้: {user_query_clean}
จำนวนวิชาสูงสุดที่อนุญาตให้แนะนำ: 5

ข้อมูลรายวิชาที่ค้นเจอ:
{context}

ข้อกำชับเพิ่มเติม:
- ให้ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอื่นใด ๆ
- ใช้เฉพาะ index ของวิชาที่มีอยู่ใน context เท่านั้น
- ห้ามแปลชื่อวิชา
- ห้ามใช้ single quotes และห้ามใช้ code fence
- ถ้ามีวิชาที่เกี่ยวข้องเพียงพอ ให้เลือก 5 index
- สำหรับคำถามกว้าง ๆ ให้เน้นวิชาพื้นฐานที่ต่อยอดได้หลายสายก่อน
- learning_order_indexes ต้องเป็นลำดับที่สัมพันธ์กับวิชาที่เลือกจริง
- ถ้าข้อมูลยังไม่พอ ห้ามเดา ให้ตอบว่าควรถามใหม่อย่างไร
- ส่งกลับเป็น JSON object เดียวเท่านั้น
""".strip()


def build_messages(
    user_query: str,
    department: str,
    courses: List[Dict[str, Any]],
    max_courses: int = 5,
) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT_TH},
        {
            "role": "user",
            "content": build_user_prompt(
                user_query=user_query,
                department=department,
                courses=courses,
                max_courses=max_courses,
            ),
        },
    ]