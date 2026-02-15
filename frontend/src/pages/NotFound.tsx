import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Heart, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gradient-hero flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-medical">
          <Heart className="w-8 h-8 text-primary" />
        </div>
        
        <h1 className="text-6xl font-bold text-white mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-white mb-4">Página No Encontrada</h2>
        <p className="text-white/80 mb-8">
          Lo sentimos, la página que buscas no existe o ha sido movida.
        </p>
        
        <Link to="/dashboard">
          <Button className="btn-medical">
            <Home className="w-4 h-4 mr-2" />
            Volver al Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
