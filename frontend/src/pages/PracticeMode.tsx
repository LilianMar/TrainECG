import { useEffect, useState } from "react";
import { ArrowLeft, Brain, CheckCircle, XCircle, RotateCcw, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";
import { getImageUrl } from "@/lib/image";

const PracticeMode = () => {
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
  const { toast } = useToast();

  const currentQ = questions[currentQuestion];
  const progress = questions.length
    ? ((currentQuestion + 1) / questions.length) * 100
    : 0;

  const loadQuestions = async () => {
    setIsLoadingQuestions(true);
    try {
      const response = await apiRequest<{ questions: typeof questions }>("/practice/questions?limit=10");
      setQuestions(response.questions);
      setCurrentQuestion(0);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setAnswerFeedback(null);
      setQuestionStartedAt(Date.now());
    } catch (error) {
      const message = error instanceof Error ? error.message : "No se pudieron cargar las preguntas";
      toast({
        title: "Error al cargar practica",
        description: message,
        variant: "destructive",
      });
      setQuestions([]);
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  const handleAnswerSelect = (answerIndex: number) => {
    if (showFeedback) return;
    setSelectedAnswer(answerIndex);
  };

  const handleSubmitAnswer = async () => {
    if (selectedAnswer === null) {
      toast({
        title: "Selecciona una respuesta",
        description: "Por favor, elige una opción antes de continuar.",
        variant: "destructive",
      });
      return;
    }

    if (!currentQ) return;

    try {
      const timeSpentSeconds = Math.max(
        1,
        Math.round((Date.now() - questionStartedAt) / 1000)
      );
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
          time_spent_seconds: timeSpentSeconds,
        },
      });

      setAnswerFeedback(response);
      setShowFeedback(true);

      if (response.is_correct) {
        setScore((prev) => prev + 1);
        toast({
          title: "¡Correcto!",
          description: "Excelente diagnostico.",
          variant: "success",
        });
      } else {
        toast({
          title: "Respuesta incorrecta",
          description: "Revisa la explicacion para aprender.",
          variant: "destructive",
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "No se pudo enviar la respuesta";
      toast({
        title: "Error al enviar respuesta",
        description: message,
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
      toast({
        title: "¡Práctica completada!",
        description: `Puntuacion final: ${score}/${questions.length}`,
        variant: "success",
      });
    }
  };

  const resetPractice = () => {
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setShowFeedback(false);
    setAnswerFeedback(null);
    setScore(0);
    setQuestionStartedAt(Date.now());
  };

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
              <h1 className="text-2xl font-bold text-white">Modo Práctica</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-white/90">
                Pregunta {currentQuestion + 1} de {questions.length}
              </span>
              <Button variant="outline" size="sm" onClick={resetPractice} className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                <RotateCcw className="w-4 h-4 mr-2" />
                Reiniciar
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Progress Bar */}
        <Card className="medical-card mb-6">
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Progreso</span>
              <span className="text-sm text-muted-foreground">
                Puntuación: {score}/{questions.length}
              </span>
            </div>
            <Progress value={progress} className="w-full" />
          </CardContent>
        </Card>

        {isLoadingQuestions ? (
          <Card className="medical-card">
            <CardContent className="p-8 text-center">
              <Brain className="w-10 h-10 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Cargando preguntas...</p>
            </CardContent>
          </Card>
        ) : questions.length === 0 ? (
          <Card className="medical-card">
            <CardContent className="p-8 text-center space-y-4">
              <p className="text-muted-foreground">No hay preguntas disponibles.</p>
              <Button className="btn-medical" onClick={loadQuestions}>
                Reintentar
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* ECG Display */}
          <div className="space-y-6">
            <Card className="medical-card">
              <CardHeader>
                <CardTitle>ECG para Análisis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-secondary rounded-lg p-4 ecg-grid min-h-[300px] flex items-center justify-center overflow-hidden">
                  {currentQ?.image_path ? (
                    <div className="w-full h-full flex items-center justify-center">
                      <img 
                        src={getImageUrl(currentQ.image_path)}
                        alt="ECG para análisis"
                        className="w-full h-auto object-contain rounded-md max-h-96"
                        onError={(e) => {
                          const img = e.currentTarget;
                          console.error('[IMG ERROR] Failed to load image:', img.src);
                          console.error('[IMG ERROR] Alt text:', img.alt);
                          img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="100"%3E%3Crect fill="%23eee" width="200" height="100"/%3E%3Ctext x="50%" y="50%" text-anchor="middle" dy=".3em" fill="%23999" font-size="14"%3EError loading image%3C/text%3E%3C/svg%3E';
                        }}
                        onLoad={() => {
                          console.log('[IMG LOADED] Image loaded successfully:', currentQ.image_path);
                        }}
                      />
                    </div>
                  ) : (
                    <div className="text-center">
                      <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">
                        No hay imagen disponible
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Feedback Section */}
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

                  {currentQuestion < questions.length - 1 ? (
                    <Button onClick={handleNextQuestion} className="btn-medical w-full">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Siguiente Pregunta
                    </Button>
                  ) : (
                    <div className="space-y-3">
                      <div className="text-center p-4 bg-primary/10 rounded-lg">
                        <h3 className="font-bold text-lg text-primary mb-2">¡Práctica Completada!</h3>
                        <p className="text-muted-foreground">
                          Puntuacion final: {score}/{questions.length} 
                          ({Math.round((score / questions.length) * 100)}%)
                        </p>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <Button onClick={resetPractice} variant="outline" className="w-full">
                          <RotateCcw className="w-4 h-4 mr-2" />
                          Practicar de Nuevo
                        </Button>
                        <Link to="/dashboard" className="w-full">
                          <Button className="btn-medical w-full">
                            Ir al Dashboard
                          </Button>
                        </Link>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Question and Options */}
          <div className="space-y-6">
            <Card className="medical-card">
              <CardHeader>
                <CardTitle>{currentQ.question_text}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[currentQ.option_a, currentQ.option_b, currentQ.option_c, currentQ.option_d].map((option, index) => (
                  <button
                    key={index}
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
                        {String.fromCharCode(65 + index)}
                      </span>
                      <span>{option}</span>
                    </div>
                  </button>
                ))}

                {!showFeedback && (
                  <Button 
                    onClick={handleSubmitAnswer} 
                    className="btn-medical w-full mt-6"
                    disabled={selectedAnswer === null}
                  >
                    Enviar Respuesta
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Learning Tips */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="text-sm">💡 Consejo de Aprendizaje</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Observa cuidadosamente el ritmo, la frecuencia y la morfología de las ondas. 
                  Recuerda que la práctica regular mejora significativamente la precisión diagnóstica.
                </p>
              </CardContent>
            </Card>
          </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default PracticeMode;