from typing import Dict, List, Optional


# -----------------------------
# Global career / skill mapping
# ใช้ได้ข้ามสาขา
# -----------------------------
GLOBAL_QUERY_MAP: Dict[str, List[str]] = {
    # Computer / software / data
    "เขียนโปรแกรม": ["programming", "software development", "algorithm", "coding"],
    "โปรแกรมเมอร์": ["programming", "software development", "algorithm", "coding"],
    "software engineer": ["software engineering", "programming", "system design", "testing", "requirement"],
    "นักพัฒนาซอฟต์แวร์": ["software development", "programming", "system design", "testing"],
    "พัฒนาเว็บ": ["web development", "web framework", "frontend", "backend", "api"],
    "ทำเว็บ": ["web development", "web framework", "frontend", "backend", "api"],
    "web developer": ["web development", "web framework", "frontend", "backend", "api"],
    "frontend": ["frontend", "ui", "javascript", "web development", "user interface"],
    "frontend developer": ["frontend", "ui", "javascript", "web development", "user interface"],
    "backend": ["backend", "api", "database", "server", "web framework"],
    "backend developer": ["backend", "api", "database", "server", "web framework"],
    "full stack": ["frontend", "backend", "database", "web development", "api"],
    "full stack developer": ["frontend", "backend", "database", "web development", "api"],
    "data analyst": ["data analysis", "statistics", "dashboard", "sql", "python", "reporting"],
    "นักวิเคราะห์ข้อมูล": ["data analysis", "statistics", "dashboard", "sql", "python", "reporting"],
    "data scientist": ["data science", "machine learning", "statistics", "python", "modeling"],
    "นักวิทยาศาสตร์ข้อมูล": ["data science", "machine learning", "statistics", "python", "modeling"],
    "data engineer": ["data engineering", "etl", "pipeline", "database", "big data", "data warehouse"],
    "วิศวกรข้อมูล": ["data engineering", "etl", "pipeline", "database", "big data", "data warehouse"],
    "ai": ["artificial intelligence", "machine learning", "neural network", "intelligent system"],
    "machine learning": ["machine learning", "classification", "clustering", "neural network", "model"],
    "ai engineer": ["artificial intelligence", "machine learning", "ai application", "model deployment"],
    "ml engineer": ["machine learning", "model deployment", "python", "data pipeline", "ai system"],
    "devops": ["devops", "cloud", "deployment", "automation", "container", "ci cd"],
    "cloud": ["cloud", "deployment", "distributed system", "infrastructure", "virtualization"],
    "cybersecurity": ["security", "network security", "cryptography", "system security", "forensics"],
    "security": ["security", "network security", "cryptography", "system security", "forensics"],
    "ui": ["user interface", "interaction design", "frontend", "usability"],
    "ux": ["user experience", "human computer interaction", "usability", "interaction design"],
    "ui ux": ["user interface", "user experience", "human computer interaction", "usability"],
    "designer": ["user interface", "user experience", "interaction design", "usability"],
    "qa": ["software testing", "quality assurance", "test case", "verification"],
    "tester": ["software testing", "quality assurance", "test case", "verification"],
    "mobile developer": ["mobile development", "application development", "ui", "software development"],
    "game developer": ["game development", "programming", "graphics", "interactive media"],
    "blockchain": ["blockchain", "distributed system", "smart contract", "cryptography"],
    "web3": ["blockchain", "smart contract", "distributed system", "cryptography"],

    # Quant / Math / Statistics
    "quant": ["quantitative analysis", "probability", "optimization", "mathematical modeling"],
    "quantitative analyst": ["quantitative analysis", "probability", "optimization", "mathematical modeling"],
    "operations research": ["operations research", "optimization", "mathematical modeling", "computation"],
    "statistician": ["statistics", "statistical analysis", "probability", "inference", "forecasting"],
    "business analyst": ["business analysis", "statistics", "data analysis", "decision making", "forecasting"],
    "research analyst": ["research", "statistical analysis", "data analysis", "inference"],

    # Actuarial / insurance
    "actuarial": ["actuarial science", "insurance", "risk management", "probability", "loss modeling"],
    "actuary": ["actuarial science", "insurance", "risk management", "probability", "loss modeling"],
    "นักคณิตศาสตร์ประกันภัย": ["actuarial science", "insurance", "risk management", "probability", "loss modeling"],
    "ประกันภัย": ["insurance", "actuarial science", "risk management", "probability", "underwriting"],
    "risk analyst": ["risk management", "insurance", "probability", "forecasting", "decision theory"],
    "underwriting": ["underwriting", "insurance", "risk management", "probability"],

    # Biotechnology / lab / food / environment / health-beauty
    "biotechnology": ["biotechnology", "microbiology", "genetics", "biochemistry", "bioindustry"],
    "ชีวภาพ": ["biotechnology", "microbiology", "genetics", "biochemistry", "bioindustry"],
    "จุลชีววิทยา": ["microbiology", "biotechnology", "genetics", "laboratory"],
    "genetics": ["genetics", "molecular biology", "biotechnology", "laboratory"],
    "laboratory": ["laboratory", "practical skills", "analysis", "quality control"],
    "ห้องแล็บ": ["laboratory", "practical skills", "analysis", "quality control"],
    "food science": ["food science", "food technology", "food chemistry", "food microbiology", "food processing"],
    "อาหาร": ["food science", "food technology", "food chemistry", "food microbiology", "food processing"],
    "food safety": ["food safety", "quality assurance", "food microbiology", "food processing"],
    "qa": ["quality assurance", "quality control", "analysis", "laboratory"],
    "quality control": ["quality control", "analysis", "laboratory", "quality assurance"],
    "product development": ["product development", "innovation", "quality assurance", "applied science"],
    "สิ่งแวดล้อม": ["environmental science", "environmental technology", "ecology", "waste management", "sustainability"],
    "environment": ["environmental science", "environmental technology", "ecology", "waste management", "sustainability"],
    "sustainability": ["sustainability", "resource management", "environmental analysis", "impact assessment"],
    "pollution": ["pollution control", "environmental analysis", "waste management", "ecology"],
    "สุขภาพและความงาม": ["health and beauty", "cosmetic science", "product development", "quality control", "chemistry"],
    "cosmetic": ["cosmetic science", "health product", "product development", "quality control", "chemistry"],
    "เครื่องสำอาง": ["cosmetic science", "health product", "product development", "quality control", "chemistry"],
}


