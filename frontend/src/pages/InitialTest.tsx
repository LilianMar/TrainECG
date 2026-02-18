import { useEffect, useState } from "react";
import { ArrowLeft, Brain, CheckCircle, XCircle, RotateCcw } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";
import { getImageUrl } from "@/lib/image";

const InitialTest = () => {
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
  const navigate = useNavigate();
  const { toast } = useToast();

  const currentQ = questions[currentQuestion];
  const progress = questions.length
    ? ((currentQuestion + 1) / questions.length) * 100
    : 0;

  const loadQuestions = async () => {
    setIsLoadingQuestions(true);
    try {
      const response = await apiRequest<{ questions: typeof questions }>("/practice/questions?limit=5&difficulty=1");
      if (!response.questions || response.questions.length === 0) {
        toast({
          title: "Sin preguntas",
          description: "No hay preguntas de test disponibles. Por favor intenta más tarde.",
          variant: "destructive",
        });
        navigate("/dashboard");
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
      navigate("/dashboard");
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
        body: JSON.stringify({
          question_id: currentQ.id,
          selected_answer: selectedAnswer,
          time_spent_seconds: timeSpent,
        }),
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

  const handleRestartTest = () => {
    setScore(0);
    loadQuestions();
  };

  if (isLoadingQuestions) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-8 text-center">
            <Brain className="w-12 h-12 text-accent mx-auto mb-4 animate-pulse" />
            <p className="text-lg font-medium">Cargando preguntas del test...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (testCompleted) {
    const accuracy = questions.length ? Math.round((score / questions.length) * 100) : 0;

    return (
      <div className="min-h-screen bg-background py-8">
        <div className="max-w-2xl mx-auto px-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <Link to="/dashboard" className="flex items-center space-x-2 text-accent hover:text-accent/80 transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span>Volver</span>
            </Link>
            <h1 className="text-2xl font-bold">Test Inicial Completado</h1>
            <div className="w-10" /> {/* Spacer */}
          </div>

          {/* Results Card */}
          <Card className="medical-card">
            <CardContent className="p-8">
              <div className="text-center space-y-6">
                <CheckCircle className="w-16 h-16 text-success mx-auto" />
                
                <div>
                  <h2 className="text-3xl font-bold text-success mb-2">¡Excelente!</h2>
                  <p className="text-muted-foreground">Has completado el test inicial</p>
                </div>

                <div className="bg-accent/10 p-6 rounded-lg border border-accent/20">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Puntuación</p>
                      <p className="text-3xl font-bold text-accent">{score}/{questions.length}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Precisión</p>
                      <p className="text-3xl font-bold text-accent">{accuracy}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Preguntas</p>
                      <p className="text-3xl font-bold text-accent">{questions.length}</p>
                    </div>
                  </div>
                </div>

                <div className="pt-4 space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Este es tu test diagnóstico. Usa los resultados para identificar áreas de mejora.
                  </p>
                </div>

                <div className="flex gap-4 pt-4">
                  <Button 
                    onClick={handleRestartTest}
                    variant="outline"
                    className="flex-1"
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Repetir Test
                  </Button>
                  <Button 
                    onClick={() => navigate("/practice")}
                    className="flex-1"
                  >
                    Ir a Práctica
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
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

  const options = [
    { label: "A", text: currentQ.option_a },
    { label: "B", text: currentQ.option_b },
    { label: "C", text: currentQ.option_c },
    { label: "D", text: currentQ.option_d },
  ];

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link to="/dashboard" className="flex items-center space-x-2 text-accent hover:text-accent/80 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span>Volver</span>
          </Link>
          <h1 className="text-2xl font-bold">Test Inicial</h1>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Pregunta {currentQuestion + 1} de {questions.length}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <Progress value={progress} className="h-2" />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Question and Image */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="medical-card">
              <CardContent className="p-6">
                {/* Image */}
                <div className="mb-6">
                  <img
                    src={getImageUrl(currentQ.image_path)}
                    alt="ECG"
                    className="w-full rounded-lg border border-border object-contain max-h-64"
                    onError={(e) => {
                      e.currentTarget.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%23f0f0f0' width='400' height='200'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999'%3EImagen no disponible%3C/text%3E%3C/svg%3E";
                    }}
                  />
                </div>

                {/* Question */}
                <h2 className="text-lg font-semibold mb-6">{currentQ.question_text}</h2>

                {/* Options */}
                <div className="space-y-3">
                  {options.map((option, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleAnswerSelect(idx)}
                      disabled={showFeedback}
                      className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                        selectedAnswer === idx
                          ? "border-accent bg-accent/10"
                          : "border-border hover:border-accent/50"
                      } ${
                        showFeedback && idx === answerFeedback?.correct_answer
                          ? "border-success bg-success/10"
                          : ""
                      } ${
                        showFeedback && selectedAnswer === idx && !answerFeedback?.is_correct
                          ? "border-destructive bg-destructive/10"
                          : ""
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center flex-shrink-0">
                          {option.label}
                        </div>
                        <span>{option.text}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar - Feedback/Stats */}
          <div className="space-y-6">
            {/* Score Card */}
            <Card className="medical-card bg-gradient-to-br from-accent/5 to-primary/5">
              <CardHeader>
                <CardTitle className="text-sm">Progreso</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-accent mb-2">{score}</p>
                  <p className="text-sm text-muted-foreground">respuestas correctas</p>
                </div>
              </CardContent>
            </Card>

            {/* Feedback Card */}
            {showFeedback && answerFeedback && (
              <Card className={`medical-card ${answerFeedback.is_correct ? "bg-success/10 border-success/20" : "bg-destructive/10 border-destructive/20"}`}>
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    {answerFeedback.is_correct ? (
                      <>
                        <CheckCircle className="w-5 h-5 text-success" />
                        Correcto
                      </>
                    ) : (
                      <>
                        <XCircle className="w-5 h-5 text-destructive" />
                        Incorrecto
                      </>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Clase correcta:</p>
                    <p className="font-semibold text-sm capitalize">{answerFeedback.correct_class.replace(/_/g, " ")}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Explicación:</p>
                    <p className="text-sm">{answerFeedback.explanation}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Button */}
            {!showFeedback ? (
              <Button 
                onClick={handleSubmitAnswer}
                disabled={selectedAnswer === null}
                className="w-full"
              >
                Verificar Respuesta
              </Button>
            ) : (
              <Button 
                onClick={handleNextQuestion}
                className="w-full"
              >
                {currentQuestion === questions.length - 1 ? "Ver Resultados" : "Siguiente Pregunta"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InitialTest;
