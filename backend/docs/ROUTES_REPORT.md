# TrainECG API Routes Report

Fecha: 2026-02-15

Este informe resume el flujo y el estado actual de las rutas disponibles en el backend.

## Base URL

- Local: http://localhost:8000

## Autenticacion

### POST /auth/register
- Flujo:
  1) Valida datos de registro (nombre, email, password, user_type, institution).
  2) Crea usuario y genera JWT.
  3) Responde token de acceso.
- Requiere autenticacion: no.

### POST /auth/login
- Flujo:
  1) Verifica credenciales.
  2) Genera JWT.
  3) Responde token de acceso.
- Requiere autenticacion: no.

## Health

### GET /health
- Flujo:
  1) Responde estado basico de la app.
- Requiere autenticacion: no.

### GET /
- Flujo:
  1) Responde metadata del API y enlaces a docs.
- Requiere autenticacion: no.

## Usuarios

### GET /users/me
- Flujo:
  1) Lee token Bearer desde Authorization.
  2) Valida JWT y obtiene usuario.
  3) Devuelve perfil actual.
- Requiere autenticacion: si.

### PUT /users/me
- Flujo:
  1) Lee token Bearer desde Authorization.
  2) Actualiza perfil con campos permitidos.
  3) Devuelve perfil actualizado.
- Requiere autenticacion: si.

### GET /users/profile/{user_id}
- Flujo:
  1) Busca usuario por id.
  2) Devuelve perfil publico.
- Requiere autenticacion: no.

## ECG

### POST /ecg/classify
- Flujo:
  1) Valida extension y tamano del archivo.
  2) Guarda la imagen en uploads.
  3) Preprocesa la imagen y crea ventanas.
  4) Ejecuta prediccion del modelo.
  5) Genera coordenadas de Grad-CAM (placeholder).
  6) Guarda clasificacion en base de datos.
  7) Retorna resultado.
- Requiere autenticacion: si.
- Nota: explicacion LLM es placeholder.

### GET /ecg/history
- Flujo:
  1) Lista clasificaciones del usuario.
- Requiere autenticacion: si.

## Practica

### GET /practice/questions
- Flujo:
  1) Lista preguntas con filtro opcional por dificultad.
- Requiere autenticacion: si.

### GET /practice/questions/{question_id}
- Flujo:
  1) Obtiene una pregunta especifica.
- Requiere autenticacion: si.

### POST /practice/answer
- Flujo:
  1) Valida respuesta y calcula si es correcta.
  2) Registra intento.
  3) Actualiza progreso.
  4) Retorna retroalimentacion.
- Requiere autenticacion: si.

### GET /practice/stats
- Flujo:
  1) Calcula estadisticas del usuario.
- Requiere autenticacion: si.

## Progreso

### GET /progress
- Flujo:
  1) Obtiene o crea progreso del usuario.
  2) Devuelve resumen.
- Requiere autenticacion: si.

### GET /progress/detailed
- Flujo:
  1) Obtiene progreso.
  2) Calcula rendimiento por arritmia.
  3) Genera recomendaciones.
- Requiere autenticacion: si.

### GET /progress/recommendations
- Flujo:
  1) Genera recomendaciones personalizadas.
- Requiere autenticacion: si.

### GET /progress/stats/by-arrhythmia
- Flujo:
  1) Devuelve rendimiento por tipo de arritmia.
- Requiere autenticacion: si.

## Observaciones

- Los endpoints de ECG, practica y progreso requieren JWT en header `Authorization: Bearer <token>`.
- La integracion con LLM para explicaciones aun es placeholder.
- Para practice mode es necesario poblar la base de datos con preguntas.
