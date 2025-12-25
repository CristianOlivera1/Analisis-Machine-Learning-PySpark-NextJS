# 🚀 Guía de Inicio Rápido

## Arquitectura Completada ✅

El backend ha sido completamente reestructurado siguiendo las mejores prácticas de desarrollo de software:

### 📂 Estructura del Proyecto

```
mlpysparkbackend/
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py              # Application Factory (create_app)
│   ├── config.py                # Configuración por entornos
│   ├── extensions.py            # Extensiones de Flask (CORS, etc.)
│   │
│   ├── api/                     # 🌐 Capa de API (Presentación)
│   │   ├── __init__.py         
│   │   ├── routes/             # Blueprints de endpoints
│   │   │   ├── health.py       # Health checks
│   │   │   ├── datasets.py     # Gestión de datasets
│   │   │   ├── exploration.py  # Exploración de datos
│   │   │   ├── models.py       # Modelos ML
│   │   │   └── reports.py      # Reportes
│   │   │
│   │   └── schemas/            # 📋 Validación de datos
│   │       ├── dataset_schemas.py
│   │       ├── exploration_schemas.py
│   │       ├── model_schemas.py
│   │       └── report_schemas.py
│   │
│   ├── core/                    # ⚙️ Núcleo de la aplicación
│   │   ├── spark_manager.py    # Singleton para Spark Session
│   │   └── storage.py          # Repository Pattern (almacenamiento)
│   │
│   ├── services/                # 💼 Lógica de Negocio
│   │   ├── dataset_service.py  # Gestión de datasets
│   │   ├── exploration_service.py  # Análisis de datos
│   │   ├── training_service.py # Entrenamiento de modelos
│   │   └── report_service.py   # Generación de reportes
│   │
│   └── utils/                   # 🛠️ Utilidades
│       ├── decorators.py       # Decoradores (error handling, etc.)
│       ├── exceptions.py       # Excepciones personalizadas
│       ├── validators.py       # Validadores
│       └── helpers.py          # Funciones auxiliares
│
├── storage/                     # 💾 Almacenamiento de archivos
│   ├── uploads/                # Datasets subidos
│   ├── models/                 # Modelos entrenados
│   └── reports/                # Reportes generados
│
├── app.py                       # Entry point legacy (compatibilidad)
├── run.py                       # ⚡ Entry point principal
├── requirements.txt             # 📦 Dependencias
├── .env.example                 # Ejemplo de configuración
├── .gitignore                   # Git ignore
└── README.md                    # Documentación completa
```

## 🎯 Patrones y Prácticas Implementadas

### ✨ Patrones de Diseño
- **Application Factory Pattern**: Creación modular de la app
- **Repository Pattern**: Gestión centralizada de datos (Storage)
- **Singleton Pattern**: SparkManager para una única sesión
- **Service Layer Pattern**: Separación de lógica de negocio
- **Blueprint Pattern**: Organización de rutas

