export type Provider = "ollama" | "hf";

export type ChatRequest = {
  department: string;
  query: string;
  provider?: Provider;
  top_k?: number;
};

export type CourseHit = {
  course_code: string;
  course_name_en: string;
  course_name_th?: string;
  category?: string;
  reason: string;
  match_level?: string;
  keywords?: string[];
  skills?: string[];
};

export type RecommendedCourse = {
  rank: number;
  course_code: string;
  course_name: string;
  match_level: "สูง" | "กลาง" | "พื้นฐาน" | string;
  reason: string;
  skills: string[];
  recommended_before_after: string;
};

export type ChatMeta = {
  provider?: string;
  department?: string;
  top_k?: number;
  model?: string;
};

export type ChatResponse = {
  summary: string;
  target_career: string;
  recommended_courses: RecommendedCourse[];
  learning_order: string[];
  career_paths: string[];
  note: string;

  recommendations: CourseHit[];
  meta?: ChatMeta;
  answer_raw?: string;
};