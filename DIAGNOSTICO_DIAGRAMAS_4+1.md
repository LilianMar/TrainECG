# Diagnóstico de los diagramas del Modelo 4+1 — TrainECG

Fecha: 2026-03-18

Comparación entre lo que muestran los 5 diagramas del Modelo 4+1 en `USB_template/sections/metodologia.tex` y la arquitectura real verificada en el código fuente del proyecto.

---

## Diagrama 1: Vista General — Problemas graves

| Elemento en el diagrama | Realidad en el código | Veredicto |
|---|---|---|
| **"Base de datos vectorizada" (5)** | No existe. El sistema usa **SQLite** relacional (`ecg_app.db` vía SQLAlchemy). No hay embeddings ni búsqueda vectorial. | **INCORRECTO** |
| **"LLM open evidence" (6)** | El LLM es **OpenAI GPT-3.5-turbo** (`backend/app/services/llm_service.py`). No se usa OpenEvidence. | **INCORRECTO** |
| **"Búsqueda semántica"** (flecha) | No existe búsqueda semántica. El chatbot usa **TF-IDF local** en el frontend (`FloatingChatbot.tsx` + `corpus.json`). El LLM recibe un prompt directo con el resultado de clasificación + skill_level. | **INCORRECTO** |
| **"Datos del contexto" (4)** con "Original/New Content" | Sugiere un patrón RAG que no existe. El sistema no recupera contexto de ninguna base de datos para alimentar el LLM. | **INCORRECTO** |
| **Modelo de clasificación (3)** | Correcto: existe el Hybrid CNN-LSTM-Attention en `backend/app/ml_pipeline/model_manager.py` | OK |
| **Módulo de práctica (7)** | Correcto: existe PracticeMode, InitialTest, PostPracticeTest | OK |
| **Formulario de evaluación (8)** | Correcto: existe el sistema de progreso y evaluación | OK |
| **Falta**: Chatbot TF-IDF | Es un componente importante del sistema (`frontend/src/components/FloatingChatbot.tsx`), no aparece | **FALTANTE** |
| **Falta**: Sistema de logros/badges | 16 tipos de badges con `AchievementService` | **FALTANTE** |
| **Falta**: Pipeline de preprocesamiento | Sliding windows, Otsu, anotación de imagen (`backend/app/ml_pipeline/image_preprocessor.py`) | **FALTANTE** |

---

## Diagrama 2: Vista de Detalle (diagrama de actividad) — Problemas graves

| Elemento | Realidad | Veredicto |
|---|---|---|
| **"Base de datos Vectorizada"** (columna) | No existe. Es SQLite relacional. | **INCORRECTO** |
| **"LLM OpenEvidence"** (columna) | Es OpenAI GPT-3.5-turbo | **INCORRECTO** |
| **Flujo "Búsqueda semántica → BD vectorizada → contexto → LLM"** | No existe patrón RAG. El flujo real es: resultado de clasificación + skill_level → prompt directo a OpenAI → explicación | **INCORRECTO** |
| **"Contexto Alimenta la base de datos"** | No se alimenta ninguna BD de contexto. La clasificación se guarda en tabla `ECGClassification` (SQLite) | **INCORRECTO** |
| **Falta**: Pipeline de sliding windows | El preprocesamiento real divide la imagen en ventanas horizontales (150px ancho, 30px paso), cada una se clasifica y se aplica voting | **FALTANTE** |
| **Falta**: Anotación de imagen | `ImageAnnotator` dibuja rectángulos rojos sobre ventanas afectadas | **FALTANTE** |
| **Falta**: Actualización de progreso y badges | Después de clasificar se actualiza `UserProgress` y se verifican badges | **FALTANTE** |

---

## Diagrama 3: Vista de Componentes — Parcialmente correcto

| Elemento | Realidad | Veredicto |
|---|---|---|
| **"Base de datos vectorial"** | No existe | **INCORRECTO** |
| **"OpenEvidence API"** (API externa) | Es **OpenAI API** | **INCORRECTO** |
| **"Servicio OpenEvidence"** | Debería ser **LLMService** (`llm_service.py`) que llama a OpenAI | **INCORRECTO** |
| Capa UI: solo 2 componentes + práctica | Faltan: Login, Register, Dashboard, Progress, Profile, Library, FloatingChatbot, BadgeIcon | **INCOMPLETO** |
| Capa API: 3 controladores | Faltan: `progress`, `achievements`, `users`, `health` (hay 7 routers, no 3) | **INCOMPLETO** |
| Capa servicios: 4 servicios | Faltan: **UserService**, **ProgressService**, **AchievementService** (hay 5 servicios, no 4) | **INCOMPLETO** |
| **"Servicio de explicabilidad"** | Parcialmente correcto: existe GradCAM (`grad_cam.py`), pero la explicación principal la genera el LLMService | OK parcial |
| Capa acceso a datos: 3 repositorios | Faltan: repositorios de progreso y achievements. Hay 7 modelos de datos | **INCOMPLETO** |

---

## Diagrama 4: Vista de Despliegue — Muy distorsionado

