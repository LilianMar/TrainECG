import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Heart, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";
import { setAccessToken } from "@/lib/auth";
import logo1 from "@/assets/logo1.png";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await apiRequest<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: {
          email,
          password,
        },
      });

      setAccessToken(response.access_token);
      toast({
        title: "Bienvenido a TrainECG",
        description: "Has iniciado sesión exitosamente.",
        variant: "success",
      });
      navigate("/dashboard");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Error de autenticación";
      toast({
        title: "Error de autenticación",
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
          <div className="w-32 h-32 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-teal p-4">
            <img src={logo1} alt="TrainECG Logo" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">TrainECG</h1>
          <p className="text-white/80">Plataforma de aprendizaje médico</p>
        </div>

        {/* Login Form */}
        <Card className="medical-card">
          <CardHeader>
            <CardTitle className="text-2xl text-center text-foreground">
              Iniciar Sesión
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Correo Electrónico
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="doctor@ejemplo.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  Contraseña
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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

              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2 text-sm">
                  <input type="checkbox" className="rounded border-border" />
                  <span className="text-muted-foreground">Recordarme</span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm text-primary hover:underline"
                >
                  ¿Olvidaste tu contraseña?
                </Link>
              </div>

              <Button
                type="submit"
                className="w-full btn-medical"
                disabled={isLoading}
              >
                {isLoading ? "Iniciando sesión..." : "Iniciar Sesión"}
              </Button>

              <div className="text-center">
                <span className="text-muted-foreground text-sm">
                  ¿No tienes cuenta?{" "}
                  <Link to="/register" className="text-primary hover:underline">
                    Regístrate aquí
                  </Link>
                </span>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;