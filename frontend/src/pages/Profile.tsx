import { useEffect, useState } from "react";
import { ArrowLeft, User, Mail, GraduationCap, Calendar, Edit, Settings } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { apiRequest } from "@/lib/api";

const Profile = () => {
  const [userProfile, setUserProfile] = useState<{
    name: string;
    email: string;
    userType: string;
    institution?: string | null;
    joinDate: string;
    location: string;
    specialization: string;
    avatar: string;
  } | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await apiRequest<{
          name: string;
          email: string;
          user_type: string;
          institution?: string | null;
          created_at: string;
        }>("/users/me");

        const createdAt = new Date(response.created_at);
        const joinDate = createdAt.toLocaleDateString("es-CO", {
          year: "numeric",
          month: "long",
        });

        setUserProfile({
          name: response.name,
          email: response.email,
          userType: response.user_type,
          institution: response.institution ?? "",
          joinDate,
          location: "",
          specialization: "",
          avatar: "/api/placeholder/120/120",
        });
      } catch {
        setUserProfile(null);
      }
    };

    loadProfile();
  }, []);

  const stats = [
    { label: "ECGs Analizados", value: "124", color: "text-primary" },
    { label: "Precisión Promedio", value: "87%", color: "text-success" },
    { label: "Días Consecutivos", value: "12", color: "text-warning" },
    { label: "Rango Actual", value: "Avanzado", color: "text-foreground" }
  ];

  const recentActivity = [
    {
      date: "Hoy",
      activity: "Completó práctica de Fibrilación Auricular",
      score: "9/10 correctas"
    },
    {
      date: "Ayer",
      activity: "Analizó 5 ECGs con IA",
      score: "85% precisión"
    },
    {
      date: "2 días",
      activity: "Completó módulo de Taquicardias",
      score: "Certificado obtenido"
    }
  ];

  const preferences = [
    { setting: "Notificaciones diarias", enabled: true },
    { setting: "Recordatorios de práctica", enabled: true },
    { setting: "Informes semanales", enabled: false },
    { setting: "Modo oscuro", enabled: false }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-foreground">Mi Perfil</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="medical-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Información Personal</CardTitle>
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-start space-x-6">
                  <Avatar className="w-24 h-24">
                    <AvatarImage src={userProfile?.avatar || ""} alt={userProfile?.name || ""} />
                    <AvatarFallback className="text-2xl font-bold bg-gradient-medical text-white">
                      {userProfile?.name.split(' ').map(n => n[0]).join('') || ""}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 space-y-4">
                    <div>
                      <h2 className="text-2xl font-bold text-foreground mb-1">
                        {userProfile?.name || "Usuario"}
                      </h2>
                      <Badge variant="secondary" className="mb-2">
                        {userProfile?.userType || ""}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Mail className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">{userProfile?.email || ""}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <GraduationCap className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">{userProfile?.institution || ""}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">Miembro desde {userProfile?.joinDate || ""}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <User className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">{userProfile?.specialization || ""}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Statistics */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle>Estadísticas de Rendimiento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {stats.map((stat, index) => (
                    <div key={index} className="text-center">
                      <div className={`text-2xl font-bold ${stat.color} mb-1`}>
                        {stat.value}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle>Actividad Reciente</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                      <div>
                        <p className="font-medium text-sm">{activity.activity}</p>
                        <p className="text-xs text-muted-foreground">{activity.date}</p>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {activity.score}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Learning Streak */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="text-lg">🔥 Racha de Aprendizaje</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold text-warning mb-2">12</div>
                  <p className="text-sm text-muted-foreground mb-4">días consecutivos</p>
                  <div className="flex justify-center space-x-1 mb-4">
                    {Array.from({length: 7}, (_, i) => (
                      <div
                        key={i}
                        className={`w-4 h-4 rounded-full ${
                          i < 5 ? 'bg-warning' : 'bg-muted'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    ¡Sigue así para mantener tu racha!
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="text-lg">Acciones Rápidas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Settings className="w-4 h-4 mr-2" />
                  Configuración
                </Button>
                
                <Button variant="outline" className="w-full justify-start">
                  <User className="w-4 h-4 mr-2" />
                  Cambiar Avatar
                </Button>
                
                <Button variant="outline" className="w-full justify-start">
                  <Mail className="w-4 h-4 mr-2" />
                  Preferencias de Email
                </Button>
              </CardContent>
            </Card>

            {/* Preferences */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="text-lg">Preferencias</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {preferences.map((pref, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-foreground">{pref.setting}</span>
                      <div className={`w-10 h-6 rounded-full transition-colors ${
                        pref.enabled ? 'bg-primary' : 'bg-muted'
                      } relative cursor-pointer`}>
                        <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform absolute top-1 ${
                          pref.enabled ? 'translate-x-5' : 'translate-x-1'
                        }`} />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Account Info */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="text-lg">Información de Cuenta</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Plan:</span>
                  <span className="font-medium">Gratuito</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ubicación:</span>
                  <span className="font-medium">{userProfile?.location || ""}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Última actividad:</span>
                  <span className="font-medium">Hoy</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Profile;