# -----------------------------
# Department-specific hints
# อิงจาก program_profile / career_tags / domain_keywords ในไฟล์ JSON
# -----------------------------
DEPARTMENT_HINTS: Dict[str, Dict[str, List[str]]] = {
    "CS": {
        "program": [
            "computer science",
            "software development",
            "programming",
            "algorithm",
            "data structure",
            "database",
            "web development",
            "artificial intelligence",
            "machine learning",
        ],
        "careers": [
            "software developer",
            "software engineer",
            "web developer",
            "ai engineer",
            "data scientist",
            "it professional",
        ],
        "intents": [
            "เขียนโปรแกรม",
            "ทำเว็บ",
            "พัฒนาเว็บ",
            "ai",
            "machine learning",
            "database",
            "algorithm",
        ],
    },
    "AM": {
        "program": [
            "applied mathematics",
            "mathematical modeling",
            "numerical methods",
            "differential equations",
            "linear algebra",
            "optimization",
            "computation",
            "quantitative analysis",
            "proof",
            "analysis",
        ],
        "careers": [
            "quantitative analyst",
            "data analyst",
            "researcher",
            "mathematics teacher",
            "operations research analyst",
        ],
        "intents": [
            "ชอบคณิตศาสตร์",
            "สมการ",
            "การคำนวณ",
            "numerical",
            "optimization",
            "mathematical modeling",
            "quantitative",
        ],
    },
    "AS": {
        "program": [
            "applied statistics",
            "statistical analysis",
            "probability",
            "forecasting",
            "regression",
            "sampling",
            "experimental design",
            "inference",
            "data analysis",
            "statistical computing",
        ],
        "careers": [
            "statistician",
            "data analyst",
            "business analyst",
            "research analyst",
            "data scientist",
        ],
        "intents": [
            "วิเคราะห์ข้อมูลเชิงสถิติ",
            "สถิติ",
            "พยากรณ์",
            "regression",
            "probability",
            "sampling",
            "hypothesis testing",
        ],
    },
    "ASB": {
        "program": [
            "actuarial science",
            "business statistics",
            "insurance",
            "risk management",
            "probability",
            "stochastic processes",
            "forecasting",
            "decision theory",
            "financial mathematics",
            "loss modeling",
        ],
        "careers": [
            "actuarial analyst",
            "risk analyst",
            "business analyst",
            "data analyst",
            "underwriting analyst",
        ],
        "intents": [
            "ประกันภัย",
            "risk",
            "actuarial",
            "insurance",
            "underwriting",
            "forecasting",
        ],
    },
    "BT": {
        "program": [
            "biotechnology",
            "microbiology",
            "genetics",
            "biochemistry",
            "molecular biology",
            "bioprocess",
            "fermentation",
            "cell culture",
            "laboratory",
            "bioindustry",
        ],
        "careers": [
            "biotechnology researcher",
            "quality control scientist",
            "product development scientist",
            "production supervisor",
            "food biotechnologist",
        ],
        "intents": [
            "biotechnology",
            "biology",
            "microbiology",
            "genetics",
            "laboratory",
            "fermentation",
            "bio",
        ],
    },
    "EST": {
        "program": [
            "environmental science",
            "environmental technology",
            "ecology",
            "waste management",
            "pollution control",
            "environmental analysis",
            "environmental microbiology",
            "resource management",
            "sustainability",
            "impact assessment",
        ],
        "careers": [
            "environmental scientist",
            "environmental analyst",
            "environmental officer",
            "sustainability officer",
            "wastewater analyst",
        ],
        "intents": [
            "สิ่งแวดล้อม",
            "การจัดการทรัพยากร",
            "pollution",
            "waste",
            "ecology",
            "environmental management",
            "conservation",
        ],
    },
    "FST": {
        "program": [
            "food science",
            "food technology",
            "food chemistry",
            "food microbiology",
            "food processing",
            "food safety",
            "quality assurance",
            "food engineering",
            "product development",
            "sensory evaluation",
        ],
        "careers": [
            "food scientist",
            "quality assurance officer",
            "food technologist",
            "product developer",
            "food engineer",
        ],
        "intents": [
            "อาหาร",
            "พัฒนาผลิตภัณฑ์อาหาร",
            "food safety",
            "food processing",
            "food chemistry",
            "food microbiology",
            "qa",
        ],
    },
    "HBS": {
        "program": [
            "health and beauty science",
            "cosmetic science",
            "chemistry",
            "laboratory",
            "quality control",
            "product development",
            "health product",
            "cosmeceutical",
            "regulatory affairs",
            "emulsion science",
        ],
        "careers": [
            "cosmetic scientist",
            "health product researcher",
            "quality control scientist",
            "product development scientist",
            "health and beauty entrepreneur",
        ],
        "intents": [
            "เครื่องสำอาง",
            "cosmetic",
            "สุขภาพและความงาม",
            "quality control",
            "product development",
            "chemistry",
            "health product",
        ],
    },
    "MC": {
        "program": [
            "mathematics with computer science",
            "data science",
            "mathematical modeling",
            "computation",
            "optimization",
            "software development",
            "systems analysis",
            "business intelligence",
            "data analytics",
        ],
        "careers": [
            "data scientist",
            "software developer",
            "systems analyst",
            "business intelligence analyst",
            "research assistant",
        ],
        "intents": [
            "ชอบคณิตและคอม",
            "data science",
            "business intelligence",
            "software developer",
            "systems analyst",
            "optimization",
        ],
    },
    "MCS": {  # เผื่อใช้ code นี้แทน MC
        "program": [
            "mathematics with computer science",
            "data science",
            "mathematical modeling",
            "computation",
            "optimization",
            "software development",
            "systems analysis",
            "business intelligence",
            "data analytics",
        ],
        "careers": [
            "data scientist",
            "software developer",
            "systems analyst",
            "business intelligence analyst",
            "research assistant",
        ],
        "intents": [
            "ชอบคณิตและคอม",
            "data science",
            "business intelligence",
            "software developer",
            "systems analyst",
            "optimization",
        ],
    },
    "SDA": {
        "program": [
            "statistical data science",
            "analytics",
            "probability",
            "statistics theory",
            "data analysis",
            "machine learning",
            "optimization",
            "business intelligence",
            "analytics engineering",
        ],
        "careers": [
            "data analyst",
            "data scientist",
            "business intelligence analyst",
            "analytics engineer",
            "quantitative analyst",
        ],
        "intents": [
            "analytics",
            "data science",
            "probability",
            "statistics",
            "machine learning",
            "business intelligence",
            "dashboard",
        ],
    },
}


