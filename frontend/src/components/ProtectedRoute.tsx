import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getAccessToken, isTokenValid } from "@/lib/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const [isValid, setIsValid] = useState<boolean | null>(null);

  useEffect(() => {
    const validateToken = async () => {
      const token = getAccessToken();
      
      if (!token) {
        setIsValid(false);
        return;
      }

      const valid = await isTokenValid(token);
      setIsValid(valid);
    };

    validateToken();
  }, []);

  // Show loading state while validating
  if (isValid === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Redirect to login if token is invalid
  if (!isValid) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
