#!/bin/bash
# reset_database.sh - Reinicia BD completamente con datos

set -e

echo "=========================================="
echo "🔄 Reseteando Base de Datos"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# 0. Copiar imágenes de entrenamiento a uploads
echo "0️⃣ Copiando imágenes de ECG..."
mkdir -p uploads/practice_ecgs
cp -v train/*.png uploads/practice_ecgs/ 2>/dev/null || echo "   ⚠️ Algunas imágenes ya existen"
echo "   ✅ Imágenes copiadas"

# 1. Borrar BD vieja
echo ""
echo "1️⃣ Borrando base de datos antigua..."
rm -f ecg_app.db
echo "   ✅ Borrado"
echo ""
echo "2️⃣ Creando tablas nuevas..."
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from app.database.base import Base
from app.database.session import engine


# Crear todas las tablas
Base.metadata.create_all(bind=engine)
print("   ✅ Tablas creadas")
EOF

# 3. Cargar preguntas de prueba
echo ""
echo "3️⃣ Cargando preguntas de práctica..."
python3 seed_test_questions.py 2>/dev/null || echo "   ⚠️ seed_test_questions.py"

# 4. Cargar preguntas profesionales del banco de entrenamiento
echo ""
echo "4️⃣ Cargando banco de preguntas profesionales..."
python3 load_train_questions.py 2>/dev/null || echo "   ⚠️ load_train_questions.py"

echo ""
echo "=========================================="
echo "✅ Base de datos lista!"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. Levanta la app:"
echo "   python run.py"
echo ""
echo "2. Abre en el navegador:"
echo "   http://localhost:8000/docs"
echo ""
echo "=========================================="
