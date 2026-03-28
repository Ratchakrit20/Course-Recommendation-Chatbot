from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

CHROMA_DIR = r"C:\Users\prad.R\Documents\ChatBot\course-chatbot\server-ai\chroma_db2"
COLLECTION_NAME = "kmutnb_courses"
EMBED_MODEL = "nomic-embed-text-v2-moe"

def main():
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    query = "อยากเป็น Data Analyst ต้องเรียนวิชาอะไรบ้าง"
    results = db.similarity_search_with_score(query, k=5)

    for i, (doc, score) in enumerate(results, start=1):
        print("=" * 100)
        print(f"Result #{i}")
        print("Score:", score)
        print("Course code:", doc.metadata.get("course_code"))
        print("Course TH:", doc.metadata.get("course_name_th"))
        print("Course EN:", doc.metadata.get("course_name_en"))
        print("Program:", doc.metadata.get("program"))
        print("Category:", doc.metadata.get("category"))
        print("Primary roles:", doc.metadata.get("primary_roles"))
        print("Intent tags:", doc.metadata.get("intent_tags"))
        print("Search priority:", doc.metadata.get("search_priority"))
        print("Text:", doc.page_content[:600], "...")
        print()

if __name__ == "__main__":
    main()