import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Heart, Mail, Lock, User, GraduationCap, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";
import { setAccessToken } from "@/lib/auth";

const Register = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    userType: "",
    institution: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Error en contraseñas",
        description: "Las contraseñas no coinciden.",
        variant: "destructive",
      });
      return;
    }

    if (!formData.name || !formData.email || !formData.password || !formData.userType) {
      toast({
        title: "Campos requeridos",
        description: "Por favor, completa todos los campos obligatorios.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiRequest<{ access_token: string }>("/auth/register", {
        method: "POST",
        body: {
          name: formData.name,
          email: formData.email,
          password: formData.password,
          user_type: formData.userType,
          institution: formData.institution || null,
        },
      });

      setAccessToken(response.access_token);
      toast({
        title: "¡Registro exitoso!",
        description: "Tu cuenta ha sido creada. Bienvenido a TrainECG.",
      });
      navigate("/dashboard");
    } catch (error) {
      const message = error instanceof Error ? error.message : "No se pudo crear la cuenta";
      toast({
        title: "Registro fallido",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-hero flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-medical">
            <Heart className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">TrainECG</h1>
          <p className="text-white/80">Crea tu cuenta para comenzar</p>
        </div>

        {/* Registration Form */}
        <Card className="medical-card">
          <CardHeader>
            <CardTitle className="text-2xl text-center text-foreground">
              Registrarse
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Nombre Completo *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Dr. Juan Pérez"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Correo Electrónico *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="doctor@ejemplo.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Tipo de Usuario *
                </label>
                <Select onValueChange={(value) => handleInputChange("userType", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona tu perfil" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="student">Estudiante de Medicina</SelectItem>
                    <SelectItem value="resident">Médico Residente</SelectItem>
                    <SelectItem value="doctor">Médico Especialista</SelectItem>
                    <SelectItem value="nurse">Enfermero/a</SelectItem>
                    <SelectItem value="other">Otro Profesional de Salud</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Institución (Opcional)
                </label>
                <div className="relative">
                  <GraduationCap className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Universidad / Hospital"
                    value={formData.institution}
                    onChange={(e) => handleInputChange("institution", e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Contraseña *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Confirmar Contraseña *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="flex items-start space-x-2 pt-2">
                <input 
                  type="checkbox" 
                  className="rounded border-border mt-1" 
                  required 
                />
                <label className="text-xs text-muted-foreground">
                  Acepto los{" "}
                  <Link to="/terms" className="text-primary hover:underline">
                    términos y condiciones
                  </Link>
                  {" "}y la{" "}
                  <Link to="/privacy" className="text-primary hover:underline">
                    política de privacidad
                  </Link>
                </label>
              </div>

              <Button
                type="submit"
                className="w-full btn-medical"
                disabled={isLoading}
              >
                {isLoading ? "Creando cuenta..." : "Crear Cuenta"}
              </Button>

              <div className="text-center">
                <span className="text-muted-foreground text-sm">
                  ¿Ya tienes cuenta?{" "}
                  <Link to="/login" className="text-primary hover:underline">
                    Inicia sesión aquí
                  </Link>
                </span>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Privacy Note */}
        <Card className="mt-4 bg-secondary/50">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">
              🔒 Tus datos están protegidos con encriptación de grado médico y cumplimos 
              con las normas de privacidad en salud.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Register;