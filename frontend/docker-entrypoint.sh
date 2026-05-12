#!/bin/sh
# Genera /runtime-config.js con los valores de las variables de entorno
# del contenedor. Permite cambiar la URL del backend SIN reconstruir la imagen.
set -e

API_URL="${API_URL:-}"

cat > /usr/share/nginx/html/runtime-config.js <<EOF
window.RUNTIME_CONFIG = {
  apiUrl: "${API_URL}"
};
EOF

echo "[entrypoint] runtime-config.js generado con apiUrl='${API_URL}'"

exec nginx -g 'daemon off;'
