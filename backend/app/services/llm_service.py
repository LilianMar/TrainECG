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

            prompt = f"""Eres un cardiólogo educador especializado en interpretacion de ECG. 
Un estudiante ha estado practicando y completó {test_attempts} tests con una precisión general del {accuracy:.1f}%.

DESEMPEÑO POR ARRITMIA:
{performance_summary if performance_summary else "Sin datos de tests aún"}

ÁREAS DE MEJORA IDENTIFICADAS:
{', '.join(weak_areas) if weak_areas else "Progreso consistente en todas las áreas"}
{incorrect_summary}

Por favor, proporciona recomendaciones ESPECÍFICAS y MOTIVADORAS basadas en las areas con mayor inicdencia de errores para:
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
<div style="margin: 20px 0; padding: 15px; border-radius: 8px;">
    
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

            prompt = f"""Eres un cardiólogo especialista en interpretación de ECG. Se ha clasificado el siguiente tipo de latido cardíaco: {predicted_class.replace('_', ' ').title()}.

DATOS DEL ANÁLISIS:
- Tipo de latido detectado: {predicted_class.replace('_', ' ').title()}
- Confianza del modelo: {confidence*100:.1f}%
- Ventanas con este tipo de latido: {affected_windows}
- Nivel del estudiante: {skill_descriptions.get(user_skill_level, 'estudiante')}

Proporciona una BREVE pero COMPLETA explicación de qué caracteriza este tipo de latido, su significado clínico y tips para identificarlo en ECGs.
Adapta el lenguaje al nivel del estudiante.

Responde en TEXTO PLANO sin HTML. Máximo 300 tokens."""

            response = client_instance.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un cardiólogo especialista educador. Explica claro y adapta al nivel del estudiante. NO uses HTML, solo texto plano.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )

            # Clean response from any HTML tags
            import re
            clean_text = re.sub(r'<[^>]+>', '', response.choices[0].message.content)
            
            return clean_text

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
    <h3> Recomendaciones (Asistente Local)</h3>
    <p>Has completado <strong>{test_attempts} tests</strong> con una precisión del <strong>{accuracy:.1f}%</strong>.</p>
    
    {f'<p style="color: red;"><strong>Áreas a mejorar:</strong> {", ".join(s.replace("_", " ").title() for s in weak_areas)}</p>' if weak_areas else '<p style="color: green;"><strong>✓ Buen desempeño</strong> en todas las áreas.</p>'}
    
    <h3> Próximos Pasos</h3>
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
            "normal": "Latido Normal: Representa un ritmo cardíaco sinusal regular, sin alteraciones en la conducción eléctrica. Es el patrón esperado en un corazón sano.",
            "supraventricular_ectopic": "Latido Ectópico Supraventricular: Latido prematuro originado en las aurículas o nodo AV. Generalmente benigno, pero puede indicar irritabilidad auricular.",
            "ventricular_ectopic": "Latido Ectópico Ventricular: Latido prematuro originado en los ventrículos. Requiere evaluación clínica, especialmente si es frecuente o con patrón anormal.",
            "fusion": "Latido de Fusión: Resultado de activación simultánea desde dos focos diferentes. Indica conducción eléctrica compleja.",
            "unknown": "Latido No Clasificable: Patrón atípico o con artefactos que dificultan la clasificación precisa.",
            "paced": "Latido con Marcapasos: Ritmo generado o asistido por dispositivo de estimulación cardíaca artificial.",
        }
        
        description = class_descriptions.get(
            predicted_class, 
            f"{predicted_class.replace('_', ' ').title()}: Tipo de latido detectado por el modelo."
        )
        
        return f"{description}\\n\\nConfianza del análisis: {confidence*100:.1f}%\\nVentanas con este patrón: {affected_windows}"

    @staticmethod
    def generate_recommendations(
        wrong_questions: List[dict],
        skill_level: int,
        previous_level: Optional[int] = None,
    ) -> dict:
        """
        Generate LLM-based study recommendations for test evaluation.

        Args:
            wrong_questions: List of question dicts answered incorrectly
            skill_level: User's current skill level (1-5)
            previous_level: Prior skill level, if available
        """
        client_instance = LLMService._ensure_client()

        arrhythmias_to_review = sorted({
            q.get("correct_class", "unknown")
            for q in wrong_questions
            if q.get("correct_class")
        })

        if not client_instance:
            logger.warning("OpenAI API key not configured. Using fallback test recommendations.")
            return {
                "success": True,
                "recommendations": LLMService._fallback_test_recommendations(
                    wrong_questions, skill_level, previous_level
                ),
                "arrhythmias_to_review": arrhythmias_to_review,
            }

        try:
            skill_descriptions = {
                1: "principiante",
                2: "intermedio",
                3: "intermedio",
                4: "avanzado",
                5: "experto",
            }

            errors_by_type = {}
            for question in wrong_questions:
                arr_type = question.get("correct_class", "unknown")
                if arr_type not in errors_by_type:
                    errors_by_type[arr_type] = []
                if question.get("question_text"):
                    errors_by_type[arr_type].append(question.get("question_text"))

            wrong_summary = ""
            for arr_type, questions in errors_by_type.items():
                wrong_summary += f"\n- {arr_type.replace('_', ' ').title()}:"
                for text in questions[:3]:
                    wrong_summary += f"\n  • {text[:160]}..."

            prompt = f"""Eres un cardiólogo educador especializado en interpretacion de ECG.
