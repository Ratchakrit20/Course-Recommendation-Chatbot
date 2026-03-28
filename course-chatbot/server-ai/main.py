import ast
import json
import logging
import re
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import DEFAULT_PROVIDER, DEFAULT_TOP_K
from schemas import (
    ChatRequest,
    ChatResponse,
    ChatMeta,
    CourseHit,
    RecommendedCourse,
)
from retriever import search_department
from query_utils import enhance_query
from prompt_builder import SYSTEM_PROMPT_TH, build_user_prompt
from llm_ollama import (
    chat_with_ollama,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaResponseError,
)
# from llm_hf import chat_with_hf

logger = logging.getLogger(__name__)

app = FastAPI(title="Course Recommendation Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "Course chatbot API is running",
    }


def _build_reason(course: dict, user_query: str) -> str:
    parts = []

    keywords = course.get("keywords") or []
    major_focus = course.get("major_focus") or []
    description = (course.get("description") or "").strip()

    if keywords:
        if isinstance(keywords, list):
            parts.append(f"คีย์เวิร์ดที่เกี่ยวข้อง: {', '.join(map(str, keywords[:3]))}")
        else:
            parts.append(f"คีย์เวิร์ดที่เกี่ยวข้อง: {keywords}")

    if major_focus:
        if isinstance(major_focus, list):
            parts.append(f"จุดเน้นของวิชา: {', '.join(map(str, major_focus[:2]))}")
        else:
            parts.append(f"จุดเน้นของวิชา: {major_focus}")

    if description:
        parts.append("มีเนื้อหาสอดคล้องกับคำถามของผู้ใช้")

    if not parts:
        parts.append(f"เกี่ยวข้องกับคำถาม '{user_query}' จากข้อมูลรายวิชา")

    return " | ".join(parts)


def _extract_answer_text(result: Any) -> str:
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        raise ValueError("LLM result does not contain valid content")

    if isinstance(result, str) and result.strip():
        return result.strip()

    raise ValueError("LLM returned empty answer")


