"""
LLM Service - Handles interactions with OpenAI's ChatGPT API.
"""

from typing import List, Optional
from openai import OpenAI, APIError
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class LLMService:
    """Service for generating recommendations using ChatGPT."""

    @staticmethod
    def _ensure_client():
        """Ensure OpenAI client is initialized."""
        global client
        if not client and settings.OPENAI_API_KEY:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return client

    @staticmethod
    def generate_progress_recommendations(
        arrhythmia_performance: dict,
        test_attempts: int,
        accuracy: float,
        weak_areas: List[str],
        incorrect_answers: Optional[List[dict]] = None,
    ) -> str:
        """
        Generate personalized progress recommendations using GPT.
        
        Args:
            arrhythmia_performance: Dict with performance by arrhythmia type
            test_attempts: Number of tests completed
            accuracy: Overall accuracy percentage
            weak_areas: List of arrhythmia types with low accuracy
            incorrect_answers: List of incorrect answers with details
            
        Returns:
            HTML string with personalized recommendations
        """
        client_instance = LLMService._ensure_client()
        
        if not client_instance:
            logger.warning("OpenAI API key not configured. Using fallback recommendations.")
            return LLMService._fallback_progress_recommendations(
                arrhythmia_performance, test_attempts, accuracy, weak_areas, incorrect_answers
            )

        try:
            # Build performance summary
            performance_summary = "\n".join([
                f"- {arr.replace('_', ' ').title()}: {data.get('test_accuracy', 0):.1f}% en tests"
                for arr, data in arrhythmia_performance.items()
                if data.get('test_total', 0) > 0
            ])

            # Build incorrect answers summary
            incorrect_summary = ""
            if incorrect_answers:
                # Group by arrhythmia type
                errors_by_type = {}
                for answer in incorrect_answers:
                    arr_type = answer.get("correct_class", "unknown")
                    if arr_type not in errors_by_type:
                        errors_by_type[arr_type] = []
                    errors_by_type[arr_type].append(answer.get("question_text", ""))
                
                incorrect_summary = "\nPREGUNTAS QUE HA RESPONDIDO INCORRECTAMENTE:\n"
                for arr_type, questions in errors_by_type.items():
                    incorrect_summary += f"\n{arr_type.title()}:\n"
                    for q in questions[:3]:  # Limitar a 3 preguntas por tipo
                        if q:
                            incorrect_summary += f"  • {q[:100]}...\n"

            prompt = f"""Eres un cardiólogo educador especializado en formación de ECG. 
Un estudiante ha estado practicando y completó {test_attempts} tests con una precisión general del {accuracy:.1f}%.

DESEMPEÑO POR ARRITMIA:
{performance_summary if performance_summary else "Sin datos de tests aún"}

ÁREAS DE MEJORA IDENTIFICADAS:
{', '.join(weak_areas) if weak_areas else "Progreso consistente en todas las áreas"}
{incorrect_summary}

Por favor, proporciona recomendaciones ESPECÍFICAS y MOTIVADORAS basadas en los errores identificados para:
1. Conceptos clave a reforzar en las áreas débiles
2. Estrategias de estudio específicas para los tópicos problemáticos
3. Próximos pasos recomendados

Responde en HTML simple (divs y párrafos). Máximo 300 tokens. Sé conciso, práctico y motivador."""

            response = client_instance.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto cardiólogo educador. Proporciona recomendaciones prácticas, específicas y motivadoras basadas en los errores específicos del estudiante.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )

            return f"""
<div style="margin: 20px 0; padding: 15px; background: #f0f8ff; border-radius: 8px;">
    <h3>🎯 Recomendaciones Personalizadas</h3>
    {response.choices[0].message.content}
</div>
"""

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return LLMService._fallback_progress_recommendations(
                arrhythmia_performance, test_attempts, accuracy, weak_areas, incorrect_answers
            )

    @staticmethod
    def generate_ecg_explanation(
        predicted_class: str,
        confidence: float,
        affected_windows: int,
        user_skill_level: int,
    ) -> str:
        """
        Generate professional ECG classification explanation using GPT.
        
        Args:
            predicted_class: Predicted arrhythmia type
            confidence: Model confidence (0-1)
            affected_windows: Number of affected windows
            user_skill_level: User's skill level (1-5)
            
        Returns:
            HTML string with explanation
        """
        client_instance = LLMService._ensure_client()
        
        if not client_instance:
            logger.warning("OpenAI API key not configured. Using fallback explanation.")
            return LLMService._fallback_ecg_explanation(
                predicted_class, confidence, affected_windows, user_skill_level
            )

        try:
            skill_descriptions = {
                1: "un principiante",
                2: "un estudiante intermedio",
                3: "un estudiante avanzado",
                4: "un profesional experimentado",
                5: "un experto cardiólogo",
            }

            prompt = f"""Eres un cardiólogo especialista en ECG. Acaba de clasificarse un ECG como: {predicted_class.replace('_', ' ').title()}.

DATOS DEL ANÁLISIS:
- Clasificación predicha: {predicted_class.replace('_', ' ').title()}
- Confianza del modelo: {confidence*100:.1f}%
- Ventanas afectadas: {affected_windows}
- Nivel del estudiante: {skill_descriptions.get(user_skill_level, 'estudiante')}

Proporciona una BREVE pero COMPLETA explicación de qué es esta arritmia y por qué el modelo la detectó.
Adapta el lenguaje al nivel del estudiante.

Responde en HTML simple. Máximo 300 tokens."""

            response = client_instance.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un cardiólogo especialista educador. Explica claros y adapta al nivel del estudiante.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )

            return f"""
<div style="margin: 15px 0; padding: 12px; background: #fff8f0; border-left: 4px solid #ff9800;">
    <h4>📋 Explicación Detallada</h4>
    {response.choices[0].message.content}
    <p style="font-size: 12px; color: #666; margin-top: 10px;">
        Confianza del modelo: {confidence*100:.1f}%
    </p>
</div>
"""

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return LLMService._fallback_ecg_explanation(
                predicted_class, confidence, affected_windows, user_skill_level
            )

    @staticmethod
    def _fallback_progress_recommendations(
        arrhythmia_performance: dict,
        test_attempts: int,
        accuracy: float,
        weak_areas: List[str],
        incorrect_answers: Optional[List[dict]] = None,
    ) -> str:
        """Fallback when OpenAI is unavailable."""
        return f"""
<div style="margin: 20px 0;">
    <h3>🎯 Recomendaciones (Asistente Local)</h3>
    <p>Has completado <strong>{test_attempts} tests</strong> con una precisión del <strong>{accuracy:.1f}%</strong>.</p>
    
    {f'<p style="color: red;"><strong>⚠️ Áreas a mejorar:</strong> {", ".join(s.replace("_", " ").title() for s in weak_areas)}</p>' if weak_areas else '<p style="color: green;"><strong>✓ Buen desempeño</strong> en todas las áreas.</p>'}
    
    <h3>📚 Próximos Pasos</h3>
    <ul>
        <li>Continúa practicando con los temas débiles</li>
        <li>Realiza otro test diagnóstico en 1-2 semanas</li>
        <li>Estudia casos clínicos relacionados</li>
    </ul>
</div>
"""

    @staticmethod
    def _fallback_ecg_explanation(
        predicted_class: str,
        confidence: float,
        affected_windows: int,
        user_skill_level: int,
    ) -> str:
        """Fallback ECG explanation when OpenAI is unavailable."""
        class_descriptions = {
            "normal": "Ritmo sinusal normal",
            "atrial_fibrillation": "Fibrilación auricular (disrupciones irregulares)",
            "ventricular_tachycardia": "Taquicardia ventricular (frecuencia rápida)",
            "av_block": "Bloqueo AV (conducción lenta)",
            "atrial_flutter": "Flutter auricular (ondas rápidas regulares)",
        }
        
        description = class_descriptions.get(
            predicted_class, 
            predicted_class.replace("_", " ").title()
        )
        
        return f"""
<div style="margin: 15px 0; padding: 12px; background: #fff8f0; border-left: 4px solid #ff9800;">
    <h4>📋 Resultado de Clasificación</h4>
    <p><strong>Diagnóstico:</strong> {description}</p>
    <p><strong>Confianza:</strong> {confidence*100:.1f}%</p>
    <p><strong>Ventanas afectadas:</strong> {affected_windows}</p>
</div>
"""

    @staticmethod
    def generate_recommendations(
        wrong_questions: List[dict],
        skill_level: int,
        previous_level: Optional[int] = None,
    ) -> dict:
        """Legacy method for backward compatibility."""
        return {
            "success": True,
            "recommendations": LLMService._fallback_progress_recommendations(
                {}, 0, 0, []
            ),
        }


