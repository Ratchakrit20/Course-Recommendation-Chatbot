KMUTNB Courses RAG-Ready Final

Recommended ingest:
- Use kmutnb_courses_rag_ready_final.jsonl
- One line = one course
- Embed only `retrieval_text`
- Store metadata:
  program, category, primary_roles, intent_tags, search_priority, course_code

Suggested retrieval pipeline:
1) Vector search top_k = 12
2) Filter by program if the user specifies a major
3) Rerank by:
   final_score = vector_score + 0.15*search_priority + 0.10*max(role_relevance_scores)
4) Summarize top 5-8 courses

Important:
- `intent_tags`, `primary_roles`, `role_relevance_scores` were generated heuristically.
- They are suitable for testing/demo and can be refined manually later.
