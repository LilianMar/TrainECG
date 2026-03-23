# ECG Insight Mentor Backend

Backend API para la plataforma de entrenamiento en lectura de electrocardiogramas (ECG) con apoyo de inteligencia artificial.

## 📋 Descripción General

API RESTful construida con **FastAPI** y **SQLite** que proporciona:

- ✅ Autenticación y gestión de usuarios
- ✅ Clasificación de ECG con modelo CNN+LSTM+Attention
- ✅ Interpretabilidad con Grad-CAM
- ✅ Módulo de práctica con retroalimentación
- ✅ Seguimiento de progreso y análisis
- ✅ Integración con LLM para explicaciones
- ✅ Seguridad con JWT y encriptación
- ✅ Logging y monitoreo

## 🏗️ Estructura del Proyecto

```
ecg-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configuración y variables de entorno
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py             # Base de modelos SQLAlchemy
│   │   └── session.py          # Gestión de sesiones
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # Modelo de usuario
│   │   ├── ecg.py              # Modelos de ECG y práctica
│   │   └── progress.py         # Modelo de progreso
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Schemas de usuario (Pydantic)
│   │   ├── ecg.py              # Schemas de ECG
│   │   └── progress.py         # Schemas de progreso
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # Rutas de autenticación
│   │   ├── users.py            # Rutas de perfil
│   │   ├── health.py           # Rutas de salud
│   │   ├── ecg.py              # Rutas de clasificación (TODO)
│   │   ├── practice.py         # Rutas de práctica (TODO)
│   │   └── progress.py         # Rutas de progreso (TODO)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py     # Lógica de usuarios
│   │   ├── ecg_service.py      # Lógica de ECG
│   │   └── progress_service.py # Lógica de progreso
│   ├── security/
│   │   ├── __init__.py
│   │   └── auth.py             # JWT y contraseñas
│   ├── middleware/
│   │   ├── cors.py             # CORS middleware
│   │   └── logging.py          # Logging middleware
│   ├── ml_pipeline/
│   │   ├── __init__.py
│   │   ├── model_manager.py    # Carga y predicción del modelo
│   │   ├── image_preprocessor.py # Preprocesamiento de imágenes
│   │   └── grad_cam.py         # Interpretabilidad con Grad-CAM
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py     # Manejo de archivos
│       └── logger.py           # Configuración de logging
├── logs/                        # Archivos de logging (ignorado en Git)
├── models/                      # Modelos ML pre-entrenados
│   ├── best_model_Hybrid_CNN_LSTM_Attention.h5
│   ├── best_model_Hybrid_CNN_LSTM_Attention_balanced.h5
│   └── best_model_CNN_Mejorada_Usuario.h5
├── uploads/                     # Imágenes subidas por usuarios (ignorado en Git)
├── scripts/                     # Scripts de utilidad (setup, database, etc.)
│   ├── populate_db.sh
│   ├── reset_database.sh
│   ├── insert_questions.py
│   └── ... (ver backend/scripts/README.md)
├── .env.example               # Variables de entorno (plantilla)
├── .gitignore                 # Archivos ignorados por Git
├── .dockerignore              # Archivos ignorados para Docker
├── requirements.txt           # Dependencias de Python
├── run.py                     # Script de entrada
├── Dockerfile                 # Containerización de backend
├── docker-compose.yml         # Orquestación con Docker Compose
└── README.md                  # Este archivo
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.10+
- pip o conda
- Git

### Pasos

1. **Clonar repositorio** (si aplica)
```bash
git clone <repo-url>
cd ecg-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus valores
```

5. **Ejecutar aplicación**
```bash
python run.py
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

Una vez que la aplicación esté corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Autenticación

### Endpoints de Autenticación

