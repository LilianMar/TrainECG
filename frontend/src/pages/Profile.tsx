import { useEffect, useState } from "react";
import { ArrowLeft, User, Mail, GraduationCap, Calendar, Edit, Settings, MapPin, TrendingUp, Activity as ActivityIcon, Award, Save, X } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/api";

interface UserStats {
  total_ecgs: number;
  avg_accuracy: number;
  consecutive_days: number;
  rank: string;
}

interface Activity {
  date: string;
  activity: string;
  score: string;
}

const Profile = () => {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  const [userProfile, setUserProfile] = useState<{
    name: string;
    email: string;
    userType: string;
    institution?: string | null;
    joinDate: string;
    avatar: string;
  } | null>(null);

  const [editedData, setEditedData] = useState<{
    name: string;
    institution: string;
  }>({
    name: "",
    institution: "",
  });

  const [stats, setStats] = useState<UserStats>({
    total_ecgs: 0,
    avg_accuracy: 0,
    consecutive_days: 0,
    rank: "Principiante"
  });

  const [recentActivity, setRecentActivity] = useState<Activity[]>([]);
  const [location, setLocation] = useState<string>("No disponible");

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
          avatar: "/api/placeholder/120/120",
        });

        // Inicializar datos para edición
        setEditedData({
          name: response.name,
          institution: response.institution || "",
        });
      } catch {
        setUserProfile(null);
      }
    };

    const loadStats = async () => {
      try {
        const response = await apiRequest<UserStats>("/users/me/stats");
        setStats(response);
      } catch (error) {
        console.error("Error loading stats:", error);
      }
    };

    const loadActivity = async () => {
      try {
        const response = await apiRequest<{ activities: Activity[] }>("/users/me/activity");
        setRecentActivity(response.activities);
      } catch (error) {
        console.error("Error loading activity:", error);
      }
    };

    const detectLocation = () => {
      // Try to get location from browser's language/timezone
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      
      // Simple mapping of timezones to locations
      if (timezone.includes("Bogota")) {
        setLocation("Colombia");
      } else if (timezone.includes("America")) {
        const country = timezone.split("/")[1]?.replace(/_/g, " ");
        setLocation(country || "América");
      } else {
        setLocation(timezone.split("/")[0] || "No disponible");
      }
    };

    loadProfile();
    loadStats();
    loadActivity();
    detectLocation();
  }, []);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    // Restaurar datos originales
    if (userProfile) {
      setEditedData({
        name: userProfile.name,
        institution: userProfile.institution || "",
      });
    }
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (!editedData.name.trim()) {
      toast({
        title: "Error de validación",
        description: "El nombre no puede estar vacío.",
        variant: "destructive",
      });
      return;
    }

    setIsSaving(true);
    try {
      const response = await apiRequest<{
        name: string;
        email: string;
        user_type: string;
        institution?: string | null;
        created_at: string;
      }>("/users/me", {
        method: "PUT",
        body: {
          name: editedData.name,
          institution: editedData.institution || null,
        },
      });

      // Actualizar el perfil con los nuevos datos
      setUserProfile(prev => prev ? {
        ...prev,
        name: response.name,
        institution: response.institution ?? "",
      } : null);

      setIsEditing(false);
      toast({
        title: "Perfil actualizado",
        description: "Tus datos se han guardado exitosamente.",
        variant: "success",
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "No se pudo actualizar el perfil";
      toast({
        title: "Error al actualizar",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const statsDisplay = [
    { 
      label: "ECGs Analizados", 
      value: stats.total_ecgs.toString(), 
      color: "text-primary",
      icon: ActivityIcon
    },
    { 
      label: "Precisión Promedio", 
      value: `${stats.avg_accuracy}%`, 
      color: "text-success",
      icon: TrendingUp
    },
    { 
      label: "Días Consecutivos", 
      value: stats.consecutive_days.toString(), 
      color: "text-warning",
      icon: Calendar
    },
    { 
      label: "Rango Actual", 
      value: stats.rank, 
      color: "text-foreground",
      icon: Award
    }
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
                  <div className="flex gap-2">
                    {isEditing ? (
                      <>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={handleCancel}
                          disabled={isSaving}
                        >
                          <X className="w-4 h-4 mr-2" />
                          Cancelar
                        </Button>
                        <Button 
                          size="sm"
                          onClick={handleSave}
                          disabled={isSaving}
                        >
                          <Save className="w-4 h-4 mr-2" />
                          {isSaving ? "Guardando..." : "Guardar"}
                        </Button>
                      </>
                    ) : (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={handleEdit}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Editar
                      </Button>
                    )}
                  </div>
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
                    {isEditing ? (
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="name">Nombre completo</Label>
                          <Input
                            id="name"
                            value={editedData.name}
                            onChange={(e) => setEditedData(prev => ({ ...prev, name: e.target.value }))}
                            placeholder="Ingresa tu nombre"
                            className="mt-1"
                          />
                        </div>

                        <div>
                          <Label htmlFor="email">Correo electrónico</Label>
                          <Input
                            id="email"
                            value={userProfile?.email || ""}
                            disabled
                            className="mt-1 bg-muted"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            El correo no se puede modificar
                          </p>
                        </div>

                        <div>
                          <Label htmlFor="institution">Institución</Label>
                          <Input
                            id="institution"
                            value={editedData.institution}
                            onChange={(e) => setEditedData(prev => ({ ...prev, institution: e.target.value }))}
                            placeholder="Nombre de tu institución"
                            className="mt-1"
                          />
                        </div>

                        <div>
                          <Label htmlFor="userType">Tipo de usuario</Label>
                          <Input
                            id="userType"
                            value={userProfile?.userType || ""}
                            disabled
                            className="mt-1 bg-muted"
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            El tipo de usuario no se puede modificar
                          </p>
                        </div>
                      </div>
                    ) : (
                      <>
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
                            <span className="text-sm">{userProfile?.institution || "No especificado"}</span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">Miembro desde {userProfile?.joinDate || ""}</span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <MapPin className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm">{location}</span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Statistics */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Estadísticas de Rendimiento
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {statsDisplay.map((stat, index) => (
                    <div key={index} className="text-center space-y-2">
                      <div className="flex justify-center">
                        <stat.icon className={`w-6 h-6 ${stat.color}`} />
                      </div>
                      <div className={`text-2xl font-bold ${stat.color}`}>
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
                <CardTitle className="flex items-center gap-2">
                  <ActivityIcon className="w-5 h-5" />
                  Actividad Reciente
                </CardTitle>
              </CardHeader>
              <CardContent>
                {recentActivity.length > 0 ? (
                  <div className="space-y-4">
                    {recentActivity.map((activity, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{activity.activity}</p>
                          <p className="text-xs text-muted-foreground">{activity.date}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {activity.score}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <ActivityIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No hay actividad reciente</p>
                    <p className="text-sm mt-1">¡Comienza a usar la aplicación!</p>
                  </div>
                )}
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
                  <div className="text-4xl font-bold text-warning mb-2">
                    {stats.consecutive_days}
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    {stats.consecutive_days === 1 ? "día consecutivo" : "días consecutivos"}
                  </p>
                  <div className="flex justify-center space-x-1 mb-4">
                    {Array.from({length: 7}, (_, i) => (
                      <div
                        key={i}
                        className={`w-4 h-4 rounded-full transition-colors ${
                          i < Math.min(stats.consecutive_days, 7) ? 'bg-warning' : 'bg-muted'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {stats.consecutive_days > 0 
                      ? "¡Sigue así para mantener tu racha!" 
                      : "¡Comienza tu racha de aprendizaje hoy!"}
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
                <Link to="/classify" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <ActivityIcon className="w-4 h-4 mr-2" />
                    Analizar ECG
                  </Button>
                </Link>
                
                <Link to="/practice" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <GraduationCap className="w-4 h-4 mr-2" />
                    Modo Práctica
                  </Button>
                </Link>
                
                <Link to="/progress" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Ver Progreso
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Account Info */}
            <Card className="medical-card">
              <CardHeader>
                <CardTitle className="text-lg">Información de Cuenta</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Plan:</span>
                  <Badge variant="secondary">Gratuito</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ubicación:</span>
                  <span className="font-medium">{location}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Última actividad:</span>
                  <span className="font-medium">
                    {recentActivity.length > 0 ? recentActivity[0].date : "Sin actividad"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Rango:</span>
                  <Badge variant="outline">{stats.rank}</Badge>
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