### 🛡️ Buenas Prácticas
- **Separation of Concerns**: Cada capa tiene una responsabilidad
- **DRY (Don't Repeat Yourself)**: Código reutilizable
- **SOLID Principles**: Código mantenible y escalable
- **Type Hints**: Tipado estático para mejor IDE support
- **Comprehensive Logging**: Logs en todos los niveles
- **Error Handling**: Manejo centralizado de errores
- **Input Validation**: Validación exhaustiva de datos
- **Documentation**: Docstrings completos

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd mlpysparkbackend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env con tus configuraciones
# (Usar cualquier editor de texto)
```

### 3. Iniciar el Servidor

```bash
# Modo desarrollo
python run.py

# O usando Flask CLI
set FLASK_APP=run.py  # Windows
export FLASK_APP=run.py  # Linux/Mac
flask run
```

El servidor estará disponible en: `http://localhost:5000`

## 📡 Endpoints Disponibles

### Health Check
```
GET  /api/health          # Estado general
GET  /api/health/spark    # Estado de Spark
```

### Datasets
```
POST   /api/datasets/upload          # Subir CSV/Excel
POST   /api/datasets/upload-json     # Subir JSON
GET    /api/datasets                 # Listar todos
GET    /api/datasets/:id             # Obtener info
GET    /api/datasets/:id/preview     # Vista previa
DELETE /api/datasets/:id             # Eliminar
GET    /api/datasets/samples         # Ejemplos disponibles
POST   /api/datasets/samples/:id/load  # Cargar ejemplo
```

### Exploración de Datos
```
GET  /api/datasets/:id/statistics     # Estadísticas descriptivas
GET  /api/datasets/:id/histogram      # Histograma
GET  /api/datasets/:id/chart          # Datos para gráficos
GET  /api/datasets/:id/correlation    # Matriz de correlación
POST /api/datasets/:id/filter         # Filtrar datos
GET  /api/datasets/:id/describe       # Describir columna
GET  /api/datasets/:id/missing        # Valores faltantes
```

### Modelos ML
```
GET    /api/models/types              # Tipos disponibles
POST   /api/models/train              # Entrenar modelo
GET    /api/models                    # Listar modelos
GET    /api/models/:id                # Info de modelo
POST   /api/models/:id/predict        # Predicciones
DELETE /api/models/:id                # Eliminar
GET    /api/models/:id/feature-importance
POST   /api/models/:id/evaluate
```

### Reportes
```
POST /api/reports/generate              # Generar reporte
GET  /api/reports/export-dataset/:id    # Exportar dataset
GET  /api/reports/model/:id/metrics     # Métricas detalladas
GET  /api/reports/summary               # Resumen del sistema
```

## 🧪 Testing Rápido

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Cargar Dataset de Ejemplo
```bash
curl -X POST http://localhost:5000/api/datasets/samples/iris/load
```

### 3. Ver Datasets
```bash
curl http://localhost:5000/api/datasets
```

## 🔄 Migración desde app.py Anterior

El antiguo `app.py` ha sido refactorizado completamente:

### Antes (Monolítico)
```
app.py (1200+ líneas)
├── Configuración
├── Rutas
├── Lógica de negocio
├── Utilidades
└── Todo mezclado
```

### Ahora (Arquitectura en Capas)
```
app/
├── api/          # Rutas y validación
├── services/     # Lógica de negocio
├── core/         # Componentes core
└── utils/        # Utilidades
```

**Ventajas:**
- ✅ Código más mantenible
- ✅ Fácil testing
- ✅ Escalabilidad
- ✅ Reutilización de código
- ✅ Mejor organización

## 📝 Próximos Pasos

1. **Testing**: Implementar tests unitarios y de integración
2. **CI/CD**: Configurar pipeline de despliegue
3. **Docker**: Crear Dockerfile y docker-compose
4. **Monitoring**: Agregar métricas y monitoreo
5. **Authentication**: Implementar autenticación JWT
6. **Rate Limiting**: Agregar límites de peticiones
7. **Caching**: Implementar caché para consultas frecuentes
8. **API Documentation**: Swagger/OpenAPI

## 🐛 Troubleshooting

### Error: PySpark no encuentra Java
```bash
# Instalar Java JDK 11 o superior
# Configurar JAVA_HOME
set JAVA_HOME=C:\Path\To\Java  # Windows
export JAVA_HOME=/path/to/java  # Linux/Mac
```

### Error: Puerto 5000 en uso
```bash
# Cambiar puerto en .env
FLASK_PORT=5001
```

### Error: Módulo no encontrado
```bash
# Verificar que estás en el entorno virtual
pip install -r requirements.txt
```

## 📚 Recursos Adicionales

- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MLlib Guide](https://spark.apache.org/docs/latest/ml-guide.html)

## ✅ Checklist de Calidad

- [x] Arquitectura en capas
- [x] Separation of Concerns
- [x] Error handling centralizado
- [x] Validación de datos
- [x] Logging comprehensivo
- [x] Type hints
- [x] Docstrings completos
- [x] Configuración por entornos
- [x] README completo
- [x] .gitignore configurado
- [x] Requirements actualizado

---

**¡El backend está listo para desarrollo!** 🎉
