/**
 * Get the full URL for an image path from the backend
 */
export const getImageUrl = (imagePath: string): string => {
  const apiBaseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  
  if (!imagePath) {
    console.warn('[getImageUrl] Empty image path provided');
    return '';
  }

  // Si el path ya comienza con /, usarlo directamente
  if (imagePath.startsWith('/')) {
    // Remover /app si está presente
    const cleanPath = imagePath.replace(/^\/app/, '');
    const finalUrl = `${apiBaseUrl}${cleanPath}`;
    console.log('[getImageUrl] Constructed URL:', {
      input: imagePath,
      apiBase: apiBaseUrl,
      cleaned: cleanPath,
      final: finalUrl
    });
    return finalUrl;
  }
  
  // Si no comienza con /, asumir que es una ruta relativa
  const finalUrl = `${apiBaseUrl}/${imagePath}`;
  console.log('[getImageUrl] Constructed URL:', {
    input: imagePath,
    apiBase: apiBaseUrl,
    final: finalUrl
  });
  return finalUrl;
};
