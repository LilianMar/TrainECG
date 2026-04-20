import { Link, useNavigate } from "react-router-dom";
import {
  Activity,
  Brain,
  Eye,
  Target,
  BookOpen,
  MessageCircle,
  ArrowRight,
  ShieldCheck,
  Clock,
  GraduationCap,
  TrendingUp,
} from "lucide-react";
import logoHeart from "@/assets/logoTrainECG-heart.png";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  variant: "primary" | "teal";
}

function FeatureCard({ icon, title, description, variant }: FeatureCardProps) {
  const iconBg =
    variant === "primary"
      ? "bg-primary/10 text-primary group-hover:bg-primary/15"
      : "bg-success/10 text-success group-hover:bg-success/15";

  return (
    <div className="group p-7 rounded-2xl bg-white border border-border hover:border-success/40 hover:shadow-teal transition-all duration-300">
      <div
        className={`w-11 h-11 rounded-[10px] mb-5 flex items-center justify-center transition-all duration-300 group-hover:scale-105 ${iconBg}`}
      >
        {icon}
      </div>
      <h3 className="text-[15px] font-semibold text-foreground mb-2 tracking-tight group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-sm text-muted-foreground leading-relaxed">
        {description}
      </p>
    </div>
  );
}

function FeaturesSection() {
  const features: FeatureCardProps[] = [
    {
      icon: <Brain className="w-5 h-5" />,
      title: "Clasificación con IA",
      description:
        "Modelo CNN-LSTM con atención que identifica latidos normales, ectópicos supraventriculares, ventriculares y de fusión a partir de imágenes de ECG.",
      variant: "primary",
    },
    {
      icon: <Eye className="w-5 h-5" />,
      title: "Grad-CAM Explicable",
      description:
        "Visualiza con mapas de calor las regiones del trazado que el modelo consideró relevantes para su predicción, facilitando la interpretación clínica.",
      variant: "teal",
    },
    {
      icon: <Target className="w-5 h-5" />,
      title: "Modo Práctica",
      description:
        "Resuelve casos clínicos reales con preguntas de selección múltiple, retroalimentación inmediata y explicaciones detalladas por arritmia.",
      variant: "primary",
    },
    {
      icon: <TrendingUp className="w-5 h-5" />,
      title: "Evaluación Adaptativa",
      description:
        "Test inicial y post-práctica que ajusta tu nivel de habilidad y prioriza las arritmias en las que necesitas reforzar.",
      variant: "teal",
    },
    {
      icon: <BookOpen className="w-5 h-5" />,
      title: "Biblioteca Clínica",
      description:
        "Catálogo de arritmias con criterios diagnósticos, características electrocardiográficas y manejo terapéutico de referencia.",
      variant: "primary",
    },
    {
      icon: <MessageCircle className="w-5 h-5" />,
      title: "Asistente Educativo",
      description:
        "Chatbot integrado con corpus médico curado que resuelve dudas sobre interpretación de ECG en cualquier momento de tu estudio.",
      variant: "teal",
    },
  ];

  return (
    <section id="features" className="py-24 bg-muted/30">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-14">
          <h2 className="text-[36px] md:text-[48px] font-semibold tracking-tight text-foreground mb-4">
            Una plataforma integral
          </h2>
          <p className="text-base text-muted-foreground max-w-xl mx-auto leading-relaxed">
            Herramientas diseñadas para acompañarte desde tus primeras lecturas
            de ECG hasta la práctica clínica avanzada.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature, idx) => (
            <FeatureCard key={idx} {...feature} />
          ))}
        </div>
      </div>
    </section>
  );
}

