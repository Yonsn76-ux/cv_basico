# 🎯 Clasificador de CVs por Profesiones v2.0

**Versión simplificada y fácil de usar**

Sistema inteligente para clasificar currículums vitae por profesión o puesto de trabajo. Esta versión v2 está diseñada para ser más simple e intuitiva, permitiendo entrenar modelos específicos por profesión y obtener recomendaciones precisas sobre qué trabajo es más adecuado para cada persona.

## 🌟 Características Principales

- **🎓 Entrenamiento por Profesiones**: Organiza CVs en carpetas por profesión y entrena modelos específicos
- **🔍 Clasificación Inteligente**: Analiza cualquier CV y recomienda la profesión más adecuada
- **📊 Ranking de Profesiones**: Muestra probabilidades para todas las profesiones disponibles
- **🖥️ Interfaz Simplificada**: Una sola ventana con pestañas fáciles de usar
- **📄 Multi-formato**: Soporta PDFs, Word e imágenes con OCR
- **⚡ Rápido y Eficiente**: Usa algoritmos optimizados (Random Forest, Regresión Logística)

## 🎯 Casos de Uso

### Para Empresas de Reclutamiento:
- Clasificar automáticamente CVs recibidos por área
- Identificar candidatos ideales para posiciones específicas
- Acelerar el proceso de selección inicial

### Para Consultores de Carrera:
- Ayudar a personas a identificar profesiones afines
- Orientar sobre cambios de carrera
- Evaluar compatibilidad con diferentes áreas

### Para Instituciones Educativas:
- Orientar a estudiantes sobre carreras profesionales
- Analizar perfiles de egresados
- Mejorar programas académicos

## 🚀 Instalación Rápida

### 1. Requisitos
- Python 3.8 o superior
- Tesseract OCR (para procesar imágenes)

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar aplicación
```bash
python main_gui.py
```

## 📋 Guía de Uso

### Paso 1: Preparar Datos de Entrenamiento

1. **Organizar CVs por profesión**:
   ```
   mis_cvs/
   ├── Agrónomo/
   │   ├── cv_agronomo_1.pdf
   │   ├── cv_agronomo_2.docx
   │   └── cv_agronomo_3.jpg
   ├── Ingeniero de Software/
   │   ├── cv_software_1.pdf
   │   └── cv_software_2.pdf
   ├── Marketing/
   │   ├── cv_marketing_1.docx
   │   └── cv_marketing_2.pdf
   └── Contador/
       ├── cv_contador_1.pdf
       └── cv_contador_2.docx
   ```

2. **Usar CVs de ejemplo** (opcional):
   ```bash
   python sample_generator.py
   ```
   Esto creará carpetas con CVs de ejemplo para probar el sistema.

### Paso 2: Entrenar el Modelo

1. Abrir la pestaña **"🎓 Entrenar Modelo"**
2. Para cada profesión:
   - Escribir el nombre (ej: "Agrónomo")
   - Seleccionar la carpeta con CVs de esa profesión
   - Hacer clic en "➕ Agregar Profesión"
3. Configurar tipo de modelo (recomendado: Random Forest)
4. Hacer clic en **"🚀 Entrenar Modelo"**
5. Esperar a que termine el entrenamiento

### Paso 3: Clasificar CVs

1. Abrir la pestaña **"🔍 Clasificar CV"**
2. Verificar que el modelo esté cargado (✅ verde)
3. Seleccionar un archivo CV
4. Hacer clic en **"🎯 Clasificar CV"**
5. Ver los resultados:
   - **Profesión recomendada** con nivel de confianza
   - **Ranking completo** de todas las profesiones
   - **Interpretación** del resultado

## 📊 Interpretación de Resultados

### Niveles de Confianza:
- **Alta (>80%)**: ✅ El CV coincide muy bien con esta profesión
- **Media (60-80%)**: ⚠️ Buena coincidencia, pero podría encajar en otras profesiones
- **Baja (<60%)**: ❓ No hay una coincidencia clara con ninguna profesión específica

### Ejemplo de Resultado:
```
🎯 Profesión Recomendada: Agrónomo
🔥 Confianza: 87.3% (Alta)

📊 Ranking de Profesiones:
1. Agrónomo - 87.3%
2. Ingeniero de Software - 8.1%
3. Marketing - 3.2%
4. Contador - 1.4%
```

## 🛠️ Configuración Avanzada

### Tipos de Modelo:
- **Random Forest** (recomendado): Mejor para datasets pequeños y medianos
- **Logistic Regression**: Más rápido, bueno para datasets grandes

### Mejores Prácticas:
- **Mínimo 5-10 CVs por profesión** para resultados confiables
- **Usar profesiones bien diferenciadas** (ej: Agrónomo vs Ingeniero vs Marketing)
- **CVs de calidad** con información completa y relevante
- **Actualizar el modelo** regularmente con nuevos CVs

## 📁 Estructura del Proyecto

```
cv_classifier_v2/
├── main_gui.py           # 🖥️ Interfaz gráfica principal
├── cv_processor.py       # 📄 Procesamiento de documentos
├── cv_classifier.py      # 🤖 Modelo de clasificación
├── sample_generator.py   # 📝 Generador de CVs de ejemplo
├── requirements.txt      # 📦 Dependencias
├── README.md            # 📖 Esta documentación
└── models/              # 💾 Modelos entrenados (se crea automáticamente)
```

## 🔧 Solución de Problemas

### Error: "Tesseract not found"
```bash
# Windows: Descargar desde
https://github.com/UB-Mannheim/tesseract/wiki

# Linux:
sudo apt-get install tesseract-ocr tesseract-ocr-spa

# macOS:
brew install tesseract tesseract-lang
```

### Error: "No se pudo extraer texto"
- Verificar que el archivo no esté corrupto
- Para imágenes: asegurar que el texto sea legible
- Para PDFs: verificar que no estén protegidos

### Baja precisión del modelo
- Usar más CVs de entrenamiento (mínimo 10 por profesión)
- Verificar que las profesiones sean suficientemente diferentes
- Asegurar que los CVs contengan información relevante

### Error de memoria
- Reducir el número de características (max_features en cv_classifier.py)
- Usar menos CVs de entrenamiento
- Cerrar otras aplicaciones

## 🎓 Profesiones de Ejemplo Incluidas

El generador de muestras incluye CVs para:
- **👨‍🌾 Agrónomo**: Especialistas en agricultura y producción agrícola
- **💻 Ingeniero de Software**: Desarrolladores y programadores
- **📈 Especialista en Marketing**: Marketing digital y tradicional
- **📊 Contador**: Contabilidad y finanzas
- **👨‍⚕️ Médico**: Profesionales de la salud

## 🔮 Próximas Mejoras

- [ ] Soporte para más formatos de archivo
- [ ] Análisis de habilidades específicas
- [ ] Exportación de resultados a Excel/CSV
- [ ] API REST para integración
- [ ] Análisis de experiencia laboral
- [ ] Detección automática de idiomas

## 📞 Soporte

Si encuentras problemas:
1. Verificar que todas las dependencias estén instaladas
2. Revisar que Tesseract OCR esté configurado
3. Asegurar que tienes suficientes CVs de entrenamiento
4. Verificar que los archivos CV sean válidos

## 📄 Licencia

Este proyecto es de código abierto bajo licencia MIT.

---

**¡Disfruta clasificando CVs con IA! 🚀**

*Versión 2.0 - Simplificada y optimizada para uso profesional*