# -----------------------------
# Generic hint words
# ใช้ช่วยดึง intent จากคำถามทั่วไป
# -----------------------------
GENERIC_HINTS: Dict[str, List[str]] = {
    "web": ["web development", "web framework", "frontend", "backend", "api"],
    "เว็บไซต์": ["web development", "web framework", "frontend", "backend", "api"],
    "frontend": ["frontend", "ui", "web development", "user interface"],
    "backend": ["backend", "api", "database", "server"],
    "database": ["database", "sql", "data modeling"],
    "ฐานข้อมูล": ["database", "sql", "data modeling"],
    "data": ["data analysis", "database", "statistics", "sql"],
    "ข้อมูล": ["data analysis", "database", "statistics", "sql"],
    "python": ["python", "programming"],
    "api": ["api", "backend", "web framework"],
    "ai": ["artificial intelligence", "machine learning"],
    "ml": ["machine learning", "classification", "model"],
    "lab": ["laboratory", "analysis", "practical skills"],
    "แล็บ": ["laboratory", "analysis", "practical skills"],
    "วิจัย": ["research", "analysis", "laboratory"],
    "research": ["research", "analysis", "laboratory"],
    "คุณภาพ": ["quality control", "quality assurance", "analysis"],
    "quality": ["quality control", "quality assurance", "analysis"],
    "พยากรณ์": ["forecasting", "regression", "statistics"],
    "optimization": ["optimization", "mathematical modeling", "computation"],
    "สมการ": ["equations", "mathematical modeling", "analysis"],
    "สิ่งแวดล้อม": ["environmental science", "sustainability", "waste management"],
    "อาหาร": ["food science", "food technology", "food safety"],
    "เครื่องสำอาง": ["cosmetic science", "product development", "quality control"],
    "ประกัน": ["insurance", "risk management", "probability"],
}


