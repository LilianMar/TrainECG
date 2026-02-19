import { useEffect, useState } from "react";
import { ArrowLeft, Brain, CheckCircle, TrendingUp, AlertCircle } from "lucide-react";
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
        toast({
          title: "¡Correcto!",
          description: "Excelente respuesta",
        });
      } else {
        toast({
          title: "Incorrecto",
          description: `La respuesta correcta es la opción ${String.fromCharCode(65 + response.correct_answer)}`,
          variant: "destructive",
        });
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
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
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
      // Prepare answers with questions for backend
      const answers = questions.map((q, index) => ({
        question_id: q.id,
        selected_answer: index === currentQuestion ? selectedAnswer : 0, // Simplified
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
    const { accuracy, previous_level, new_level, level_improved, recommendations } = testResults;

    return (
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-gradient-hero relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-black/10 to-transparent" />
          <div className="relative z-10 container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <Link to="/dashboard">
                <Button variant="outline" size="sm" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Volver
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-white">Resultados de Evaluación</h1>
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

                <div className="bg-accent/10 p-6 rounded-lg border border-accent/20">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Precisión</p>
                      <p className="text-3xl font-bold text-accent">{Math.round(accuracy)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Nivel Anterior</p>
                      <p className="text-3xl font-bold text-warning">{previous_level}/5</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Nivel Actual</p>
                      <p className="text-3xl font-bold text-success">{new_level}/5</p>
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
              className="flex-1"
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

              <div className="bg-accent/10 p-6 rounded-lg border border-accent/20">
                <p className="text-2xl font-bold text-accent">{score}/10</p>
                <p className="text-sm text-muted-foreground mt-2">Tu puntuación</p>
              </div>

              <Button
                onClick={handleSubmitTest}
                disabled={isSubmittingTest}
                className="w-full"
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
            <Link to="/dashboard">
              <Button variant="outline" size="sm" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-white">Test de Evaluación</h1>
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
                const isSelected = selectedAnswer === index;
                const isCorrect =
                  showFeedback && answerFeedback?.correct_answer === index;
                const isWrong =
                  showFeedback && isSelected && !isCorrect;

                return (
                  <button
                    key={option}
                    onClick={() => handleAnswerSelect(index)}
                    disabled={showFeedback}
                    className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                      isCorrect
                        ? "border-success bg-success/10"
                        : isWrong
                          ? "border-destructive bg-destructive/10"
                          : isSelected
                            ? "border-accent bg-accent/10"
                            : "border-border hover:border-accent/50"
                    } ${showFeedback ? "cursor-not-allowed" : "cursor-pointer"}`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex items-center justify-center w-8 h-8 rounded font-semibold ${
                          isCorrect
                            ? "bg-success text-white"
                            : isWrong
                              ? "bg-destructive text-white"
                              : "bg-border"
                        }`}
                      >
                        {optionLabel}
                      </div>
                      <span>{optionText}</span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Feedback */}
            {showFeedback && answerFeedback && (
              <div className={`p-4 rounded-lg ${
                answerFeedback.is_correct
                  ? "bg-success/10 border border-success"
                  : "bg-destructive/10 border border-destructive"
              }`}>
                <p className="font-semibold mb-2">
                  {answerFeedback.is_correct ? "¡Correcto!" : "Incorrecto"}
                </p>
                <p className="text-sm mb-3">{answerFeedback.explanation}</p>
                <p className="text-xs text-muted-foreground">
                  Clase correcta: {answerFeedback.correct_class.replace(/_/g, " ")}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        {!showFeedback ? (
          <Button onClick={handleSubmitAnswer} className="w-full" size="lg">
            Enviar Respuesta
          </Button>
        ) : (
          <Button
            onClick={handleNextQuestion}
            className="w-full"
            size="lg"
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
