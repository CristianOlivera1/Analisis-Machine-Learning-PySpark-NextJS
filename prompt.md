Menus principales
1. Dashboard inicial
- Acceso rápido a las funciones principales (entrenar, visualizar).
- Carga de datasets
- Formulario para subir archivos CSV/Excel o seleccionar datasets abiertos preconfigurados (se almacenaran en localstorage y se subira desde un modal).
- Vista previa de columnas y tipos de datos.

2. Exploración de datos
- Tablas interactivas con filtros.
- Gráficas básicas (histogramas, barras, líneas).
- Estadísticas descriptivas (media, mediana, desviación estándar).

3. Entrenamiento de modelos (MLlib)
- Formulario para elegir tipo de modelo (clasificación, regresión, clustering).
- Selección de variables predictoras y objetivo.
- Botón para lanzar entrenamiento → se conecta al backend (el formulario debera de aparecer en un modal).
- Resultados del modelo
- Métricas de rendimiento (accuracy, precision, recall, F1).
- Visualización de curvas ROC, matrices de confusión.
- Descarga de reporte en PDF/Excel.

___DESPUES_____
4. Predicciones en tiempo real
- Formulario donde el usuario ingresa valores manuales.
- El modelo devuelve una predicción (ej. categoría, valor numérico).
- Se muestra en la web con feedback visual.

5. Documentación / Reportes
- Página que explica el dataset, el modelo aplicado y los hallazgos.
- Descarga de documentación generada automáticamente.
