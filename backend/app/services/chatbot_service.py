"""
Chatbot TF-IDF service using local corpus.json.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.ecg import PracticeAttempt, PracticeQuestion

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatbotService:
    """Loads corpus and provides TF-IDF similarity search."""

    _corpus: list[dict] = []
    _vector_index: dict[int, dict[str, float]] = {}
    _doc_frequency: dict[str, int] = {}
    _initialized: bool = False

    @staticmethod
    def _normalize(text: str) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize("NFD", text.lower())
        normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    @classmethod
    def _tokenize(cls, text: str) -> list[str]:
        return [token for token in cls._normalize(text).split(" ") if len(token) > 2]

    @classmethod
    def _corpus_path(cls) -> Path:
        # backend/app/services/chatbot_service.py -> backend/scripts/corpus.json
        return Path(__file__).resolve().parents[2] / "scripts" / "corpus.json"

    @classmethod
    def initialize(cls) -> None:
        """Load corpus and build vector index once."""
        if cls._initialized:
            return

        corpus_path = cls._corpus_path()
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

        with open(corpus_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        corpus = payload.get("corpus", [])
        if not isinstance(corpus, list) or not corpus:
            raise ValueError("Invalid or empty corpus in corpus.json")

        cls._corpus = corpus
        cls._build_index()
        cls._initialized = True
        logger.info("Chatbot corpus initialized with %s items", len(cls._corpus))

    @classmethod
    def _build_index(cls) -> None:
        doc_count = len(cls._corpus)
        doc_frequency: dict[str, int] = {}

        for doc in cls._corpus:
            combined_text = f"{doc.get('pregunta', '')} {doc.get('respuesta', '')}"
            unique_tokens = set(cls._tokenize(combined_text))
            for token in unique_tokens:
                doc_frequency[token] = doc_frequency.get(token, 0) + 1

        vector_index: dict[int, dict[str, float]] = {}
        for doc in cls._corpus:
            doc_id = int(doc.get("id"))
            tokens = cls._tokenize(f"{doc.get('pregunta', '')} {doc.get('respuesta', '')}")
            term_frequency: dict[str, int] = {}
            for token in tokens:
                term_frequency[token] = term_frequency.get(token, 0) + 1

            vector: dict[str, float] = {}
            for token, freq in term_frequency.items():
                idf = math.log(doc_count / max(doc_frequency.get(token, 1), 1))
                vector[token] = float(freq) * idf
            vector_index[doc_id] = vector

        cls._doc_frequency = doc_frequency
        cls._vector_index = vector_index

    @staticmethod
    def _cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
        if not vec1 or not vec2:
            return 0.0

        keys = set(vec1.keys()) | set(vec2.keys())
        dot_product = 0.0
        mag1 = 0.0
        mag2 = 0.0

        for key in keys:
            v1 = vec1.get(key, 0.0)
            v2 = vec2.get(key, 0.0)
            dot_product += v1 * v2
            mag1 += v1 * v1
            mag2 += v2 * v2

        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        return dot_product / (math.sqrt(mag1) * math.sqrt(mag2))

    @classmethod
    def search(cls, query: str, top_k: int = 1) -> list[dict]:
        """Return top_k corpus items ranked by cosine similarity."""
        cls.initialize()

        tokens = cls._tokenize(query)
        if not tokens:
            return []

        query_vector: dict[str, float] = {}
        for token in tokens:
            query_vector[token] = query_vector.get(token, 0.0) + 1.0

        scores: list[dict] = []
        for doc in cls._corpus:
            doc_id = int(doc.get("id"))
            doc_vector = cls._vector_index.get(doc_id, {})
            score = cls._cosine_similarity(query_vector, doc_vector)
            if score > 0:
                scores.append(
                    {
                        "id": doc_id,
                        "categoria": str(doc.get("categoria", "")),
                        "pregunta": str(doc.get("pregunta", "")),
                        "respuesta": str(doc.get("respuesta", "")),
                        "score": float(score),
                    }
                )

        scores.sort(key=lambda item: item["score"], reverse=True)
        return scores[:top_k]

    @classmethod
    def get_source_by_id(cls, source_id: int) -> dict | None:
        """Get a source item by id from corpus."""
        cls.initialize()
        for doc in cls._corpus:
            if int(doc.get("id", -1)) == source_id:
                return {
                    "id": int(doc.get("id")),
                    "categoria": str(doc.get("categoria", "")),
                    "pregunta": str(doc.get("pregunta", "")),
                    "respuesta": str(doc.get("respuesta", "")),
                    "score": 1.0,
                }
        return None

    @staticmethod
    def get_recent_error_topics(db: Session, user_id: int, limit: int = 5) -> list[str]:
        """Return latest weak topics from incorrect practice attempts."""
        attempts = (
            db.query(PracticeAttempt, PracticeQuestion)
            .join(PracticeQuestion, PracticeAttempt.question_id == PracticeQuestion.id)
            .filter(PracticeAttempt.user_id == user_id)
            .filter(PracticeAttempt.is_correct == "False")
            .order_by(desc(PracticeAttempt.created_at))
            .limit(limit)
            .all()
        )

        topics: list[str] = []
        seen: set[str] = set()
        for _, question in attempts:
            topic = str(question.correct_class or "").strip()
            if topic and topic not in seen:
                seen.add(topic)
                topics.append(topic)
        return topics

    @staticmethod
    def compose_personalized_answer(
        base_answer: str,
        skill_level: int | None,
        recent_error_topics: list[str],
    ) -> str:
        """Add concise personalization to corpus response."""
        if not base_answer:
            return base_answer

        level_hint = ""
        if skill_level is not None:
            if skill_level <= 2:
                level_hint = "\n\nEnfoque sugerido: repasa primero criterios básicos de identificación en ECG (ritmo, frecuencia, QRS y ondas P)."
            elif skill_level >= 4:
                level_hint = "\n\nEnfoque sugerido: contrasta este patrón con diagnósticos diferenciales y criterios de urgencia."

        topics_hint = ""
        if recent_error_topics:
            pretty_topics = ", ".join(t.replace("_", " ") for t in recent_error_topics[:3])
            topics_hint = f"\n\nTemas a reforzar según tu práctica reciente: {pretty_topics}."

        return f"{base_answer}{level_hint}{topics_hint}".strip()