function StatsSection() {
  const stats = [
    { value: "6", label: "Tipos de latidos clasificados" },
    { value: "20+", label: "Casos clínicos de práctica" },
    { value: "5", label: "Niveles de habilidad" },
    { value: "24/7", label: "Asistente disponible" },
  ];

  return (
    <section className="py-16 bg-gradient-hero relative overflow-hidden">
      <div className="absolute top-0 right-0 w-96 h-96 bg-success/15 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-white/8 rounded-full blur-[80px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
          {stats.map((stat, idx) => (
            <div key={idx} className="text-center">
              <div className="text-[36px] md:text-[52px] font-semibold text-white tracking-tight leading-none mb-2">
                {stat.value}
              </div>
              <p className="text-white/75 text-sm">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute -top-40 right-0 w-[480px] h-[480px] bg-success/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute -bottom-40 left-0 w-[360px] h-[360px] bg-primary/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-3xl mx-auto px-6 text-center relative z-10">
        <h2 className="text-[36px] md:text-[48px] font-semibold tracking-tight text-foreground mb-5">
          Comienza tu entrenamiento hoy
        </h2>
        <p className="text-base text-muted-foreground mb-10 max-w-xl mx-auto leading-relaxed">
          Únete a estudiantes y profesionales de la salud que están afinando
          su criterio para la lectura de electrocardiogramas con apoyo de
          inteligencia artificial.
        </p>
        <Link
          to="/register"
          className="inline-flex items-center gap-2 px-7 py-3.5 bg-primary hover:bg-primary-hover text-primary-foreground text-sm font-semibold rounded-[10px] shadow-medical hover:shadow-teal hover:-translate-y-px transition-all duration-200"
        >
          Crear cuenta gratis
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </section>
  );
}

function Footer() {
  const links = [
    {
      heading: "Plataforma",
      items: [
        { label: "Características", href: "#features" },
        { label: "Iniciar sesión", href: "/login" },
        { label: "Registrarse", href: "/register" },
      ],
    },
    {
      heading: "Recursos",
      items: [
        { label: "Biblioteca de arritmias", href: "/login" },
        { label: "Modo práctica", href: "/login" },
        { label: "Evaluación", href: "/login" },
      ],
    },
    {
      heading: "Legal",
      items: [
        { label: "Términos y condiciones", href: "/terms" },
      ],
    },
  ];

  return (
    <footer className="bg-foreground text-white/70 py-14">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-3">
              <img src={logoHeart} alt="TrainECG" className="w-8 h-8 object-contain" />
              <span className="text-base font-semibold text-white">TrainECG</span>
            </div>
            <p className="text-xs text-white/60 leading-relaxed max-w-xs">
              Plataforma educativa para el entrenamiento en interpretación de
              electrocardiogramas con apoyo de inteligencia artificial.
            </p>
          </div>

          {links.map(({ heading, items }) => (
            <div key={heading}>
              <h3 className="text-xs font-semibold text-white mb-4 tracking-widest uppercase">
                {heading}
              </h3>
              <ul className="space-y-2.5">
                {items.map((item) => (
                  <li key={item.label}>
                    {item.href.startsWith("#") ? (
                      <a
                        href={item.href}
                        className="text-sm text-white/60 hover:text-success transition-colors"
                      >
                        {item.label}
                      </a>
                    ) : (
                      <Link
                        to={item.href}
                        className="text-sm text-white/60 hover:text-success transition-colors"
                      >
                        {item.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-white/10 pt-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-white/50">
            TrainECG — Trabajo de tesis, Universidad de San Buenaventura Cali.
          </p>
          <p className="text-xs text-white/40">
            Herramienta educativa. No sustituye el criterio médico profesional.
          </p>
        </div>
      </div>
    </footer>
  );
}

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-secondary/40 to-accent/30">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 border-b border-border/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center shadow-medical p-1.5">
              <img src={logoHeart} alt="TrainECG" className="w-full h-full object-contain" />
            </div>
            <span className="text-lg font-bold bg-gradient-primary bg-clip-text text-transparent">
              TrainECG
            </span>
          </Link>

          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="hidden sm:inline-flex px-4 py-2 text-sm font-semibold text-primary hover:bg-primary/5 rounded-lg transition-all"
            >
              Iniciar sesión
            </Link>
            <button
              onClick={() => navigate("/register")}
              className="px-5 py-2.5 bg-primary text-primary-foreground text-sm font-semibold rounded-lg hover:bg-primary-hover transition-all duration-200 shadow-medical hover:shadow-teal"
            >
              Registrarse
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative py-24 md:py-32 overflow-hidden">
        <div className="absolute top-0 right-0 w-[480px] h-[480px] bg-success/10 rounded-full blur-[120px] -z-10" />
        <div className="absolute bottom-0 left-0 w-[360px] h-[360px] bg-primary/10 rounded-full blur-[100px] -z-10" />

        <div className="max-w-5xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 bg-success/10 border border-success/30 rounded-full text-xs font-semibold tracking-widest uppercase text-success">
            <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            Plataforma educativa con IA
          </div>

          <h1 className="text-[42px] md:text-[68px] font-bold leading-[1.08] tracking-tight text-foreground mb-6">
            Aprende a interpretar
            <br />
            <span className="bg-gradient-primary bg-clip-text text-transparent">
              electrocardiogramas
            </span>
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg md:text-xl text-muted-foreground leading-relaxed">
            Entrena tu criterio clínico con clasificación automática, mapas de
            atención Grad-CAM, casos prácticos y un asistente educativo
            disponible las 24 horas.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center mb-14">
            <button
              onClick={() => navigate("/register")}
              className="inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-primary hover:bg-primary-hover text-primary-foreground font-semibold rounded-[10px] shadow-medical hover:shadow-teal hover:-translate-y-px transition-all duration-200"
            >
              Empezar ahora
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate("/login")}
              className="inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-white text-primary font-semibold rounded-[10px] border-2 border-primary/20 hover:border-primary/40 hover:bg-primary/5 transition-all duration-200 shadow-card"
            >
              <Activity className="w-4 h-4" />
              Ya tengo cuenta
            </button>
          </div>

          <div className="flex items-center justify-center flex-wrap gap-x-6 gap-y-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-success" />
              Datos privados y seguros
            </div>
            <span className="hidden sm:inline w-1 h-1 rounded-full bg-border" />
            <div className="flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-success" />
              Resultados en segundos
            </div>
            <span className="hidden sm:inline w-1 h-1 rounded-full bg-border" />
            <div className="flex items-center gap-2">
              <GraduationCap className="w-3.5 h-3.5 text-success" />
              Diseñado para estudiantes y profesionales
            </div>
          </div>
        </div>
      </section>

      <FeaturesSection />
      <StatsSection />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Landing;
