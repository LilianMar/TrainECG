import { useState, useCallback } from "react";
import { Upload, FileImage, Brain, AlertCircle, CheckCircle, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";

const ClassifyECG = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<{
    arrhythmia: string;
    confidence: number;
    recommendations: string[];
    explanation: string;
    annotated_image?: string;
  } | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [isDragActive, setIsDragActive] = useState(false);
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files && files[0]) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        setUploadedFile(file);
      } else {
        toast({
          title: "Formato no válido",
          description: "Por favor, sube una imagen (JPG, PNG, etc.)",
          variant: "destructive",
        });
      }
    }
  }, [toast]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      setUploadedFile(files[0]);
    }
  };

  const analyzeECG = async () => {
    if (!uploadedFile) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append("file", uploadedFile);

    // Simulate analysis progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const response = await apiRequest<{
        predicted_class: string;
        confidence: number;
        llm_explanation: string;
        annotated_image?: string;
      }>("/ecg/classify", {
        method: "POST",
        body: formData,
        isForm: true,
      });

      const classLabels: Record<string, string> = {
        normal: "Ritmo Sinusal Normal",
        atrial_fibrillation: "Fibrilacion Auricular",
        ventricular_tachycardia: "Taquicardia Ventricular",
        av_block: "Bloqueo AV",
        atrial_flutter: "Flutter Auricular",
        supraventricular_ectopic: "Latido Ectópico Supraventricular",
        ventricular_ectopic: "Latido Ectópico Ventricular",
        fusion: "Latido de Fusión",
        unknown: "Latido No Clasificable",
        paced: "Latido con Marcapasos",
      };

      const arrhythmiaLabel = classLabels[response.predicted_class] ?? response.predicted_class;

      setAnalysisResult({
        arrhythmia: arrhythmiaLabel,
        confidence: Number((response.confidence * 100).toFixed(1)),
        recommendations: [
          "Revisar el trazado con contexto clinico",
          "Correlacionar con sintomas del paciente",
          "Consultar con un especialista si hay dudas",
        ],
        explanation: response.llm_explanation || "Sin explicacion adicional disponible.",
        annotated_image: response.annotated_image,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "No se pudo analizar el ECG";
      toast({
        title: "Error en el analisis",
        description: message,
        variant: "destructive",
      });
    } finally {
      clearInterval(progressInterval);
      setAnalysisProgress(100);
      setIsAnalyzing(false);
    }
  };

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
            <h1 className="text-2xl font-bold text-white">Clasificación de ECG</h1>
          </div>
        </div>
      </header>

      <main className="bg-gray-50/30 py-8">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Upload className="w-5 h-5 mr-2 text-primary" />
                  Subir ECG
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!uploadedFile ? (
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                      isDragActive
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                  >
                    <FileImage className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg font-medium text-foreground mb-2">
                      Arrastra tu ECG aquí
                    </p>
                    <p className="text-muted-foreground mb-4">
                      O haz clic para seleccionar un archivo
                    </p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload">
                      <Button className="btn-medical" asChild>
                        <span>Seleccionar Archivo</span>
                      </Button>
                    </label>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-success" />
                      <span className="font-medium">Archivo cargado: {uploadedFile.name}</span>
                    </div>
                    
                    {uploadedFile && (
                      <img
                        src={URL.createObjectURL(uploadedFile)}
                        alt="ECG Preview"
                        className="w-full h-48 object-contain bg-secondary rounded-lg"
                      />
                    )}
                    
                    <div className="flex space-x-3">
                      <Button
                        onClick={analyzeECG}
                        disabled={isAnalyzing}
                        className="btn-medical flex-1"
                      >
                        <Brain className="w-4 h-4 mr-2" />
                        {isAnalyzing ? "Analizando..." : "Analizar ECG"}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setUploadedFile(null)}
                        disabled={isAnalyzing}
                      >
                        Cambiar
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Analysis Progress */}
            {isAnalyzing && (
              <Card className="medical-card">
                <CardContent className="p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <Brain className="w-5 h-5 text-primary animate-pulse" />
                    <span className="font-medium">Analizando ECG con IA...</span>
                  </div>
                  <Progress value={analysisProgress} className="w-full" />
                  <p className="text-sm text-muted-foreground mt-2">
                    {analysisProgress}% completado
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {analysisResult ? (
              <>
                <Card className="medical-card border-primary/20 bg-primary/5">
                  <CardHeader>
                    <CardTitle className="flex items-center text-primary">
                      <AlertCircle className="w-5 h-5 mr-2" />
                      Resultado del Análisis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-lg">{analysisResult.arrhythmia}</h3>
                      <p className="text-muted-foreground">
                        Confianza: {analysisResult.confidence}%
                      </p>
                    </div>
                    
                    {/* Display annotated image if available */}
                    {analysisResult.annotated_image && (
                      <div className="p-4 bg-secondary rounded-lg">
                        <h4 className="font-medium mb-3 text-sm">
                          📊 ECG Analizado - Regiones de Detección Encerradas (Rectángulos Rojos)
                        </h4>
                        <img
                          src={`data:image/png;base64,${analysisResult.annotated_image}`}
                          alt="ECG Anotado con Arritmias"
                          className="w-full h-auto rounded-lg border border-border"
                          style={{ maxHeight: '400px', objectFit: 'contain' }}
                        />
                        <p className="text-xs text-muted-foreground mt-2">
                          Los rectángulos rojos indican las regiones donde el modelo detectó el patrón de &quot;{analysisResult.arrhythmia}&quot;.
                          El porcentaje en cada rectángulo es la confianza del modelo para esa ventana.
                        </p>
                      </div>
                    )}
                    
                    <div className="p-4 bg-secondary rounded-lg">
                      <h4 className="font-medium mb-2">Explicación Clínica:</h4>
                      <p className="text-sm text-muted-foreground">
                        {analysisResult.explanation}
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Recomendaciones:</h4>
                      <ul className="space-y-1">
                        {analysisResult.recommendations.map((rec: string, index: number) => (
                          <li key={index} className="text-sm text-muted-foreground flex items-start">
                            <span className="text-primary mr-2">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="medical-card">
                <CardContent className="p-8 text-center">
                  <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="font-medium text-foreground mb-2">
                    Análisis con IA Avanzada
                  </h3>
                  <p className="text-muted-foreground">
                    Sube un ECG para obtener un análisis detallado con explicaciones clínicas 
                    y recomendaciones personalizadas.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ClassifyECG;