def _extract_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise ValueError("LLM returned empty text")

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s*```$", "", text).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response does not contain a valid JSON object")

    candidate = text[start:end + 1].strip()

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    try:
        parsed = ast.literal_eval(candidate)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    raise ValueError("LLM returned invalid JSON/object")


def _safe_list_of_strings(value: Any, max_items: int = 5) -> List[str]:
    if not value:
        return []

    if isinstance(value, list):
        items: List[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                items.append(text)
        return items[:max_items]

    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []

    return []


def _safe_list_of_ints(value: Any, max_items: int = 3, max_index: int = 5) -> List[int]:
    if not value:
        return []

    results: List[int] = []

    if isinstance(value, list):
        for item in value:
            try:
                num = int(item)
            except (TypeError, ValueError):
                continue
            if 1 <= num <= max_index and num not in results:
                results.append(num)
        return results[:max_items]

    return []


def _normalize_match_level(rank: int) -> str:
    if rank == 1:
        return "สูง"
    if rank == 2:
        return "กลาง"
    return "พื้นฐาน"


def _build_recommendation_hits(courses: List[dict], user_query: str) -> List[CourseHit]:
    hits: List[CourseHit] = []

    for idx, c in enumerate(courses[:3], start=1):
        hits.append(
            CourseHit(
                course_code=str(c.get("course_code", "")).strip(),
                course_name_en=str(c.get("course_name_en", "")).strip(),
                course_name_th=str(c.get("course_name_th", "")).strip() or None,
                category=str(c.get("category", "")).strip() or None,
                reason=_build_reason(c, user_query),
                match_level=_normalize_match_level(idx),
                keywords=_safe_list_of_strings(c.get("keywords"), max_items=5),
                skills=_safe_list_of_strings(c.get("skills"), max_items=5),
            )
        )

    return hits


def _build_meta(req: ChatRequest, provider: str, llm_result: Any) -> ChatMeta:
    if isinstance(llm_result, dict):
        return ChatMeta(
            provider=provider,
            department=req.department,
            top_k=req.top_k or DEFAULT_TOP_K,
            model=str(llm_result.get("model", "")).strip() or None,
        )

    return ChatMeta(
        provider=provider,
        department=req.department,
        top_k=req.top_k or DEFAULT_TOP_K,
        model=None,
    )


def _parse_structured_response(raw_answer: str, max_index: int) -> Dict[str, Any]:
    try:
        parsed = _extract_json_object(raw_answer)
    except ValueError:
        logger.warning("LLM did not return valid JSON, using fallback response")
        return {
            "summary": raw_answer.strip() if raw_answer.strip() else "ข้อมูลไม่เพียงพอสำหรับสรุปอย่างมั่นใจ",
            "target_career": "ยังไม่ชัดเจน",
            "selected_course_indexes": [],
            "learning_order_indexes": [],
            "career_paths": [],
            "note": "โมเดลไม่ได้ส่ง JSON ที่สมบูรณ์ ระบบจึงใช้ข้อความดิบแทน",
        }

    return {
        "summary": str(parsed.get("summary", "")).strip() or "ข้อมูลไม่เพียงพอสำหรับสรุปอย่างมั่นใจ",
        "target_career": str(parsed.get("target_career", "")).strip() or "ยังไม่ชัดเจน",
        "selected_course_indexes": _safe_list_of_ints(parsed.get("selected_course_indexes"), max_items=5, max_index=max_index),
        "learning_order_indexes": _safe_list_of_ints(parsed.get("learning_order_indexes"), max_items=5, max_index=max_index),
        "career_paths": _safe_list_of_strings(parsed.get("career_paths"), max_items=5),
        "note": str(parsed.get("note", "")).strip(),
    }


def _course_display_name(course: dict) -> str:
    name_th = str(course.get("course_name_th", "")).strip()
    name_en = str(course.get("course_name_en", "")).strip()
    return name_th or name_en or "ไม่ระบุชื่อวิชา"


def _fallback_summary(req: ChatRequest, courses: List[dict]) -> str:
    names = [_course_display_name(c) for c in courses[:2]]
    if names:
        return f"จากคำถามของผู้ใช้ ระบบพบรายวิชาที่เกี่ยวข้อง เช่น {', '.join(names)} ซึ่งอาจใช้เป็นจุดเริ่มต้นในการวางแผนการเรียนได้"
    return "ระบบพบรายวิชาที่เกี่ยวข้องเบื้องต้นสำหรับคำถามนี้"


def _fallback_target(req: ChatRequest) -> str:
    q = req.query.lower()
    if "data" in q or "ข้อมูล" in q or "สถิติ" in q:
        return "สายข้อมูลและการวิเคราะห์"
    if "web" in q or "เว็บ" in q:
        return "สายพัฒนาเว็บและซอฟต์แวร์"
    if "ai" in q or "machine learning" in q:
        return "สายปัญญาประดิษฐ์และข้อมูล"
    return "สายงานที่เกี่ยวข้องกับสาขาที่เลือก"


def _build_recommended_courses_from_indexes(
    courses: List[dict],
    selected_indexes: List[int],
    user_query: str,
) -> List[RecommendedCourse]:
    if not selected_indexes:
        selected_indexes = list(range(1, min(len(courses), 5) + 1))

    results: List[RecommendedCourse] = []

    for rank, course_idx in enumerate(selected_indexes[:5], start=1):
        actual_index = course_idx - 1
        if actual_index < 0 or actual_index >= len(courses):
            continue

        course = courses[actual_index]
        next_hint = ""
        recommended_next = course.get("recommended_next") or []
        if isinstance(recommended_next, list) and recommended_next:
            next_hint = f"อาจต่อยอดไปยัง {', '.join(map(str, recommended_next[:2]))}"
        elif rank == 1:
            next_hint = "ควรเริ่มจากวิชานี้ก่อนเพื่อปูพื้นฐาน"
        elif rank == 2:
            next_hint = "เหมาะเรียนต่อหลังจากมีพื้นฐานจากวิชาก่อนหน้า"
        else:
            next_hint = "ใช้ต่อยอดหลังจากเข้าใจพื้นฐานหลักแล้ว"

        results.append(
            RecommendedCourse(
                rank=rank,
                course_code=str(course.get("course_code", "")).strip(),
                course_name=_course_display_name(course),
                match_level=_normalize_match_level(rank),
                reason=_build_reason(course, user_query),
                skills=_safe_list_of_strings(course.get("skills"), max_items=5),
                recommended_before_after=next_hint,
            )
        )

    return results


def _build_learning_order_from_indexes(courses: List[dict], indexes: List[int]) -> List[str]:
    results: List[str] = []

    for idx in indexes[:5]:
        actual_index = idx - 1
        if 0 <= actual_index < len(courses):
            results.append(_course_display_name(courses[actual_index]))

    return results


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        provider = (req.provider or DEFAULT_PROVIDER).lower()
        # if provider not in {"ollama", "hf"}:
        #     raise HTTPException(status_code=400, detail="provider ต้องเป็น ollama หรือ hf")
        # provider = (req.provider or DEFAULT_PROVIDER).lower()
        if provider != "ollama":
            provider = "ollama"

        top_k = req.top_k or DEFAULT_TOP_K
        enhanced_query = enhance_query(req.query, req.department)

        # courses = search_department(req.department, enhanced_query, k=top_k)
        
        courses = search_department(
            department=req.department,
            query=enhanced_query,
            original_query=req.query,
            k=top_k,
        )
        if not courses:
            raise HTTPException(status_code=404, detail="ไม่พบรายวิชาที่เกี่ยวข้อง")

        user_prompt = build_user_prompt(
            user_query=req.query,
            department=req.department,
            courses=courses,
            max_courses=top_k,
        )

        # if provider == "ollama":
        #     llm_result = chat_with_ollama(SYSTEM_PROMPT_TH, user_prompt)
        # else:
        #     llm_result = chat_with_hf(SYSTEM_PROMPT_TH, user_prompt)
        llm_result = chat_with_ollama(SYSTEM_PROMPT_TH, user_prompt)
        raw_answer = _extract_answer_text(llm_result)
        parsed = _parse_structured_response(raw_answer, max_index=len(courses))

        selected_indexes = parsed.get("selected_course_indexes") or []
        learning_order_indexes = parsed.get("learning_order_indexes") or selected_indexes

        recommended_courses = _build_recommended_courses_from_indexes(
            courses,
            selected_indexes,
            req.query,
        )
        recommendations = _build_recommendation_hits(courses, req.query)

        summary = parsed["summary"].strip() if parsed["summary"].strip() else _fallback_summary(req, courses)
        target_career = parsed["target_career"].strip() if parsed["target_career"].strip() else _fallback_target(req)
        learning_order = _build_learning_order_from_indexes(courses, learning_order_indexes)
        career_paths = parsed["career_paths"]

        if not recommended_courses:
            recommended_courses = _build_recommended_courses_from_indexes(courses, [], req.query)

        if not learning_order:
            learning_order = [_course_display_name(c) for c in courses[:3]]

        if not career_paths:
            career_paths = [_fallback_target(req)]

        return ChatResponse(
            summary=summary,
            target_career=target_career,
            recommended_courses=recommended_courses,
            learning_order=learning_order,
            career_paths=career_paths,
            note=parsed["note"],
            recommendations=recommendations,
            meta=_build_meta(req, provider, llm_result),
            answer_raw=raw_answer,
        )

    except HTTPException:
        raise
    except FileNotFoundError as exc:
        logger.exception("Required file not found")
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OllamaTimeoutError:
        raise HTTPException(status_code=504, detail="Ollama ใช้เวลาตอบนานเกินกำหนด")
    except OllamaConnectionError:
        raise HTTPException(status_code=502, detail="ไม่สามารถเชื่อมต่อ Ollama ได้")
    except OllamaResponseError:
        raise HTTPException(status_code=502, detail="Ollama ตอบกลับผิดรูปแบบหรือเกิดข้อผิดพลาด")
    except ValueError as exc:
        logger.exception("Invalid LLM output")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unhandled server error")
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบ")