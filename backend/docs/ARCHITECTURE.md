# 📊 ECG Backend - Arquitectura Visual y Referencias

## 🗂️ Árbol de Estructura Completo

```
ecg-backend/
│
├── 📁 app/                          # Código principal
│   ├── 📄 __init__.py
│   ├── 📄 main.py                  # ⭐ Punto de entrada FastAPI
│   │
│   ├── 📁 core/                    # Configuración
│   │   ├── 📄 __init__.py
│   │   └── 📄 config.py            # Settings + variables de entorno
│   │
│   ├── 📁 database/                # Persistencia
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py              # Base declarativa SQLAlchemy
│   │   └── 📄 session.py           # Conexión y sesiones
│   │
│   ├── 📁 models/                  # Tablas (SQLAlchemy ORM)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py              # Tabla: users
│   │   ├── 📄 ecg.py               # Tablas: ecg_classifications, practice_questions
│   │   └── 📄 progress.py          # Tabla: user_progress
│   │
│   ├── 📁 schemas/                 # DTOs (Pydantic)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py              # UserCreate, UserResponse, etc.
│   │   ├── 📄 ecg.py               # ECGClassificationResponse, etc.
│   │   └── 📄 progress.py          # UserProgressResponse, etc.
│   │
│   ├── 📁 routes/                  # Endpoints (FastAPI routers)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 health.py            # GET /health, GET /
│   │   ├── 📄 auth.py              # POST /auth/register, /auth/login
│   │   ├── 📄 users.py             # GET/PUT /users/me, GET /users/profile/{id}
│   │   ├── 📄 ecg.py               # 🚧 POST /ecg/classify (TODO)
│   │   ├── 📄 practice.py          # 🚧 GET/POST /practice/* (TODO)
│   │   └── 📄 progress.py          # 🚧 GET /progress/* (TODO)
│   │
│   ├── 📁 services/                # Lógica de negocio
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user_service.py      # Operaciones CRUD de usuarios
│   │   ├── 📄 ecg_service.py       # Operaciones de ECG y práctica
│   │   └── 📄 progress_service.py  # Análisis y recomendaciones
│   │
│   ├── 📁 security/                # Autenticación y autorización
│   │   ├── 📄 __init__.py
│   │   └── 📄 auth.py              # JWT, hash de contraseñas
│   │
│   ├── 📁 middleware/              # Procesadores de request/response
│   │   ├── 📄 cors.py              # CORS configuration
│   │   └── 📄 logging.py           # Logging de requests
│   │
│   ├── 📁 ml_pipeline/             # Modelos ML e inferencia
│   │   ├── 📄 __init__.py
│   │   ├── 📄 model_manager.py     # Cargar y usar modelo Keras
│   │   ├── 📄 image_preprocessor.py # Preprocesamiento, ventanas deslizantes
│   │   └── 📄 grad_cam.py          # Grad-CAM para interpretabilidad
│   │
│   └── 📁 utils/                   # Funciones auxiliares
│       ├── 📄 __init__.py
│       ├── 📄 file_handler.py      # Manejo de archivos subidos
│       └── 📄 logger.py            # Logging configurado
│
├── 📁 tests/                        # Tests (pytest)
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py              # Fixtures y configuración
│   ├── 📄 test_auth.py             # Tests de autenticación
│   └── 📄 test_endpoints.py        # Tests de API
│
├── 📁 logs/                         # Archivos de logging
│   └── 📄 app.log
│
├── 📁 uploads/                      # Imágenes subidas por usuarios
│
├── 📁 models/                       # Modelos ML pre-entrenados
│   ├── 📄 best_model_Hybrid_CNN_LSTM_Attention.h5
│   ├── 📄 best_model_Hybrid_CNN_LSTM_Attention_balanced.h5
│   └── 📄 best_model_CNN_Mejorada_Usuario.h5
│
├── 📄 .env.example                 # Variables de entorno (plantilla)
├── 📄 .gitignore                   # Archivos a ignorar
├── 📄 requirements.txt             # Dependencias Python
├── 📄 Dockerfile                   # Configuración Docker
├── 📄 docker-compose.yml           # Orquestación Docker
├── 📄 Makefile                     # Comandos de desarrollo
├── 📄 run.py                       # Script de entrada
├── 📄 README.md                    # Documentación completa
├── 📄 QUICKSTART.md               # Guía de inicio rápido
└── 📄 ARCHITECTURE.md             # Este archivo
```

## 🔄 Flujo de Datos (Request → Response)

```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENTE (Frontend)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Request
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               FASTAPI (app/main.py)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Middleware: CORS, Logging                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Routes (app/routes/):                                  │  │
│  │ - auth.py      → @router.post("/auth/register")      │  │
│  │ - auth.py      → @router.post("/auth/login")         │  │
│  │ - users.py     → @router.get("/users/me")            │  │
│  │ - ecg.py       → @router.post("/ecg/classify") 🚧    │  │
│  │ - practice.py  → @router.get("/practice/questions")  │  │
│  └───────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Services (app/services/):                              │  │
│  │ Lógica de negocio sin FastAPI                         │  │
│  │ - user_service.create_user()                          │  │
│  │ - ecg_service.create_classification()                 │  │
│  │ - progress_service.generate_recommendations()         │  │
│  └───────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Security (app/security/):                              │  │
│  │ - hash_password()                                      │  │
│  │ - verify_token()                                       │  │
│  │ - create_access_token()                                │  │
│  └───────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Database (app/database/):                              │  │
│  │ SQLAlchemy + SQLite                                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Models (app/models/):                                  │  │
│  │ - User                                                 │  │
│  │ - ECGClassification                                    │  │
│  │ - PracticeQuestion                                     │  │
│  │ - UserProgress                                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                     │                                        │
└─────────────────────┼────────────────────────────────────────┘
                     │
                     │ SQL Queries
                     ▼
          ┌──────────────────────┐
          │  SQLite Database     │
          │  (ecg_app.db)        │
          └──────────────────────┘
```

## 🤖 Flujo de Clasificación de ECG (Detallado)

