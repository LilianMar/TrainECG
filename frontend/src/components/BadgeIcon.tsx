import React from 'react';
import {
  FileHeart,
  Stethoscope,
  Activity,
  TrendingUp,
  Rocket,
  Trophy,
  Crown,
  HeartHandshake,
  Zap,
  Shield,
  Heart,
  HeartPulse,
  CheckCircle,
  Target,
  Flame,
  Brain,
  Lightbulb,
  Award,
} from 'lucide-react';

interface BadgeIconProps {
  iconName: string;
  className?: string;
  isAchieved?: boolean;
}

// Mapping de nombres de iconos a componentes
const iconMap: { [key: string]: React.ComponentType<{ className?: string }> } = {
  FileHeart,
  Stethoscope,
  Activity,
  TrendingUp,
  Rocket,
  Trophy,
  Crown,
  HeartHandshake,
  Zap,
  Shield,
  Heart,
  HeartPulse,
  CheckCircle,
  Target,
  Flame,
  Brain,
  Lightbulb,
  Award,
};

export const BadgeIcon: React.FC<BadgeIconProps> = ({ 
  iconName, 
  className = "w-6 h-6",
  isAchieved = true 
}) => {
  const IconComponent = iconMap[iconName];

  if (!IconComponent) {
    // Fallback a un icono por defecto
    return <Award className={className} />;
  }

  return (
    <IconComponent 
      className={`${className} ${!isAchieved ? "opacity-50 grayscale" : ""}`}
    />
  );
};