El estudiante acaba de completar un test de evaluacion.

DATOS DEL ESTUDIANTE:
- Nivel actual: {skill_level}/5 ({skill_descriptions.get(skill_level, 'intermedio')})
- Nivel previo: {previous_level}/5""" if previous_level is not None else f"""Eres un cardiólogo educador especializado en interpretacion de ECG.
El estudiante acaba de completar un test de evaluacion.

DATOS DEL ESTUDIANTE:
- Nivel actual: {skill_level}/5 ({skill_descriptions.get(skill_level, 'intermedio')})"""

            prompt += f"""

PREGUNTAS RESPONDIDAS INCORRECTAMENTE (resumen por arritmia):
{wrong_summary if wrong_summary else "Sin errores registrados."}

Genera recomendaciones ESPECIFICAS y accionables con foco en las debilidades:
1) Conceptos clinicos clave a reforzar
2) Pautas concretas para identificar la arritmia en ECG
3) Ejercicios o practica sugerida

Responde en HTML simple (divs y parrafos). Maximo 300 tokens. Sin emojis."""

            response = client_instance.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto cardiólogo educador. Da recomendaciones prácticas y motivadoras basadas en errores concretos.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                max_tokens=300,
            )

            return {
                "success": True,
                "recommendations": response.choices[0].message.content,
                "arrhythmias_to_review": arrhythmias_to_review,
            }
        except APIError as exc:
            logger.error(f"OpenAI API error: {str(exc)}")
            return {
                "success": True,
                "recommendations": LLMService._fallback_test_recommendations(
                    wrong_questions, skill_level, previous_level
                ),
                "arrhythmias_to_review": arrhythmias_to_review,
            }

    @staticmethod
    def _fallback_test_recommendations(
        wrong_questions: List[dict],
        skill_level: int,
        previous_level: Optional[int] = None,
    ) -> str:
        """Fallback recommendations for test evaluation."""
        arrhythmias = sorted({
            q.get("correct_class", "unknown")
            for q in wrong_questions
            if q.get("correct_class")
        })
        arrhythmias_text = ", ".join(
            a.replace("_", " ").title() for a in arrhythmias
        ) if arrhythmias else "Sin areas especificas detectadas"

        previous_text = f" (nivel previo {previous_level}/5)" if previous_level is not None else ""

        return f"""
<div style="margin: 12px 0;">
    <p><strong>Nivel actual:</strong> {skill_level}/5{previous_text}</p>
    <p><strong>Areas a reforzar:</strong> {arrhythmias_text}</p>
    <p><strong>Sugerencias:</strong></p>
    <ul>
        <li>Repasa los criterios diagnosticos de las arritmias con mayor error.</li>
        <li>Comparte trazos normales vs. patologicos y practica la diferenciacion.</li>
        <li>Realiza otro test tras estudiar los temas marcados.</li>
    </ul>
</div>
"""


