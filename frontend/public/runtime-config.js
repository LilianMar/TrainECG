// Configuración leída en runtime por el frontend.
// nginx (docker-entrypoint.sh) sobreescribe este archivo al iniciar el contenedor,
// inyectando los valores reales desde las variables de entorno API_URL.
// Para desarrollo local con `vite dev` se queda con apiUrl vacío y cae al default
// de import.meta.env.VITE_API_URL (ver src/lib/api.ts).
window.RUNTIME_CONFIG = {
  apiUrl: ""
};