def _clean_query(text: str) -> str:
    return " ".join((text or "").strip().split())


def _extend_unique(target: List[str], seen: set, terms: List[str], query_lower: str) -> None:
    for term in terms:
        term_clean = _clean_query(term)
        key = term_clean.lower()
        if key and key not in seen and key not in query_lower:
            seen.add(key)
            target.append(term_clean)


def enhance_query(query: str, department: Optional[str] = None) -> str:
    query = _clean_query(query)
    if not query:
        return ""

    q_lower = query.lower()
    expansions: List[str] = []
    seen = set()

    # 1) ขยายจาก global map
    for trigger, related_terms in GLOBAL_QUERY_MAP.items():
        if trigger.lower() in q_lower:
            _extend_unique(expansions, seen, related_terms, q_lower)

    # 2) ขยายจาก generic hints
    for trigger, related_terms in GENERIC_HINTS.items():
        if trigger.lower() in q_lower:
            _extend_unique(expansions, seen, related_terms, q_lower)

    # 3) ถ้าระบุสาขา ให้เติมคำของสาขานั้นเพิ่ม
    dept = (department or "").strip().upper()
    dept_profile = DEPARTMENT_HINTS.get(dept)
    if dept_profile:
        dept_terms: List[str] = []
        dept_terms.extend(dept_profile.get("program", []))
        dept_terms.extend(dept_profile.get("careers", []))

        # เพิ่ม intent ของสาขาเมื่อ query มีความเกี่ยวข้องบางส่วน
        matched_intent = False
        for intent in dept_profile.get("intents", []):
            if intent.lower() in q_lower:
                matched_intent = True
                break

        # ถ้าถามกว้าง ๆ แต่เลือกสาขาแล้ว ก็ยังควรเติมคำหลักของสาขา
        if matched_intent or len(q_lower.split()) <= 12:
            _extend_unique(expansions, seen, dept_terms, q_lower)

    if not expansions:
        return query

    return f"{query} {' '.join(expansions)}"