# 🚀 INSTRUCCIONES RÁPIDAS - Clasificador de CVs v2.0

## ⚡ Inicio Rápido (5 minutos)

### 1. Ejecutar la aplicación
```bash
python run.py
```
El script verificará dependencias y configurará todo automáticamente.

### 2. Usar CVs de ejemplo (recomendado para primera vez)
Cuando el script pregunte, responde **"s"** para crear CVs de ejemplo.
Esto creará la carpeta `sample_cvs/` con CVs organizados por profesión.

### 3. Entrenar tu primer modelo
1. Abrir pestaña **"🎓 Entrenar Modelo"**
2. **Asignar nombre al modelo:** Escribir `mi_primer_modelo` en "Nombre del modelo"
3. **Seleccionar algoritmo:** Elegir entre 4 opciones disponibles:
   - 🌲 **Random Forest (Recomendado):** Robusto y preciso
   - 📈 **Logistic Regression:** Rápido y simple
   - 🎯 **SVM:** Excelente para datos complejos
   - ⚡ **Naive Bayes:** Muy rápido, bueno para textos
4. Agregar profesiones una por una:
   - Escribir "Agrónomo" → Seleccionar carpeta `sample_cvs/Agrónomo/`
   - Escribir "Ingeniero de Software" → Seleccionar carpeta `sample_cvs/Ingeniero de Software/`
   - Escribir "Especialista en Marketing" → Seleccionar carpeta `sample_cvs/Especialista en Marketing/`
5. Hacer clic en **"🚀 Entrenar y Guardar Modelo"**
6. Esperar 1-2 minutos - ¡El modelo se guarda automáticamente!

### 4. Clasificar un CV
1. Abrir pestaña **"🔍 Clasificar CV"**
2. **Seleccionar modelo:** En el dropdown "Modelo a usar" elegir el modelo deseado
3. **Cargar modelo:** Hacer clic en "📂 Cargar Modelo"
4. **Verificar:** Debe aparecer "✅ Modelo 'nombre_modelo' cargado"
5. Seleccionar cualquier CV de las carpetas de ejemplo
6. Hacer clic en **"🎯 Clasificar CV"**
7. ¡Ver los resultados con ranking de profesiones!

### 5. Experimentar con algoritmos (Recomendado)
1. **Probar diferentes algoritmos:** Entrenar el mismo conjunto de datos con diferentes algoritmos:
   - `modelo_rf_agricultura` → Random Forest + datos agricultura
   - `modelo_svm_agricultura` → SVM + mismos datos
   - `modelo_nb_agricultura` → Naive Bayes + mismos datos
2. **Comparar resultados:** Usar el mismo CV de prueba con todos los modelos
3. **Elegir el mejor:** Seleccionar el algoritmo que mejor funcione para tu caso

### 6. Usar múltiples modelos (Avanzado)
1. **Entrenar más modelos:** Repetir paso 3 con diferentes nombres y profesiones
2. **Cambiar entre modelos:** En "🔍 Clasificar CV" seleccionar el modelo apropiado
3. **Gestionar modelos:** Usar pestaña "📚 Mis Modelos" para ver, eliminar o cargar modelos

## 📁 Estructura de Carpetas para Entrenamiento

```
mis_cvs/
├── Agrónomo/
│   ├── cv1.pdf
│   ├── cv2.docx
│   └── cv3.jpg
├── Ingeniero/
│   ├── cv1.pdf
│   └── cv2.pdf
├── Marketing/
│   ├── cv1.docx
│   └── cv2.pdf
└── Contador/
    ├── cv1.pdf
    └── cv2.docx
```

## 🎯 Consejos para Mejores Resultados

### ✅ Hacer:
- Usar **5-10 CVs por profesión** mínimo
- Elegir **profesiones bien diferenciadas** (Agrónomo vs Ingeniero vs Marketing)
- Usar **CVs completos** con experiencia, educación y habilidades
- **Nombres descriptivos** para las profesiones

### ❌ Evitar:
- Profesiones muy similares (ej: "Ingeniero Civil" y "Ingeniero de Construcción")
- CVs muy cortos o incompletos
- Menos de 2 profesiones
- Archivos corruptos o ilegibles

## 🔧 Solución de Problemas Rápida

### "Error: No module named 'PyQt6'"
```bash
pip install PyQt6
```

### "Tesseract not found"
- **Windows**: Descargar desde https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

### "No se pudo extraer texto del CV"
- Verificar que el archivo no esté corrupto
- Para imágenes: asegurar que el texto sea legible
- Probar con otro archivo

### "Precisión muy baja"
- Usar más CVs de entrenamiento
- Verificar que las profesiones sean diferentes
- Revisar la calidad de los CVs

## 📊 Interpretación de Resultados

### Ejemplo de Resultado Bueno:
```
🎯 Profesión Recomendada: Agrónomo
🔥 Confianza: 89.2% (Alta)

✅ Interpretación: El CV coincide muy bien con esta profesión
```

### Ejemplo de Resultado Dudoso:
```
🎯 Profesión Recomendada: Marketing
🔥 Confianza: 52.1% (Baja)

❓ Interpretación: El CV no coincide claramente con ninguna profesión específica
```

## 🎓 Profesiones de Ejemplo Incluidas

Los CVs de ejemplo incluyen:
- **👨‍🌾 Agrónomo**: Especialistas en agricultura
- **💻 Ingeniero de Software**: Desarrolladores y programadores  
- **📈 Especialista en Marketing**: Marketing digital y tradicional
- **📊 Contador**: Contabilidad y finanzas
- **👨‍⚕️ Médico**: Profesionales de la salud

## 🚀 Flujo Completo de Trabajo

1. **Preparar datos** → Organizar CVs en carpetas por profesión
2. **Entrenar modelo** → Agregar profesiones y entrenar
3. **Guardar modelo** → Asignar nombre descriptivo y guardar
4. **Gestionar modelos** → Ver, cargar, eliminar modelos según necesidad
5. **Clasificar CVs** → Seleccionar CV y obtener recomendación
6. **Interpretar resultados** → Revisar confianza y ranking
7. **Mejorar modelo** → Agregar más CVs si es necesario

## 📚 Nueva Funcionalidad: Gestión de Modelos

### ✨ **¿Qué puedes hacer ahora?**
- **Guardar múltiples modelos** con nombres personalizados
- **Ver lista de todos tus modelos** con información detallada
- **Cargar el modelo que necesites** para cada tarea
- **Eliminar modelos** que ya no uses

### 🎯 **Ejemplos de Uso:**
```
modelo_agricultura_2024    → Para CVs del sector agrícola
modelo_tecnologia_2024     → Para CVs de IT y software
modelo_salud_2024          → Para CVs del sector salud
modelo_junior_2024         → Para posiciones entry-level
modelo_senior_2024         → Para posiciones de liderazgo
```

### 📋 **Cómo usar la gestión de modelos:**
1. **Entrenar** un modelo en "🎓 Entrenar Modelo"
2. **Guardar** con nombre en "📚 Mis Modelos"
3. **Ver lista** de todos tus modelos guardados
4. **Cargar** el modelo que necesites para clasificar
5. **Eliminar** modelos antiguos cuando no los necesites

## 📞 ¿Necesitas Ayuda?

1. **Leer el README.md** para información detallada
2. **Verificar que todas las dependencias estén instaladas**
3. **Probar con los CVs de ejemplo primero**
4. **Asegurar que tienes suficientes CVs por profesión**

---

**¡En 5 minutos tendrás tu clasificador funcionando! 🎉**
