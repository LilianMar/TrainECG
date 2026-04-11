# ---- Etapa 1: Build ----
FROM oven/bun:1 AS build

WORKDIR /app

# Aceptar VITE_API_URL como argumento de build (sobreescribe .env)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Copiar archivos de dependencias primero (cache de capas)
COPY package.json bun.lockb* ./

# Instalar dependencias
RUN bun install

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

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
