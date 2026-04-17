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
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setAnswerFeedback(null);
      setQuestionStartedAt(Date.now());
    } else {
      setTestCompleted(true);
    }
  };

  const handleSubmitInitialTest = async () => {
    try {
      await apiRequest("/practice/complete-initial-test", {
        method: "POST",
        body: {
          score,
          total: questions.length,
        },
      });

      toast({
        title: "¡Nivel Asignado!",
        description: "Tu nivel de habilidad ha sido asignado. Ahora puedes acceder a la práctica.",
      });

      // Navigate to dashboard first so user data reloads and sees the change
      // Then can navigate to practice from there
      setTimeout(() => navigate("/dashboard"), 2000);
    } catch (error) {
      console.error("Error submitting test:", error);
      toast({
        title: "Error",
        description: "No se pudo guardar tu nivel. Intenta nuevamente.",
        variant: "destructive",
      });
    }
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
                <h1 className="text-2xl font-bold text-white">Test Inicial Completado</h1>
              </div>
              <div className="w-10" /> {/* Spacer */}
            </div>
          </div>
        </header>

        <div className="bg-gray-50/30 py-8">
          <div className="max-w-2xl mx-auto px-4">
            {/* Results Card */}
            <Card className="medical-card">
              <CardContent className="p-8">
                <div className="text-center space-y-6">
                  <CheckCircle className="w-16 h-16 text-success mx-auto" />

                  <div>
                    <h2 className="text-3xl font-bold text-success mb-2">¡Excelente!</h2>
                    <p className="text-muted-foreground">Has completado el test inicial</p>
                  </div>

                  <div className="bg-primary/20 p-6 rounded-lg border border-primary/40">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Puntuación</p>
                        <p className="text-3xl font-bold" style={{color: 'hsl(213, 50%, 25%)'}}>{score}/{questions.length}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Precisión</p>
                        <p className="text-3xl font-bold" style={{color: 'hsl(213, 50%, 25%)'}}>{accuracy}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Preguntas</p>
                        <p className="text-3xl font-bold" style={{color: 'hsl(213, 50%, 25%)'}}>{questions.length}</p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 space-y-3">
                    <p className="text-sm text-muted-foreground">
                      Este es tu test diagnóstico inicial. Se te ha asignado un nivel de habilidad basado en tu desempeño.
                    </p>
                  </div>

                  <div className="pt-4">
                    <Button
                      onClick={handleSubmitInitialTest}
                      className="btn-medical w-full"
                    >
                      Comenzar Práctica
                    </Button>
                  </div>
                </div>
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

  const options = [
    { label: "A", text: currentQ.option_a },
    { label: "B", text: currentQ.option_b },
    { label: "C", text: currentQ.option_c },
    { label: "D", text: currentQ.option_d },
  ];

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
              <h1 className="text-2xl font-bold text-white">Test Inicial</h1>
            </div>
            <div className="text-right">
              <p className="text-sm text-white/90">Pregunta {currentQuestion + 1} de {questions.length}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="bg-gray-50/30 py-8">
        <div className="max-w-4xl mx-auto px-4">

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
                      className={`w-full p-4 text-left border rounded-lg transition-all ${
                        selectedAnswer === idx
                          ? showFeedback
                            ? idx === answerFeedback?.correct_answer
                              ? "border-success bg-success/10 text-success"
                              : "border-destructive bg-destructive/10 text-destructive"
                            : "border-primary bg-primary/10 text-primary"
                          : showFeedback && idx === answerFeedback?.correct_answer
                          ? "border-success bg-success/10 text-success"
                          : "border-border hover:border-primary/50 hover:bg-primary/5"
                      }`}
                    >
                      <div className="flex items-center">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full border border-current flex items-center justify-center mr-3 text-xs font-medium">
                          {option.label}
                        </span>
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
            <Card className="medical-card bg-gradient-to-br from-primary/5 to-primary/10">
              <CardHeader>
                <CardTitle className="text-sm">Progreso</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary mb-2">{score}</p>
                  <p className="text-sm text-foreground/70">respuestas correctas</p>
                </div>
              </CardContent>
            </Card>

            {/* Feedback Card */}
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

            {/* Action Button */}
            {!showFeedback ? (
              <Button 
                onClick={handleSubmitAnswer}
                disabled={selectedAnswer === null}
                className="btn-medical w-full mt-6"
              >
                Verificar Respuesta
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
      </div>
    </div>
  );
};

export default InitialTest;
