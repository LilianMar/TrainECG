import { Heart, Upload, Brain, BarChart3, BookOpen, Target, CheckCircle2, TrendingUp } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import logo2 from "@/assets/logo2.png";
import { clearAccessToken } from "@/lib/auth";
import { useCallback, useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

interface UserData {
  initial_test_completed: boolean;
  skill_level: number | null;
}

interface DashboardStats {
  total_ecgs: number;
  avg_accuracy: number;
  consecutive_days: number;
}

interface DashboardProgress {
  total_ecgs_analyzed: number;
  total_practice_attempts: number;
  practice_accuracy: number;
  current_streak_days: number;
}

interface PracticeStats {
  total_attempts: number;
  correct_answers: number;
  accuracy_percentage: number;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserData | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [progress, setProgress] = useState<DashboardProgress | null>(null);
  const [practiceStats, setPracticeStats] = useState<PracticeStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUserData = useCallback(async () => {
    try {
      const [userResponse, statsResponse, progressResponse, practiceResponse] = await Promise.all([
        apiRequest<UserData>("/users/me"),
        apiRequest<DashboardStats>("/users/me/stats"),
        apiRequest<DashboardProgress>("/progress"),
        apiRequest<PracticeStats>("/practice/stats"),
      ]);
      setUser(userResponse);
      setStats(statsResponse);
      setProgress(progressResponse);
      setPracticeStats(practiceResponse);
    } catch (error) {
      console.error("Error loading user data:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  useEffect(() => {
    const handleRefresh = () => {
      loadUserData();
    };

    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        loadUserData();
      }
    };

    window.addEventListener("focus", handleRefresh);
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      window.removeEventListener("focus", handleRefresh);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [loadUserData]);

  const handleLogout = () => {
    clearAccessToken();
    navigate("/login");
  };

  // Mostrar test inicial si NO ha sido completado
  const initialTestFeature = {
    title: "Test Inicial",
    description: "Evalúa tu nivel actual de conocimientos",
    icon: Target,
    path: "/test",
    gradient: "bg-gradient-medical",
  };

  // Mostrar test de evaluación si HA sido completado
  const evaluationTestFeature = {
    title: "Test de Evaluación",
    description: "Evalúa tu progreso y obtén recomendaciones",
    icon: TrendingUp,
    path: "/test-evaluation",
    gradient: "bg-gradient-medical",
  };

  const baseFeatures = [
    {
      title: "Clasificar ECG",
      description: "Sube una imagen de ECG para análisis automático con IA",
      icon: Upload,
      path: "/classify",
      gradient: "bg-gradient-medical",
    },
    {
      title: "Modo Práctica",
      description: "Practica con casos reales y recibe retroalimentación",
      icon: Brain,
      path: "/practice",
      gradient: "bg-gradient-medical",
    },
    user?.initial_test_completed ? evaluationTestFeature : initialTestFeature,
    {
      title: "Mi Progreso",
      description: "Visualiza tu evolución y estadísticas",
      icon: BarChart3,
      path: "/progress",
      gradient: "bg-gradient-medical",
    },
    {
      title: "Biblioteca ECG",
      description: "Accede a casos de estudio y referencias",
      icon: BookOpen,
      path: "/library",
      gradient: "bg-gradient-medical",
    },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Header Section */}
      <section className="bg-gradient-hero relative overflow-hidden py-8">
        <div className="absolute inset-0 bg-gradient-to-r from-black/10 to-transparent" />
        
        {/* Top Navigation */}
        <div className="absolute top-4 right-6 z-20 flex items-center space-x-6">
          <Link to="/profile" className="text-white/90 hover:text-white transition-colors text-sm">
            Perfil
          </Link>
          <button 
            onClick={handleLogout} 
            className="text-white/90 hover:text-white transition-colors text-sm"
          >
            Cerrar Sesión
          </button>
        </div>
        
        {/* Compact Hero Content */}
        <div className="relative z-10 text-center px-8 max-w-4xl mx-auto pt-8">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-2xl p-2 mx-auto mb-6">
            <img src={logo2} alt="TrainECG Logo" className="w-full h-full object-contain" />
          </div>
          
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Mejora tus habilidades en ECG
          </h1>
          <p className="text-lg text-white/90 max-w-2xl mx-auto">
            Entrena con IA avanzada para interpretar electrocardiogramas y perfecciona tu diagnóstico médico
          </p>

          {/* Skill Level Badge */}
          {user?.initial_test_completed && user?.skill_level && (
            <div className="mt-8 flex items-center justify-center gap-2 bg-white/10 w-fit mx-auto px-6 py-3 rounded-full border border-white/20">
              <CheckCircle2 className="w-5 h-5 text-success" />
              <span className="text-white font-semibold">
                Tu nivel: <span className="text-accent">{user.skill_level}/5</span>
              </span>
            </div>
          )}
        </div>
      </section>

      {/* Main Content */}
      <main className="bg-gray-50/30 py-16">
        <div className="container mx-auto px-8 max-w-6xl">

          {/* Feature Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {baseFeatures.slice(0, 3).map((feature, index) => (
              <Link key={index} to={feature.path}>
                <Card className="medical-card-feature group h-full">
                  <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300 shadow-teal">
                      <feature.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Additional Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 max-w-4xl mx-auto">
            {baseFeatures.slice(3).map((feature, index) => (
              <Link key={index + 3} to={feature.path}>
                <Card className="medical-card-feature group h-full">
                  <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center mb-6 mx-auto group-hover:scale-110 transition-transform duration-300 shadow-teal">
                      <feature.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </main>

      {/* Stats Section */}
      <section className="bg-gradient-hero py-16">
        <div className="container mx-auto px-8 max-w-4xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center text-white">
              <div className="text-4xl font-bold mb-2">
                {progress ? progress.total_ecgs_analyzed : stats ? stats.total_ecgs : "--"}
              </div>
              <p className="text-white/90 text-sm">ECGs Analizados</p>
            </div>
            <div className="text-center text-white">
              <div className="text-4xl font-bold mb-2">
                {practiceStats ? practiceStats.total_attempts : progress ? progress.total_practice_attempts : "--"}
              </div>
              <p className="text-white/90 text-sm">Preguntas de Práctica</p>
            </div>
            <div className="text-center text-white">
              <div className="text-4xl font-bold mb-2">
                {user?.skill_level ? `${user.skill_level}/5` : "--"}
              </div>
              <p className="text-white/90 text-sm">Nivel Actual</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;