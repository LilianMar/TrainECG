# ---- Etapa 1: Build ----
FROM oven/bun:1 AS build

WORKDIR /app

# VITE_API_URL solo se usa como fallback al hacer build. Para cambiar la URL
# en runtime sin reconstruir, definir API_URL en docker-compose (ver entrypoint).
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

# Subpath del despliegue (ej: /trainECG/). En dev/local queda como "/".
# DEBE incluir las barras inicial y final.
ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=$VITE_BASE_PATH

# Copiar archivos de dependencias primero (cache de capas)
COPY package.json bun.lockb* ./

# Instalar dependencias (frozen-lockfile cuando exista bun.lockb)
RUN bun install --frozen-lockfile || bun install

# Copiar el resto del código fuente
COPY . .

# Construir la aplicación para producción
RUN bun run build

# ---- Etapa 2: Producción con Nginx ----
FROM nginx:stable-alpine AS production

# Eliminar config default de nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar configuración personalizada de nginx (SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos estáticos generados por Vite
COPY --from=build /app/dist /usr/share/nginx/html

# Entrypoint que genera runtime-config.js desde la variable API_URL
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
