import { Heart } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Terms = () => {
  return (
    <div className="min-h-screen bg-gradient-hero p-6 md:p-10">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-medical">
            <Heart className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Términos y Condiciones</h1>
          <p className="text-white/85">TrainECG - versión sencilla y clara</p>
        </div>

        <Card className="medical-card">
          <CardHeader>
            <CardTitle className="text-xl md:text-2xl text-foreground">Uso responsable de la plataforma</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5 text-sm md:text-base text-foreground/90 leading-relaxed">
            <section>
              <h2 className="font-semibold text-foreground mb-1">1. Propósito educativo</h2>
              <p>
                TrainECG es una herramienta de apoyo para aprendizaje e interpretación de ECG. No reemplaza el juicio
                clínico ni una evaluación médica profesional.
              </p>
            </section>

            <section>
              <h2 className="font-semibold text-foreground mb-1">2. Cuenta y acceso</h2>
              <p>
                Debes proporcionar información veraz en tu registro y mantener tu contraseña de forma confidencial. Eres
                responsable de la actividad que ocurra en tu cuenta.
              </p>
            </section>

            <section>
              <h2 className="font-semibold text-foreground mb-1">3. Uso permitido</h2>
              <p>
                Puedes usar la plataforma para estudiar, practicar y mejorar tus competencias. No está permitido usar
                TrainECG para actividades ilegales, para intentar vulnerar la seguridad del sistema o para copiar su
                contenido con fines no autorizados.
              </p>
            </section>

            <section>
              <h2 className="font-semibold text-foreground mb-1">4. Limitación de responsabilidad</h2>
              <p>
                Los resultados, recomendaciones y análisis automáticos son orientativos. La decisión final en un caso
                clínico siempre corresponde al profesional de salud.
              </p>
            </section>

            <section>
              <h2 className="font-semibold text-foreground mb-1">5. Privacidad de datos</h2>
              <p>
                Tratamos tus datos con medidas de seguridad razonables y solo para el funcionamiento académico de
                TrainECG. Te recomendamos no ingresar información sensible de pacientes que permita su identificación.
              </p>
            </section>

            <section>
              <h2 className="font-semibold text-foreground mb-1">6. Cambios en estos términos</h2>
              <p>
                Podemos actualizar estos términos cuando sea necesario. Si hay cambios importantes, se reflejarán en esta
                misma página.
              </p>
            </section>

            <section>
              <h2 className="font-semibold text-foreground mb-1">7. Aceptación</h2>
              <p>
                Al registrarte y usar TrainECG, confirmas que leíste y aceptaste estos términos y condiciones.
              </p>
            </section>

            <p className="text-xs text-muted-foreground pt-2">Última actualización: 16 de abril de 2026.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Terms;
