import { useEffect, useState } from "react";
import { ArrowLeft, Brain, CheckCircle, XCircle, TrendingUp, AlertCircle } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";
import { getImageUrl } from "@/lib/image";

const PostPracticeTest = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [score, setScore] = useState(0);
  const [questions, setQuestions] = useState<Array<{
    id: number;
    image_path: string;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_answer: number;
    explanation: string;
    correct_class: string;
    difficulty_level: number;
  }>>([]);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(true);
  const [answerFeedback, setAnswerFeedback] = useState<{
    is_correct: boolean;
    correct_answer: number;
    explanation: string;
    correct_class: string;
  } | null>(null);
  const [answersByQuestion, setAnswersByQuestion] = useState<Record<number, number>>({});
  const [questionStartedAt, setQuestionStartedAt] = useState<number>(Date.now());
  const [testCompleted, setTestCompleted] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [isSubmittingTest, setIsSubmittingTest] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const currentQ = questions[currentQuestion];
  const progress = questions.length
    ? ((currentQuestion + 1) / questions.length) * 100
    : 0;

  const loadQuestions = async () => {
    setIsLoadingQuestions(true);
    try {
      // Load mixed difficulty questions (mix of level 1, 2, and 3)
      const response = await apiRequest<{ questions: typeof questions }>(
        "/practice/questions?limit=10"
      );

      if (!response.questions || response.questions.length === 0) {
        toast({
          title: "Sin preguntas",
          description: "No hay preguntas disponibles para el test.",
          variant: "destructive",
        });
        navigate("/practice");
        return;
      }

      setQuestions(response.questions);
      setCurrentQuestion(0);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setAnswerFeedback(null);
      setScore(0);
      setTestCompleted(false);
      setAnswersByQuestion({});
      setQuestionStartedAt(Date.now());
    } catch (error) {
      console.error("Error loading questions:", error);
      toast({
        title: "Error",
        description: "No se pudieron cargar las preguntas del test",
        variant: "destructive",
      });
      navigate("/practice");
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  const handleAnswerSelect = (optionIndex: number) => {
    if (!showFeedback) {
      setSelectedAnswer(optionIndex);
      if (currentQ?.id != null) {
        setAnswersByQuestion((prev) => ({
          ...prev,
          [currentQ.id]: optionIndex,
        }));
      }
    }
  };

  const handleSubmitAnswer = async () => {
    if (selectedAnswer === null) {
      toast({
        title: "Selecciona una respuesta",
        description: "Por favor selecciona una opción antes de continuar",
      });
      return;
    }

    try {
      const timeSpent = Math.max(1, Math.round((Date.now() - questionStartedAt) / 1000));

      const response = await apiRequest<{
        is_correct: boolean;
        correct_answer: number;
        explanation: string;
        correct_class: string;
      }>("/practice/answer", {
        method: "POST",
        body: {
          question_id: currentQ.id,
          selected_answer: selectedAnswer,
          time_spent_seconds: timeSpent,
        },
      });

      setAnswerFeedback(response);
      setShowFeedback(true);

      if (response.is_correct) {
        setScore(score + 1);
      }
    } catch (error) {
      console.error("Error submitting answer:", error);
      toast({
        title: "Error",
        description: "No se pudo enviar la respuesta",
        variant: "destructive",
      });
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      const nextIndex = currentQuestion + 1;
      const nextQuestionId = questions[nextIndex]?.id;
      setCurrentQuestion(nextIndex);
      setSelectedAnswer(nextQuestionId != null ? answersByQuestion[nextQuestionId] ?? null : null);
      setShowFeedback(false);
      setAnswerFeedback(null);
      setQuestionStartedAt(Date.now());
    } else {
      setTestCompleted(true);
    }
  };

  const handleSubmitTest = async () => {
    setIsSubmittingTest(true);
    try {
      // Prepare answers - only include questions that were actually answered
      const answers = questions
        .filter((q) => q.id in answersByQuestion) // Only answered questions
        .map((q) => ({
          question_id: q.id,
          selected_answer: answersByQuestion[q.id],
          time_spent_seconds: 30, // Average
        }));

      const response = await apiRequest<any>("/practice/post-practice-test", {
        method: "POST",
        body: {
          answers,
          test_questions: questions,
        },
      });

      setTestResults(response);

      toast({
        title: "¡Test Completado!",
        description: "Tu evaluación ha sido procesada.",
      });
    } catch (error) {
      console.error("Error submitting test:", error);
      toast({
        title: "Error",
        description: "No se pudo enviar el test",
        variant: "destructive",
      });
    } finally {
      setIsSubmittingTest(false);
    }
  };

  if (isLoadingQuestions) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-8 text-center">
            <Brain className="w-12 h-12 text-accent mx-auto mb-4 animate-pulse" />
            <p className="text-lg font-medium">Cargando test de evaluación...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (testResults) {
    const { previous_level, new_level, level_improved, recommendations, accuracy } = testResults;
    // Usar accuracy devuelto por el backend (cálculo correcto con respuestas reales)

    return (
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-gradient-hero relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-black/10 to-transparent" />
          <div className="relative z-10 container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Link to="/dashboard">
                  <Button variant="outline" size="sm" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Volver
                  </Button>
                </Link>
                <h1 className="text-2xl font-bold text-white">Resultados de Evaluación</h1>
              </div>
              <div className="w-10" /> {/* Spacer */}
            </div>
          </div>
        </header>

        <div className="bg-gray-50/30 py-8">
          <div className="max-w-4xl mx-auto px-4">

          {/* Results Card */}
          <Card className="medical-card mb-6">
            <CardContent className="p-8">
              <div className="text-center space-y-6">
                <div className="flex justify-center gap-4">
                  <CheckCircle className="w-16 h-16 text-success" />
                  {level_improved && <TrendingUp className="w-16 h-16 text-warning animate-bounce" />}
                </div>

                <div>
                  <h2 className="text-3xl font-bold text-success mb-2">
                    {level_improved ? "¡Progreso Detectado!" : "Test Completado"}
                  </h2>
                  <p className="text-muted-foreground">
                    {level_improved
                      ? `Mejoraste del nivel ${previous_level} al nivel ${new_level}`
                      : "Revisa tus resultados y las recomendaciones de estudio"}
                  </p>
                </div>

                <div className="bg-accent/20 p-6 rounded-lg border border-accent/40">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Precisión</p>
                      <p className="text-3xl font-bold" style={{color: 'hsl(213, 50%, 25%)'}}>{Math.round(accuracy)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Nivel Anterior</p>
                      <p className="text-3xl font-bold" style={{color: 'hsl(38, 92%, 50%)'}}>{previous_level}/5</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Nivel Actual</p>
                      <p className="text-3xl font-bold" style={{color: 'hsl(142, 76%, 36%)'}}>{new_level}/5</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recommendations Card */}
          {recommendations && (
            <Card className="medical-card mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-accent" />
                  Recomendaciones de Estudio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className="prose prose-sm dark:prose-invert max-w-none"
                  dangerouslySetInnerHTML={{
                    __html: recommendations.recommendations,
                  }}
                />

                {recommendations.arrhythmias_to_review &&
                  recommendations.arrhythmias_to_review.length > 0 && (
                    <div className="mt-6 p-4 bg-warning/10 border border-warning/20 rounded-lg">
                      <p className="text-sm font-semibold mb-3">Temas a Revisar:</p>
                      <div className="flex flex-wrap gap-2">
                        {recommendations.arrhythmias_to_review.map((arrhythmia: string) => (
                          <span
                            key={arrhythmia}
                            className="px-3 py-1 bg-warning/20 text-warning rounded-full text-sm"
                          >
                            {arrhythmia.replace(/_/g, " ").split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button
              onClick={() => navigate("/dashboard")}
              variant="outline"
              className="flex-1"
            >
              Volver a Práctica
            </Button>
            <Button
              onClick={() => navigate("/progress")}
              className="btn-medical flex-1"
            >
              Ver Progreso Completo
            </Button>
          </div>
          </div>
        </div>
      </div>
    );
  }

  if (testCompleted) {
    return (
      <div className="min-h-screen bg-background">
        <div className="bg-gray-50/30 py-8">
          <div className="max-w-2xl mx-auto px-4">
          <Card className="medical-card">
            <CardContent className="p-8 text-center space-y-6">
              <Brain className="w-16 h-16 text-accent mx-auto" />
              <div>
                <h2 className="text-3xl font-bold mb-2">Test Completado</h2>
                <p className="text-muted-foreground">Procesando resultados y generando recomendaciones...</p>
              </div>

              <div className="bg-accent/20 p-6 rounded-lg border border-accent/40">
                <p className="text-2xl font-bold" style={{color: 'hsl(213, 50%, 25%)'}}>{score}/10</p>
                <p className="text-sm text-muted-foreground mt-2">Tu puntuación</p>
              </div>

              <Button
                onClick={handleSubmitTest}
                disabled={isSubmittingTest}
                className="btn-medical w-full"
              >
                {isSubmittingTest ? "Procesando..." : "Ver Resultados y Recomendaciones"}
              </Button>
            </CardContent>
          </Card>
          </div>
        </div>
      </div>
    );
  }

  if (!currentQ) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-8 text-center">
            <p className="text-lg">No hay preguntas disponibles</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-gradient-hero relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-black/10 to-transparent" />
        <div className="relative z-10 container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/dashboard">
                <Button variant="outline" size="sm" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Volver
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-white">Test de Evaluación</h1>
            </div>
            <div className="w-20 text-right">
              <span className="text-sm text-white/90">
                {currentQuestion + 1}/{questions.length}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="bg-gray-50/30 py-8">
        <div className="max-w-3xl mx-auto px-4">

        {/* Progress */}
        <Card className="medical-card mb-6">
          <CardContent className="p-6">
            <div className="space-y-3">
              <Progress value={progress} className="h-2" />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Progreso</span>
                <span>{Math.round(progress)}%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Question */}
        <Card className="medical-card mb-6">
          <CardHeader>
            <CardTitle>{currentQ?.question_text}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Image */}
            {currentQ?.image_path && (
              <div className="relative w-full bg-muted rounded-lg overflow-hidden">
                <img
                  src={getImageUrl(currentQ.image_path)}
                  alt="ECG"
                  className="w-full h-auto max-h-80 object-cover"
                />
              </div>
            )}

            {/* Options */}
            <div className="space-y-3">
              {["option_a", "option_b", "option_c", "option_d"].map((option, index) => {
                const optionLabel = String.fromCharCode(65 + index);
                const optionText = currentQ?.[option as keyof typeof currentQ];

                return (
                  <button
                    key={option}
                    onClick={() => handleAnswerSelect(index)}
                    disabled={showFeedback}
                    className={`w-full p-4 text-left border rounded-lg transition-all ${
                      selectedAnswer === index
                        ? showFeedback
                          ? index === answerFeedback?.correct_answer
                            ? "border-success bg-success/10 text-success"
                            : "border-destructive bg-destructive/10 text-destructive"
                          : "border-primary bg-primary/10 text-primary"
                        : showFeedback && index === answerFeedback?.correct_answer
                        ? "border-success bg-success/10 text-success"
                        : "border-border hover:border-primary/50 hover:bg-primary/5"
                    }`}
                  >
                    <div className="flex items-center">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full border border-current flex items-center justify-center mr-3 text-xs font-medium">
                        {optionLabel}
                      </span>
                      <span>{optionText}</span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Feedback */}
            {showFeedback && answerFeedback && (
              <Card className={`medical-card ${answerFeedback.is_correct ? 'border-success/20 bg-success/5' : 'border-destructive/20 bg-destructive/5'}`}>
                <CardHeader>
                  <CardTitle className={`flex items-center ${answerFeedback.is_correct ? 'text-success' : 'text-destructive'}`}>
                    {answerFeedback.is_correct ? (
                      <CheckCircle className="w-5 h-5 mr-2" />
                    ) : (
                      <XCircle className="w-5 h-5 mr-2" />
                    )}
                    {answerFeedback.is_correct ? "¡Correcto!" : "Incorrecto"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Explicación:</h4>
                    <p className="text-sm text-muted-foreground">
                      {answerFeedback.explanation}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-secondary rounded-lg">
                    <h4 className="font-medium mb-2">Clase Correcta:</h4>
                    <p className="text-sm text-muted-foreground">
                      {answerFeedback.correct_class}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        {!showFeedback ? (
          <Button onClick={handleSubmitAnswer} className="btn-medical w-full mt-6">
            Enviar Respuesta
          </Button>
        ) : (
          <Button
            onClick={handleNextQuestion}
            className="btn-medical w-full mt-6"
          >
            {currentQuestion === questions.length - 1 ? "Ver Resultados" : "Siguiente Pregunta"}
          </Button>
        )}
        </div>
      </div>
    </div>
  );
};

export default PostPracticeTest;