| Elemento | Realidad | Veredicto |
|---|---|---|
| **"Cluster Orquestador"** | No existe. El sistema usa **Docker Compose** con 2 contenedores simples, no un cluster | **INCORRECTO** |
| **"WAF" (Web Application Firewall)** | No existe. Solo hay middleware CORS (`cors.py`) y logging (`logging.py`) | **INCORRECTO** |
| **"Servidor IA / Clasificador ECG"** (servidor separado) | El modelo ML se carga **dentro del contenedor backend** como singleton (`ModelManager`). No es un servidor separado | **INCORRECTO** |
| **"Base de datos vectorizada"** (servidor separado) | No existe. SQLite es un **archivo** dentro del volumen del backend | **INCORRECTO** |
| **"API Gateway"** para LLM | No existe gateway. El backend hace llamadas HTTP directas a la API de OpenAI | **INCORRECTO** |
| **"Secure LAN"** | No está configurada explícitamente. Docker usa red interna `trainecg-network` | **EXAGERADO** |
| **Falta**: La arquitectura real | 2 contenedores Docker: backend (`python:3.11-slim`, uvicorn, puerto 8000) + frontend (`nginx:stable-alpine`, puerto 9000). Volúmenes para uploads, logs y models. Red interna `trainecg-network`. | **FALTANTE** |

---

## Diagrama 5: Vista de Secuencia — Tipo de diagrama equivocado

| Elemento | Realidad | Veredicto |
|---|---|---|
| **El tipo de diagrama** | La descripción en el texto dice "secuencia" (flujos temporales), pero la imagen es un **diagrama de casos de uso** UML. Son diagramas fundamentalmente diferentes. | **TIPO ERRÓNEO** |
| **"Consultar con openEvidence"** | Es OpenAI, no OpenEvidence | **INCORRECTO** |
| **Falta**: Caso de uso Library | La Biblioteca (guía ECG + referencia de arritmias) es una funcionalidad importante | **FALTANTE** |
| **Falta**: Caso de uso Profile | Gestión de perfil del usuario | **FALTANTE** |
| **Falta**: Caso de uso Chatbot | Interacción con el chatbot TF-IDF | **FALTANTE** |
| Casos de uso presentes | Login, Clasificar, Practicar, Evaluar progreso son correctos | OK |

---

## Resumen ejecutivo

### 3 problemas transversales más graves

1. **"OpenEvidence" no existe en el sistema** — El LLM es OpenAI GPT-3.5-turbo (`backend/app/services/llm_service.py`). Todas las referencias a "OpenEvidence" en los 5 diagramas deben cambiarse a "OpenAI GPT-3.5-turbo".

2. **"Base de datos vectorizada" no existe** — El sistema usa SQLite relacional puro (`backend/app/database/session.py`). No hay embeddings, ni búsqueda vectorial, ni patrón RAG. El LLM recibe prompts directos con el resultado de clasificación y el nivel del usuario, no contexto recuperado de una BD vectorial.

3. **El diagrama de despliegue muestra infraestructura que no existe** — No hay cluster orquestador, WAF, servidor IA separado, ni API Gateway. La realidad es Docker Compose con 2 contenedores simples (backend + frontend/nginx) definidos en `docker-compose.yml`.

### Problema adicional

El diagrama 5 dice ser de "secuencia" pero es un diagrama de **casos de uso**, lo cual es una inconsistencia entre el texto descriptivo y la imagen.

---

## Arquitectura real verificada (referencia para corregir los diagramas)

### Componentes reales del sistema

**Frontend** (React + TypeScript + Vite + Tailwind + shadcn/ui):
- Páginas: Login, Register, Dashboard, ClassifyECG, PracticeMode, InitialTest, PostPracticeTest, Progress, Profile, Library, NotFound
- Componentes: ProtectedRoute, FloatingChatbot (TF-IDF local), BadgeIcon
- API client: `apiRequest()` con JWT Bearer token
- Chatbot: TF-IDF sobre `corpus.json` (100% cliente, sin backend)

**Backend** (FastAPI + Python):
- 7 Routers: auth, users, ecg, practice, progress, achievements, health
- 5 Servicios: UserService, ECGService, LLMService, AchievementService, ProgressService
- Seguridad: JWT HS256 (access 30min + refresh 7 días), bcrypt
- Middleware: CORS, Request Logging

**ML Pipeline** (`backend/app/ml_pipeline/`):
- ModelManager: carga singleton del modelo Hybrid CNN-LSTM-Attention (.h5)
- ImagePreprocessor: grayscale → detección de región ECG → sliding windows (150px, 30px step) → GaussianBlur + Otsu → resize 128x128
- ImageAnnotator: rectángulos rojos sobre ventanas con arritmia detectada
- GradCAM: mapas de activación para explicabilidad visual

**Base de datos** (SQLite vía SQLAlchemy):
- Modelos: User, ECGClassification, PracticeQuestion, PracticeAttempt, PostPracticeTest, UserProgress, UserAchievement
- 16 tipos de badges (clasificación, rendimiento, especialización, persistencia)

**LLM** (OpenAI GPT-3.5-turbo):
- Explicaciones clínicas adaptadas al nivel del usuario
- Recomendaciones post-test
- Recomendaciones de progreso
- Fallback con respuestas hardcoded si no hay API key

**Despliegue** (Docker Compose):
- Contenedor backend: `python:3.11-slim`, uvicorn, puerto 8000
- Contenedor frontend: `nginx:stable-alpine`, SPA routing, puerto 9000
- Volúmenes: ./backend, ./logs, ./uploads, ./models
- Red: `trainecg-network`
