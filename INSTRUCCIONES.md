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
2. Agregar profesiones una por una:
   - Escribir "Agrónomo" → Seleccionar carpeta `sample_cvs/Agrónomo/`
   - Escribir "Ingeniero de Software" → Seleccionar carpeta `sample_cvs/Ingeniero de Software/`
   - Escribir "Especialista en Marketing" → Seleccionar carpeta `sample_cvs/Especialista en Marketing/`
3. Hacer clic en **"🚀 Entrenar Modelo"**
4. Esperar 1-2 minutos

### 4. Clasificar un CV
1. Abrir pestaña **"🔍 Clasificar CV"**
2. Seleccionar cualquier CV de las carpetas de ejemplo
3. Hacer clic en **"🎯 Clasificar CV"**
4. ¡Ver los resultados!

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
3. **Clasificar CVs** → Seleccionar CV y obtener recomendación
4. **Interpretar resultados** → Revisar confianza y ranking
5. **Mejorar modelo** → Agregar más CVs si es necesario

## 📞 ¿Necesitas Ayuda?

1. **Leer el README.md** para información detallada
2. **Verificar que todas las dependencias estén instaladas**
3. **Probar con los CVs de ejemplo primero**
4. **Asegurar que tienes suficientes CVs por profesión**

---

**¡En 5 minutos tendrás tu clasificador funcionando! 🎉**