```
┌─────────────────────────────────────────────────────────────┐
│ POST /ecg/classify                                          │
│ {multipart: image, user_id}                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ app/routes/ecg.py:classify_ecg()                            │
│ - Valida imagen (extensión, tamaño)                         │
│ - Guarda archivo en /uploads                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ app/ml_pipeline/image_preprocessor.py                       │
│ Paso 1: Load image                                          │
│ Paso 2: Resize a 128x128                                    │
│ Paso 3: Normalize (0-1)                                     │
│ Paso 4: Crear sliding windows (128x128, 50% overlap)       │
│         [window_1, window_2, ..., window_n]                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ app/ml_pipeline/model_manager.py                            │
│ Para cada window:                                           │
│   - Predicción → clase + confianza                          │
│   - Si confianza > threshold: "afectada"                    │
│ Resultado: lista de windows afectadas                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ app/ml_pipeline/grad_cam.py                                 │
│ Para windows afectadas:                                     │
│ - Compute Grad-CAM heatmap                                  │
│ - Extraer coordenadas (x, y, width, height)                │
│ Resultado: [(x1, y1, w1, h1), ...]                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM Integration (External)                                  │
│ prompt: "Explica esta fibrilación auricular..."            │
│ Resultado: "La fibrilación auricular es..."                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ app/services/ecg_service.py:create_classification()         │
│ - Guarda todo en DB (ECGClassification)                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ JSON Response                                               │
│ {                                                           │
│   "id": 1,                                                  │
│   "predicted_class": "atrial_fibrillation",                │
│   "confidence": 0.94,                                       │
│   "gradcam_windows": [...],                                │
│   "llm_explanation": "...",                                │
│   ...                                                       │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ Matriz de Responsabilidades

| Componente | Responsabilidad | Archivo |
|-----------|-----------------|---------|
| **Route** | Recibir HTTP request, validar input, devolver response | `app/routes/*.py` |
| **Schema** | Validar estructura de datos con Pydantic | `app/schemas/*.py` |
| **Service** | Lógica de negocio sin conocer HTTP | `app/services/*.py` |
| **Model** | Definición de tablas SQL | `app/models/*.py` |
| **Database** | Conexión y sesiones | `app/database/*.py` |
| **Security** | JWT, contraseñas, autenticación | `app/security/*.py` |
| **ML Pipeline** | Carga modelo, preprocesamiento, Grad-CAM | `app/ml_pipeline/*.py` |
| **Utils** | Funciones auxiliares (logging, archivos) | `app/utils/*.py` |

## 🔐 Flujo de Autenticación

```
┌──────────────────────────────────────────────────────────┐
│ 1. REGISTRO: POST /auth/register                         │
│    {name, email, password, user_type, institution}       │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
    ┌───────────────────┐
    │ Hash password     │ ← app/security/auth.py:hash_password()
    │ bcrypt + salt     │
    └───────────┬───────┘
             │
             ▼
    ┌───────────────────┐
    │ Crear usuario DB  │ ← app/services/user_service.py
    └───────────┬───────┘
             │
             ▼
    ┌───────────────────┐
    │ Generar JWT       │ ← app/security/auth.py:create_access_token()
    │ access_token      │    payload: {sub: user_id, exp: expiry}
    └───────────┬───────┘
             │
             ▼
    │ Retornar token    │
    └────────────────────

┌──────────────────────────────────────────────────────────┐
│ 2. LOGIN: POST /auth/login                              │
│    {email, password}                                     │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ Buscar usuario por email          │
    └───────────┬───────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ Verificar password                │ ← app/security/auth.py:verify_password()
    │ bcrypt.verify(plain, hashed)      │
    └───────────┬───────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ Generar JWT token                 │
    │ Actualizar last_login             │
    └───────────┬───────────────────────┘
             │
             ▼
    │ Retornar token                    │
    └────────────────────

┌──────────────────────────────────────────────────────────┐
│ 3. USAR TOKEN: GET /users/me                            │
│    Authorization: Bearer <token>                         │
└────────────┬─────────────────────────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ Verify JWT token                  │ ← app/security/auth.py:verify_token()
    │ Check signature y expiry           │    jose.jwt.decode()
    └───────────┬───────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ Extraer user_id del payload       │
    │ Buscar usuario en DB              │
    └───────────┬───────────────────────┘
             │
             ▼
    │ Retornar UserResponse             │
    └────────────────────
```

## 📈 Escalabilidad y Mejoras Futuras

### Fase 1 - Desarrollo (Febrero 2024)
- ✅ Estructura base con mejores prácticas
- ✅ Autenticación JWT
- ✅ Modelos y schemas
- 🚧 Completar rutas de ECG, práctica y progreso

### Fase 2 - Integración (Marzo 2024)
- Conectar modelo ML real
- Integrar LLM (OpenAI/Claude)
- Rate limiting y throttling
- Tests completos

### Fase 3 - Producción (Post-entrega)
- Migrar a PostgreSQL
- Redis para caché
- Docker + Kubernetes
- Monitoring (Prometheus/Grafana)
- CDN para imágenes
- Load balancing

## 🛠️ Tecnologías por Capa

```
┌─────────────────────────────────────────┐
│ Web Framework    │ FastAPI 0.104        │
├─────────────────────────────────────────┤
│ Validación       │ Pydantic 2.5         │
├─────────────────────────────────────────┤
│ ORM              │ SQLAlchemy 2.0       │
├─────────────────────────────────────────┤
│ BD               │ SQLite (dev)         │
├─────────────────────────────────────────┤
│ Seguridad        │ PyJWT, passlib       │
├─────────────────────────────────────────┤
│ ML/DL            │ TensorFlow, Keras    │
├─────────────────────────────────────────┤
│ Imagen           │ OpenCV, Pillow       │
├─────────────────────────────────────────┤
│ Async            │ asyncio, uvicorn     │
├─────────────────────────────────────────┤
│ Testing          │ pytest               │
├─────────────────────────────────────────┤
│ Code Quality     │ black, flake8, isort │
└─────────────────────────────────────────┘
```

---

**Última actualización**: Febrero 2024
**Estado**: En desarrollo activo
