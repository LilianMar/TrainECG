import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, TrendingUp, Target, Zap, Award } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress as ProgressBar } from "@/components/ui/progress";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { apiRequest } from "@/lib/api";
import { BadgeIcon } from "@/components/BadgeIcon";

interface ProgressionData {
  week: string;
  correct_answers: number;
  total_attempts: number;
  accuracy: number;
}

interface TestAttempt {
  attempt: string;
  score: number;
  correct: number;
  total: number;
  created_at: string;
}

interface Badge {
  id: number | null;
  name: string;
  description: string;
  icon: string;
  color: string;
  earned_at: string | null;
  achieved: boolean;
}

const Progress = () => {
  const [progressData, setProgressData] = useState<{
    total_ecgs_analyzed: number;
    classification_accuracy: number;
    total_practice_attempts: number;
    practice_accuracy: number;
    total_practice_correct: number;
    test_accuracy: number;
    test_correct: number;
    test_total: number;
    current_streak_days: number;
    longest_streak_days: number;
    skill_level?: number | null;
  } | null>(null);
  const [progression, setProgression] = useState<ProgressionData[]>([]);
  const [testAttempts, setTestAttempts] = useState<TestAttempt[]>([]);
  const [postTestAttempts, setPostTestAttempts] = useState<TestAttempt[]>([]);
  const [arrhythmiaStats, setArrhythmiaStats] = useState<Array<{
    name: string;
    practice_correct: number;
    practice_total: number;
    practice_accuracy: number;
    test_correct: number;
    test_total: number;
    test_accuracy: number;
  }>>([]);
  const [recommendations, setRecommendations] = useState<{
    recommendations: string;
    test_attempts: number;
    overall_accuracy: number;
    weak_areas: string[];
    has_llm: boolean;
  } | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);

  // Calculate pie chart data based on practice attempts
  const calculatePieData = () => {
    if (!progressData || progressData.total_practice_attempts === 0) {
      return [
        { name: "Correcto", value: 0, color: "hsl(var(--success))" },
        { name: "Incorrecto", value: 0, color: "hsl(var(--destructive))" },
      ];
    }

    const correctPercentage = (progressData.total_practice_correct / progressData.total_practice_attempts) * 100;
    const incorrectPercentage = 100 - correctPercentage;

    return [
      { name: "Correcto", value: Math.round(correctPercentage), color: "hsl(var(--success))" },
      { name: "Incorrecto", value: Math.round(incorrectPercentage), color: "hsl(var(--destructive))" },
    ];
  };

  const pieData = calculatePieData();


  const loadProgress = useCallback(async () => {
    try {
      const data = await apiRequest<typeof progressData>("/progress");
      if (data) {
        setProgressData(data);
      }

      const progressionResponse = await apiRequest<{ progression: ProgressionData[] }>(
        "/progress/progression"
      );
      if (progressionResponse.progression) {
        setProgression(progressionResponse.progression);
      }

      const testResponse = await apiRequest<{ test_attempts: TestAttempt[] }>(
        "/progress/test-attempts"
      );
      if (testResponse.test_attempts) {
        setTestAttempts(testResponse.test_attempts);
      }

      const postTestResponse = await apiRequest<{ post_test_attempts: TestAttempt[] }>(
        "/progress/post-test-attempts"
      );
      if (postTestResponse.post_test_attempts) {
        setPostTestAttempts(postTestResponse.post_test_attempts);
      }

      const statsResponse = await apiRequest<{ arrhythmia_stats: Record<string, { 
        practice_correct: number; 
        practice_total: number; 
        practice_accuracy: number;
        test_correct: number;
        test_total: number;
        test_accuracy: number;
      }> }>(
        "/progress/stats/by-arrhythmia"
      );
      const stats = Object.entries(statsResponse.arrhythmia_stats || {}).map(
        ([name, stat]) => ({
          name,
          practice_correct: stat.practice_correct,
          practice_total: stat.practice_total,
          practice_accuracy: stat.practice_accuracy,
          test_correct: stat.test_correct,
          test_total: stat.test_total,
          test_accuracy: stat.test_accuracy,
        })
      );
      setArrhythmiaStats(stats);

      const recommendationsResponse = await apiRequest<{
        recommendations: string;
        test_attempts: number;
        overall_accuracy: number;
        weak_areas: string[];
        has_llm: boolean;
      }>(
        "/progress/recommendations"
      );
      if (recommendationsResponse) {
        setRecommendations(recommendationsResponse);
      }

      const badgesResponse = await apiRequest<{ 
        earned_badges: Badge[];
        available_badges: Badge[];
        all_badges: Badge[];
        total_earned: number;
        total_available: number;
      }>(
        "/achievements"
      );
      // Get top 5 badges (earned first, then available)
      if (badgesResponse) {
        const allBadges = badgesResponse.all_badges ?? badgesResponse.earned_badges ?? [];
        setBadges(allBadges.slice(0, 5));
      }
    } catch (error) {
      // Keep placeholders if API is unavailable
      console.error("Error loading progress data:", error);
    }
  }, []);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  useEffect(() => {
    const handleRefresh = () => {
      loadProgress();
    };

    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        loadProgress();
      }
    };

    window.addEventListener("focus", handleRefresh);
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      window.removeEventListener("focus", handleRefresh);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [loadProgress]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-gradient-hero relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-black/10 to-transparent" />
        <div className="relative z-10 container mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link to="/dashboard">
              <Button variant="outline" size="sm" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-white">Mi Progreso</h1>
          </div>
        </div>
      </header>

      <main className="bg-gray-50/30 py-8">
        <div className="container mx-auto px-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="medical-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Precisión Total en Test</p>
                  <p className="text-2xl font-bold text-success">
                    {progressData?.test_accuracy ?? 0}%
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-success" />
              </div>
            </CardContent>
          </Card>

          <Card className="medical-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">ECGs Analizados</p>
                  <p className="text-2xl font-bold text-primary">{progressData?.total_ecgs_analyzed ?? 0}</p>
                </div>
                <Target className="w-8 h-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="medical-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Preguntas Correctas en Práctica</p>
                  <p className="text-2xl font-bold text-warning">{progressData?.total_practice_correct ?? 0}</p>
                </div>
                <Zap className="w-8 h-8 text-warning" />
              </div>
            </CardContent>
          </Card>

          {progressData?.skill_level && (
            <Card className="medical-card bg-gradient-to-br from-primary/5 to-primary/10">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Tu Nivel Actual</p>
                    <p className="text-2xl font-bold text-primary">{progressData.skill_level}/5</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-primary" />
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Practice Performance Chart */}
          <Card className="medical-card">
            <CardHeader>
              <CardTitle>Progreso en Test por Intento</CardTitle>
            </CardHeader>
            <CardContent>
              {postTestAttempts.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={postTestAttempts}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="attempt" />
                    <YAxis domain={[0, 100]} label={{ value: '% Aciertos', angle: -90, position: 'insideLeft' }} />
                    <Tooltip 
                      formatter={(value: number) => [`${value}%`, "Precisión"]}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="score"
                      stroke="hsl(var(--primary))" 
                      strokeWidth={3}
                      dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 6 }}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                  <p>No hay datos de test disponibles. Completa el test inicial para ver tu progreso.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Accuracy Distribution */}
          <Card className="medical-card">
            <CardHeader>
              <CardTitle>Distribución de Respuestas</CardTitle>
            </CardHeader>
            <CardContent>
              {progressData && progressData.total_practice_attempts > 0 ? (
                <>
                  <div className="flex justify-center mb-6">
                    <ResponsiveContainer width={200} height={200}>
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          dataKey="value"
                          startAngle={90}
                          endAngle={450}
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value}%`, "Porcentaje"]} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Respuestas Correctas</span>
                      <span className="font-medium text-success">
                        {pieData[0].value}% ({progressData.total_practice_correct}/{progressData.total_practice_attempts})
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Respuestas Incorrectas</span>
                      <span className="font-medium text-destructive">
                        {pieData[1].value}% ({progressData.total_practice_attempts - progressData.total_practice_correct}/{progressData.total_practice_attempts})
                      </span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                  <p>No hay datos de práctica disponibles. Completa algunas preguntas para ver la distribución.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Arrhythmia Performance */}
          <Card className="medical-card">
            <CardHeader>
              <CardTitle>Rendimiento por Tipo de Arritmia</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {arrhythmiaStats.length === 0 ? (
                  <p className="text-sm text-muted-foreground">Sin datos por arritmia.</p>
                ) : arrhythmiaStats.filter(stat => stat.practice_total > 0 || stat.test_total > 0).map((stat, index) => (
                  <div key={index} className="space-y-3">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-sm font-medium capitalize">
                        {stat.name.replace(/_/g, " ")}
                      </span>
                    </div>
                    
                    {/* Barras lado a lado */}
                    <div className="grid grid-cols-2 gap-4">
                      {/* Practice Progress Bar */}
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-medium text-muted-foreground">Práctica</span>
                          <span className="text-xs font-medium text-muted-foreground">
                            {stat.practice_total > 0 ? `${stat.practice_correct}/${stat.practice_total}` : "N/A"}
                          </span>
                        </div>
                        {stat.practice_total > 0 ? (
                          <>
                            <ProgressBar 
                              value={stat.practice_accuracy} 
                              className="h-3 [&>div]:bg-blue-500"
                            />
                            <span className="text-xs text-muted-foreground text-center block">
                              {stat.practice_accuracy}%
                            </span>
                          </>
                        ) : (
                          <div className="h-3 bg-muted rounded-full" />
                        )}
                      </div>
                      
                      {/* Test Progress Bar */}
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-medium text-muted-foreground">Test</span>
                          <span className="text-xs font-medium text-muted-foreground">
                            {stat.test_total > 0 ? `${stat.test_correct}/${stat.test_total}` : "N/A"}
                          </span>
                        </div>
                        {stat.test_total > 0 ? (
                          <>
                            <ProgressBar 
                              value={stat.test_accuracy} 
                              className="h-3 [&>div]:bg-green-500"
                            />
                            <span className="text-xs text-muted-foreground text-center block">
                              {stat.test_accuracy}%
                            </span>
                          </>
                        ) : (
                          <div className="h-3 bg-muted rounded-full" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {arrhythmiaStats.filter(stat => stat.practice_total > 0 || stat.test_total > 0).length === 0 && (
                  <p className="text-sm text-muted-foreground">Sin datos por arritmia.</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Achievements/Badges */}
          <Card className="medical-card">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                <CardTitle>Insignias</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {badges.length === 0 ? (
                <div className="text-center p-6">
                  <Award className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Completa tests y práctica para desbloquear insignias
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {badges.map((badge, index) => (
                    <div 
                      key={index} 
                      className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                        badge.achieved
                          ? "border-success/20 bg-success/10"
                          : "border-muted/30 bg-muted/5 opacity-50"
                      }`}
                    >
                      <div>
                        <BadgeIcon 
                          iconName={badge.icon} 
                          isAchieved={badge.achieved}
                          className="w-6 h-6"
                        />
                      </div>
                      <div className="flex-1">
                        <h4 className={`font-medium ${badge.achieved ? "text-success" : "text-muted-foreground"}`}>
                          {badge.name}
                        </h4>
                        <p className="text-xs text-muted-foreground mb-1">{badge.description}</p>
                        {badge.achieved && badge.earned_at && (
                          <p className="text-xs text-success/70">
                            Desbloqueado: {new Date(badge.earned_at).toLocaleDateString('es-ES')}
                          </p>
                        )}
                        {!badge.achieved && (
                          <p className="text-xs text-muted-foreground/70">
                            Por conseguir
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Personalized Recommendations */}
        <Card className="medical-card mt-8">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <TrendingUp className="w-5 h-5 text-primary" />
              </div>
              <div>
                <CardTitle>Recomendaciones Personalizadas</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {recommendations?.has_llm ? "Análisis generado por IA basado en tu rendimiento" : "Análisis basado en tu rendimiento actual"}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {!recommendations ? (
              <div className="flex items-center justify-center h-[200px]">
                <p className="text-sm text-muted-foreground">Cargando recomendaciones personalizadas...</p>
              </div>
            ) : recommendations.recommendations ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-gradient-to-br from-primary/5 to-primary/10 rounded-lg border border-primary/20 hover:border-primary/40 transition-colors">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-4 h-4 text-primary" />
                      <p className="text-xs font-medium text-muted-foreground">Tests Completados</p>
                    </div>
                    <p className="text-3xl font-bold text-primary">{recommendations.test_attempts ?? 0}</p>
                  </div>
                  <div className="p-4 bg-gradient-to-br from-success/5 to-success/10 rounded-lg border border-success/20 hover:border-success/40 transition-colors">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-success" />
                      <p className="text-xs font-medium text-muted-foreground">Precisión General</p>
                    </div>
                    <p className="text-3xl font-bold text-success">{recommendations.overall_accuracy != null ? recommendations.overall_accuracy.toFixed(1) : "0.0"}%</p>
                  </div>
                  {(recommendations.weak_areas?.length ?? 0) > 0 && (
                    <div className="p-4 bg-gradient-to-br from-warning/5 to-warning/10 rounded-lg border border-warning/20 hover:border-warning/40 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-warning" />
                        <p className="text-xs font-medium text-muted-foreground">Áreas de Mejora</p>
                      </div>
                      <p className="text-3xl font-bold text-warning">{recommendations.weak_areas?.length ?? 0}</p>
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-foreground">Análisis y Sugerencias</h3>
                  <div className="p-6 bg-gradient-to-br from-blue-50/50 to-cyan-50/30 dark:from-blue-950/10 dark:to-cyan-950/10 rounded-lg border border-blue-200/30 dark:border-blue-800/30">
                    <div 
                      className="text-sm text-muted-foreground leading-relaxed [&>p]:mb-3 [&>ul]:ml-4 [&>ul]:space-y-2 [&>ol]:ml-4 [&>ol]:space-y-2 [&_li]:mb-1 [&_strong]:font-semibold [&_strong]:text-primary [&_em]:italic"
                      dangerouslySetInnerHTML={{ __html: recommendations.recommendations.replace(/^[\p{Emoji}]+\s*/u, '') }}
                    />
                  </div>
                </div>

                {(recommendations.weak_areas?.length ?? 0) > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-foreground">Enfoque tu estudio en:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {recommendations.weak_areas?.map((area, index) => (
                        <div 
                          key={index}
                          className="p-3 bg-warning/5 rounded-lg border border-warning/20 border-l-4 border-l-warning hover:bg-warning/10 transition-colors"
                        >
                          <p className="text-sm font-medium text-foreground capitalize">
                            {area.replace(/_/g, " ")}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center p-8">
                <Zap className="w-8 h-8 text-muted-foreground/40 mx-auto mb-3" />
                <p className="text-sm text-muted-foreground">Sin recomendaciones disponibles. Completa más tests para obtener análisis personalizados.</p>
              </div>
            )}
          </CardContent>
        </Card>
        </div>
      </main>
    </div>
  );
};

export default Progress;