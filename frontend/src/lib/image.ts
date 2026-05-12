import { getApiBaseUrl } from "@/lib/api";

/**
 * Get the full URL for an image path from the backend.
 */
export const getImageUrl = (imagePath: string): string => {
  if (!imagePath) return "";

  const apiBaseUrl = getApiBaseUrl();

  // Remover prefijo "/app" si viene de rutas absolutas del contenedor
  const normalized = imagePath.startsWith("/")
    ? imagePath.replace(/^\/app/, "")
    : `/${imagePath}`;

  return `${apiBaseUrl}${normalized}`;
};
