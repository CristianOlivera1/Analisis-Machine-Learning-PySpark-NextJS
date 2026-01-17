# Análisis y entrenamiento de modelos de Machine Learning con PySpark

Aplicación web de análisis y predicción de datos con Machine Learning, construida con Next.js 16, shadcn/ui, Flask y PySpark.

<img src="https://github.com/user-attachments/assets/1fbe64fb-f1fb-4a26-a5f3-c044a5acd830" alt="Banner PySpark" />

## 🚀 Características Implementadas

### ✨ Funcionalidades Principales

#### 📊 Dashboard
- **Resumen del Sistema**: Visualización de métricas clave
  - Total de datasets cargados
  - Modelos entrenados
  - Archivos en el sistema
  - Reportes generados
- **Datasets Recientes**: Lista de los últimos datasets cargados
- **Modelos Recientes**: Lista de los últimos modelos entrenados
- **Actualización en Tiempo Real**: Información actualizada del backend

#### 🎯 Página de Entrenamiento (4 Pestañas)

##### 1️⃣ Cargar Datos
- **Upload de Archivos**: Soporta CSV, Excel (.xlsx, .xls)
- **Datasets de Ejemplo**: Carga rápida de datasets (Iris, Wine, Diabetes)
- **Gestión de Datasets**: Lista completa con información detallada
  - Número de filas y columnas
  - ID único del dataset
  - Nombre del archivo
- **Eliminación de Datasets**: Borrado individual

##### 2️⃣ Explorar
- **Selector de Dataset**: Dropdown para seleccionar dataset activo
- **Vista Previa**: Tabla con las primeras 10 filas
- **Estadísticas Descriptivas**: Tabla completa con:
  - Media, Desviación Estándar
  - Mínimo, Máximo
  - Percentiles (25%, 50%, 75%)
- **Histogramas**: Visualización de distribución por columna
  - Selector de columna
  - Gráfico interactivo con Recharts
- **Análisis de Datos**: Información detallada de cada columna

##### 3️⃣ Entrenar
- **Configuración de Modelo**:
  - Selección de dataset
  - Nombre personalizado del modelo
  - Tipo de modelo (Clasificación, Regresión, Clustering)
  - Algoritmo específico
  - Columna objetivo (target)
  - Selección múltiple de características (features)
- **Validación de Formulario**: Validación antes de entrenar
- **Feedback en Tiempo Real**: Notificaciones de progreso

##### 4️⃣ Modelos
- **Lista de Modelos**: Todos los modelos entrenados
- **Información Detallada**:
  - Nombre y tipo de modelo
  - Algoritmo utilizado
  - Dataset asociado
  - Columna objetivo
  - Features utilizados
  - Métricas de evaluación
- **Acciones**:
  - Descargar reporte en Excel
  - Eliminar modelo

## 🛠️ Stack Tecnológico

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Componentes UI**: shadcn/ui + Radix UI
- **Gráficos**: Recharts
- **Tablas**: Custom components con Radix UI
- **Formularios**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Fechas**: date-fns
