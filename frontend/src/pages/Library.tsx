import { AlertCircle, ArrowLeft, BookOpen, Heart, Zap } from "lucide-react";
import {
  MdAutorenew,
  MdBlock,
  MdFlashOn,
  MdPauseCircleFilled,
  MdPauseCircleOutline,
  MdReportProblem,
  MdTimeline,
  MdTrendingUp,
} from "react-icons/md";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Library = () => {
  const ecgSteps = [
    {
      order: 1,
      title: "Calcular Frecuencia Cardiaca",
      description: "Método de regla 1500 o papel ECG",
      details: [
        "Contar cuadros grandes entre dos ondas R consecutivas",
        "Dividir 1500 entre el número de cuadros = FC (si papel a 25 mm/s)",
        "Rango normal: 60-100 lpm en reposo",
      ],
    },
    {
      order: 2,
      title: "Evaluar el Ritmo",
      description: "¿Es regular o irregular?",
      details: [
        "Ritmo regular: intervalos RR iguales",
        "Ritmo irregular: intervalos RR variables",
        "Ritmo sinusal: ondas P positivas en DII antes de cada QRS",
      ],
    },
    {
      order: 3,
      title: "Análisis del Eje Eléctrico",
      description: "Dirección de propagación eléctrica",
      details: [
        "Eje normal: -30° a +90°",
        "Desviación izquierda: -30° a -90°",
        "Desviación derecha: +90° a +180°",
        "Usar derivaciones DI y aVF para determinar",
      ],
    },
    {
      order: 4,
      title: "Duración de Complejos",
      description: "Ancho de QRS",
      details: [
        "QRS normal: <120 ms (3 cuadros pequeños)",
        "QRS ancho: ≥120 ms → sugiere bloqueo de rama",
        "Medir desde inicio Q hasta fin S",
      ],
    },
    {
      order: 5,
      title: "Segmento ST e Intervalo QT",
      description: "Isquemia y repolarización",
      details: [
        "ST normal: a nivel de línea basal",
        "ST elevado (>1 mm): infarto STEMI",
        "ST deprimido: isquemia/infarto subendocárdico",
        "QT normal: <440 ms (varía con FC)",
      ],
    },
    {
      order: 6,
      title: "Identificar Patología",
      description: "Integrar todos los hallazgos",
      details: [
        "Infarto: ST el, ondas Q, alteraciones T",
        "Bloqueos: QRS ancho, cambios PR",
        "Arritmias: alteraciones de ritmo/ondas P",
        "Hipertrofia: voltaje aumentado",
      ],
    },
  ];

  const arrhythmias = [
    {
      name: "Fibrilación Auricular",
      type: "Supraventricular",
      icon: MdTimeline,
      fc: "60-180 lpm",
      ecg: "Ausencia de P, ritmo irregular, ondas f",
      causes: "HTA, cardiopatía, tirotoxicosis, embolia",
      severity: "Media",
    },
    {
      name: "Flutter Auricular",
      type: "Supraventricular",
      icon: MdAutorenew,
      fc: "140-180 lpm",
      ecg: "Ondas F en diente de sierra, ritmo regular",
      causes: "HTA, cardiopatía, post-quirúrgica",
      severity: "Media",
    },
    {
      name: "Taquicardia Supraventricular",
      type: "Supraventricular",
      icon: MdTrendingUp,
      fc: "150-250 lpm",
      ecg: "Ritmo regular, P retrógrada o escondida en QRS",
      causes: "Vías accesorias, reentrada nodal",
      severity: "Media",
    },
    {
      name: "Taquicardia Ventricular",
      type: "Ventricular",
      icon: MdFlashOn,
      fc: "120-300 lpm",
      ecg: "QRS ancho, fusión/captura, AV disociación",
      causes: "Cardiopatía isquémica, cardiomiopatía",
      severity: "Alta",
    },
    {
      name: "Fibrilación Ventricular",
      type: "Ventricular",
      icon: MdReportProblem,
      fc: "No medible",
      ecg: "Sin complejo definido, línea basal irregular",
      causes: "Infarto, electrocución, hipotermia",
      severity: "Crítica",
    },
    {
      name: "Bloqueo AV Grado I",
      type: "Bradiarritmia",
      icon: MdPauseCircleOutline,
      fc: "60-100 lpm",
      ecg: "PR prolongado (>200 ms), todos los P conducen",
      causes: "Vagal, isquemia, fármacos (digoxina)",
      severity: "Baja",
    },
    {
      name: "Bloqueo AV Grado II Mobitz I",
      type: "Bradiarritmia",
      icon: MdPauseCircleFilled,
      fc: "40-80 lpm",
      ecg: "PR progresivamente prolongado, P bloqueada",
      causes: "Isquemia de nodo AV, vagal",
      severity: "Media",
    },
    {
      name: "Bloqueo AV Completo",
      type: "Bradiarritmia",
      icon: MdBlock,
      fc: "30-50 lpm",
      ecg: "P y QRS independientes, ritmo de escape",
      causes: "Infarto, degeneración, post-quirúrgica",
      severity: "Alta",
    },
  ];

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
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <BookOpen className="w-6 h-6" />
              Biblioteca ECG
            </h1>
          </div>
        </div>
      </header>

      <main className="bg-gray-50/30 py-8">
        <div className="container mx-auto px-6 max-w-6xl">
          <Tabs defaultValue="guide" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="guide">Guía de Interpretación</TabsTrigger>
            <TabsTrigger value="arrhythmias">Tipos de Arritmias</TabsTrigger>
          </TabsList>

          {/* Guide Tab */}
          <TabsContent value="guide" className="space-y-6">
            <Card className="medical-card-feature bg-gradient-to-r from-primary/5 to-primary/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="w-5 h-5 text-primary" />
                  Pasos para Leer un ECG
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Sigue estos 6 pasos en orden para realizar una interpretación completa y sistemática de cualquier electrocardiograma.
                </p>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {ecgSteps.map((step) => (
                <Card key={step.order} className="medical-card-feature group h-full">
                  <CardContent className="p-8">
                    <div className="flex flex-col items-center text-center">
                      <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center mb-4 shadow-teal">
                        <span className="text-white text-xl font-bold">{step.order}</span>
                      </div>
                      <h3 className="text-xl font-semibold text-foreground mb-2">{step.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">{step.description}</p>
                    </div>
                    <ul className="space-y-2 mt-4 text-left">
                      {step.details.map((detail, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                          <span className="text-sm text-foreground">{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Tips Card */}
            <Card className="medical-card-feature group h-full">
              <CardContent className="p-8">
                <div className="flex flex-col items-center text-center mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center mb-4 shadow-teal">
                    <Zap className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground">Consejos Aplicables</h3>
                  <p className="text-muted-foreground mt-1">Guías rápidas para interpretar con confianza</p>
                </div>
                <div className="space-y-3">
                <div className="flex gap-3">
                  <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-sm">Siempre contextualizar</p>
                    <p className="text-sm text-muted-foreground">Correlaciona ECG con síntomas, signos vitales e historia clínica</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-sm">Comparar con previos</p>
                    <p className="text-sm text-muted-foreground">Los cambios dinámicos son más significativos que hallazgos aislados</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-sm">Método sistemático</p>
                    <p className="text-sm text-muted-foreground">No saltes pasos; la interpretación metódica previene errores</p>
                  </div>
                </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Arrhythmias Tab */}
          <TabsContent value="arrhythmias" className="space-y-6">
            <Card className="medical-card-feature bg-gradient-to-r from-primary/5 to-primary/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="w-5 h-5 text-primary" />
                  Arritmias Cardiacas Comunes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Las arritmias se clasifican en supraventriculares, ventriculares y bradiarritmias según su origen.
                </p>
              </CardContent>
            </Card>

            <div className="grid gap-4">
              {arrhythmias.map((arr, idx) => (
                <Card key={idx} className="medical-card-feature group">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-teal">
                            <arr.icon className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold">{arr.name}</h3>
                            <p className="text-xs text-muted-foreground">{arr.type}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          arr.severity === "Crítica" ? "bg-red-200 text-red-900" :
                          arr.severity === "Alta" ? "bg-orange-200 text-orange-900" :
                          arr.severity === "Media" ? "bg-yellow-200 text-yellow-900" :
                          "bg-blue-200 text-blue-900"
                        }`}>
                          {arr.severity}
                        </span>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground font-semibold">Frecuencia:</p>
                        <p className="text-foreground">{arr.fc}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground font-semibold">ECG:</p>
                        <p className="text-foreground">{arr.ecg}</p>
                      </div>
                      <div className="md:col-span-2">
                        <p className="text-muted-foreground font-semibold">Causas comunes:</p>
                        <p className="text-foreground">{arr.causes}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
        </div>
      </main>
    </div>
  );
};

export default Library;