#### Registro
```http
POST /auth/register
Content-Type: application/json

{
  "name": "Dr. Juan Pérez",
  "email": "juan@ejemplo.com",
  "password": "securepass123",
  "user_type": "doctor",
  "institution": "Hospital ABC"
}

Response: 201 Created
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "juan@ejemplo.com",
  "password": "securepass123"
}

Response: 200 OK
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Usar Token

```http
GET /users/me
Authorization: Bearer eyJhbGc...
```

## 🏥 Endpoints Principales (Implementados)

### Health Check
- `GET /health` - Estado de la aplicación

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión

### Usuarios
- `GET /users/me` - Obtener perfil actual
- `PUT /users/me` - Actualizar perfil
- `GET /users/profile/{user_id}` - Ver perfil público

## 🔄 Endpoints por Implementar

### Clasificación de ECG
- `POST /ecg/classify` - Clasificar imagen de ECG
- `GET /ecg/history` - Historial de clasificaciones

### Práctica
- `GET /practice/questions` - Obtener preguntas
- `GET /practice/questions/{id}` - Obtener pregunta específica
- `POST /practice/answer` - Enviar respuesta
- `GET /practice/stats` - Estadísticas de práctica

### Progreso
- `GET /progress` - Obtener progreso del usuario
- `GET /progress/recommendations` - Recomendaciones personalizadas
- `GET /progress/stats/by-arrhythmia` - Estadísticas por arritmia

## 📊 Modelos de Datos

### Usuario
```python
{
  "id": 1,
  "name": "Dr. Juan Pérez",
  "email": "juan@ejemplo.com",
  "user_type": "doctor",
  "institution": "Hospital ABC",
  "is_active": true,
  "created_at": "2024-02-14T10:30:00",
  "last_login": "2024-02-14T15:45:00"
}
```

### Clasificación de ECG
```python
{
  "id": 1,
  "user_id": 1,
  "predicted_class": "atrial_fibrillation",
  "confidence": 0.94,
  "windows_analyzed": 25,
  "affected_windows": 12,
  "gradcam_windows": [
    {"x": 0, "y": 0, "width": 128, "height": 128, "confidence": 0.92}
  ],
  "llm_explanation": "...",
  "processing_time_ms": 2340,
  "created_at": "2024-02-14T16:00:00"
}
```

### Intento de Práctica
```python
{
  "user_id": 1,
  "question_id": 5,
  "selected_answer": 2,
  "is_correct": true,
  "time_spent_seconds": 45
}
```

## 🔒 Características de Seguridad

✅ **Autenticación JWT**: Tokens seguros con expiración
✅ **Hash de Contraseñas**: bcrypt con salt
✅ **CORS Configurable**: Origen de requests permitidos
✅ **Validación de Entrada**: Pydantic schemas
✅ **Logging Detallado**: Auditoría de operaciones
✅ **Validación de Archivos**: Extensiones y tamaños permitidos
✅ **Rate Limiting**: (por implementar)
✅ **Encriptación de Datos Sensibles**: (por implementar)

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_auth.py -v
```

## 📝 Variables de Entorno

Ver `.env.example` para referencia:

```env
# Base de datos
DATABASE_URL=sqlite:///./ecg_app.db
DATABASE_ECHO=False

# Seguridad
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Modelo ML
MODEL_PATH=./models/best_model_Hybrid_CNN_LSTM_Attention.h5
IMAGE_SIZE=128
WINDOW_SIZE=128
WINDOW_OVERLAP=0.5

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

## 🐳 Docker
 (desde raíz de TrainECG_app)
docker-compose up -d
```

Backend estará disponible en `http://localhost:8000Construir imagen
docker build -t ecg-backend:latest .

# Ejecutar contenedor
docker run -p 8000:8000 ecg-backend:latest

# Con Docker Compose
docker-compose up -d
```

## 📦 Dependencias Principales

- **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos
- **TensorFlow/Keras**: ML e inferencia
- **OpenCV**: Procesamiento de imágenes
- **python-jose**: JWT tokens
- **passlib**: Hash de contraseñas

Ver `requirements.txt` para lista completa.

## 📈 Performance

- **Inferencia del modelo**: ~2-3 segundos por imagen
- **Ventanas deslizantes**: Configurable (default: 128x128, overlap 50%)
- **Base de datos**: SQLite (OK para desarrollo, PostgreSQL para producción)

## 🚧 Roadmap

- [ ] Implementar rutas de ECG classification
- [ ] Implementar rutas de practice mode
- [ ] Implementar rutas de progress tracking
- [ ] Integración con LLM (OpenAI/Claude)
- [ ] Rate limiting y throttling
- [ ] Tests unitarios completos
- [ ] Documentación de API mejorada
- [ ] Migración a PostgreSQL
- [ ] Caché con Redis
- [ ] Autoscaling y load balancing
- [ ] Monitoring con Prometheus/Grafana

## 🤝 Contribución

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Commit cambios: `git commit -am 'Agregar funcionalidad'`
3. Push a rama: `git push origin feature/nueva-funcionalidad`
4. Abrir Pull Request

## 📄 Licencia

Este proyecto es parte de una tesis de trabajo de grado.

## 👨‍💼 Autor

Desarrollado para: ECG Insight Mentor Platform
Fecha: 2024

## 📧 Soporte

Para reportar issues o sugerencias, crear una issue en el repositorio.

---

**Última actualización**: Febrero 2024
