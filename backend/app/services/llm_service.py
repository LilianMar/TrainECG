"""
LLM Service - Handles interactions with OpenAI's ChatGPT API.
"""

from typing import List
import openai
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMService:
    """Service for generating recommendations using ChatGPT."""

    @staticmethod
    def initialize_openai():
        """Initialize OpenAI client."""
        if settings.LLM_API_KEY:
            openai.api_key = settings.LLM_API_KEY
        else:
            logger.warning("LLM_API_KEY not configured. ChatGPT recommendations will not work.")

    @staticmethod
    def generate_recommendations(
        wrong_questions: List[dict],
        skill_level: int,
        previous_level: int | None = None,
    ) -> dict:
        """
        Generate learning recommendations based on wrong answers.

        Args:
            wrong_questions: List of questions answered incorrectly with metadata
            skill_level: Current skill level (1-5)
            previous_level: Previous skill level before test (for progress tracking)

        Returns:
            Dict with recommendations, arrhythmia focus areas, and study suggestions
        """
        if not settings.LLM_API_KEY:
            logger.warning("LLM_API_KEY not configured. Using fallback recommendations.")
            return LLMService._fallback_recommendations(
                wrong_questions, skill_level, previous_level
            )

        try:
            # Prepare context from wrong questions
            arrhythmia_classes = [q.get("correct_class", "unknown") for q in wrong_questions]
            question_texts = [q.get("question_text", "") for q in wrong_questions]

            prompt = f"""
Eres un experto cardiólogo y educador médico. Un estudiante de ECG ha completado un test de evaluación.

CONTEXTO DEL ESTUDIANTE:
- Nivel de habilidad actual: {skill_level}/5
- Nivel anterior: {previous_level}/5 {"(Progreso)" if previous_level and previous_level < skill_level else "(Sin cambio)"}
- Preguntas incorrectas: {len(wrong_questions)}/{len(wrong_questions) + 5}  # Suma variable según test

ÁREAS DE DIFICULTAD (Arritmias):
{", ".join(set(arrhythmia_classes))}

PREGUNTAS FALLIDAS:
{chr(10).join([f"- {q}" for q in question_texts[:5]])}  # Limitar a 5 para brevedad

Por favor, proporciona:
1. **Análisis**: ¿Qué patrones ves en los errores?
2. **Áreas de Refuerzo**: Top 3 temas específicos para estudiar
3. **Recomendaciones de Estudio**: Sugerencias prácticas y materiales de referencia
4. **Próximos Pasos**: Plan de acción para mejorar

Sé conciso, práctico y ánima al estudiante. Responde en HTML simple (sin etiquetas html/body, solo divs y p).
"""

            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en educación médica especializado en ECC/ECG. Proporciona recomendaciones prácticas y motivadoras.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=1000,
            )

            recommendations_text = response.choices[0].message.content

            return {
                "success": True,
                "recommendations": recommendations_text,
                "arrhythmias_to_review": list(set(arrhythmia_classes)),
                "progress": {
                    "previous_level": previous_level,
                    "current_level": skill_level,
                    "improved": previous_level and skill_level > previous_level,
                },
            }

        except Exception as e:
            logger.error(f"Error generating recommendations with ChatGPT: {str(e)}")
            # Fallback to template-based recommendations
            return LLMService._fallback_recommendations(
                wrong_questions, skill_level, previous_level
            )

    @staticmethod
    def _fallback_recommendations(
        wrong_questions: List[dict],
        skill_level: int,
        previous_level: int | None = None,
    ) -> dict:
        """
        Fallback recommendations when LLM API is not available.
        """
        arrhythmia_classes = list(set([q.get("correct_class", "unknown") for q in wrong_questions]))

        level_suggestions = {
            1: "Revisa conceptos básicos de ECG: normal vs anormal, componentes del ECG.",
            2: "Enfócate en patrones comunes: FA, Flutter, ritmo sinusal normal.",
            3: "Estudia casos más complejos: bloques AV, taquicardias ventriculares.",
            4: "Profundiza en diagnósticos diferenciales y casos clínicos complejos.",
            5: "Mantén tu nivel revisando casos desafiantes y patrones raros.",
        }

        html_recommendations = f"""
<div style="margin: 20px 0;">
    <h3>📊 Análisis de tu Desempeño</h3>
    <p>Completaste el test con un nivel de habilidad de <strong>{skill_level}/5</strong>.</p>
    {f'<p style="color: green;"><strong>✓ ¡Progreso!</strong> Mejoraste desde nivel {previous_level}.</p>' if previous_level and skill_level > previous_level else ''}
    
    <h3>🎯 Áreas de Refuerzo</h3>
    <p>Necesitas revisar estos temas:</p>
    <ul>
        {''.join([f'<li>{arrhythmia.replace("_", " ").title()}</li>' for arrhythmia in arrhythmia_classes])}
    </ul>
    
    <h3>📚 Recomendaciones de Estudio</h3>
    <p>{level_suggestions.get(skill_level, level_suggestions[1])}</p>
    <ul>
        <li>Revisa los ejemplos de preguntas que contestaste mal</li>
        <li>Estudia casos similares en la biblioteca médica</li>
        <li>Practica con más ejemplos del nivel {skill_level}</li>
        <li>Intenta el test de evaluación nuevamente en 1 semana</li>
    </ul>
</div>
"""

        return {
            "success": True,
            "recommendations": html_recommendations,
            "arrhythmias_to_review": arrhythmia_classes,
            "progress": {
                "previous_level": previous_level,
                "current_level": skill_level,
                "improved": previous_level and skill_level > previous_level,
            },
        }
