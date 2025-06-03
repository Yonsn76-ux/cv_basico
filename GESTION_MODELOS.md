# 📚 Gestión de Modelos - CV Classifier v2.0

## 🎯 Nueva Funcionalidad: Múltiples Modelos

Ahora puedes crear, guardar y gestionar múltiples modelos entrenados con nombres personalizados. Esto te permite tener diferentes modelos para diferentes propósitos.

## 🌟 Características Principales

### ✅ **Guardar Modelos con Nombres Personalizados**
- Asigna nombres descriptivos a tus modelos
- Evita sobrescribir modelos anteriores
- Metadatos automáticos (fecha, tipo, profesiones)

### ✅ **Lista de Modelos Disponibles**
- Ve todos tus modelos en una tabla organizada
- Información detallada de cada modelo
- Estado actual (cargado/disponible)

### ✅ **Cargar Modelos Específicos**
- Cambia entre diferentes modelos fácilmente
- Carga el modelo que necesites para cada tarea
- Actualización automática de la interfaz

### ✅ **Eliminar Modelos**
- Limpia modelos que ya no necesites
- Confirmación de seguridad
- Eliminación completa de archivos

## 🚀 Cómo Usar la Gestión de Modelos

### 1. **Entrenar y Guardar un Modelo**

1. **Entrenar modelo:**
   - Ve a la pestaña "🎓 Entrenar Modelo"
   - Configura tus profesiones y entrena como siempre

2. **Guardar con nombre:**
   - Ve a la pestaña "📚 Mis Modelos"
   - En la sección "💾 Guardar Modelo Actual"
   - Escribe un nombre descriptivo (ej: `modelo_agricultura_2024`)
   - Haz clic en "💾 Guardar Modelo"

### 2. **Ver y Gestionar Modelos**

En la pestaña "📚 Mis Modelos" verás una tabla con:
- **Nombre**: Nombre que le diste al modelo
- **Tipo**: Algoritmo usado (RandomForest, LogisticRegression)
- **Profesiones**: Lista de profesiones que puede clasificar
- **Fecha**: Cuándo fue creado
- **Estado**: Si está cargado actualmente o disponible

### 3. **Cargar un Modelo Específico**

1. Selecciona el modelo en la tabla
2. Haz clic en "📂 Cargar Modelo"
3. El modelo se cargará y estará listo para clasificar

### 4. **Ver Detalles de un Modelo**

1. Selecciona el modelo en la tabla
2. Haz clic en "ℹ️ Ver Detalles"
3. Ve información completa del modelo

### 5. **Eliminar un Modelo**

1. Selecciona el modelo en la tabla
2. Haz clic en "🗑️ Eliminar Modelo"
3. Confirma la eliminación

## 💡 Casos de Uso Prácticos

### **Modelo por Industria:**
```
modelo_tecnologia_2024    → Ingeniero Software, Data Scientist, DevOps
modelo_agricultura_2024  → Agrónomo, Veterinario, Técnico Agrícola
modelo_salud_2024        → Médico, Enfermero, Farmacéutico
```

### **Modelo por Nivel:**
```
modelo_junior_2024       → Posiciones junior/entry-level
modelo_senior_2024       → Posiciones senior/management
modelo_especialista_2024 → Roles muy específicos
```

### **Modelo por Región:**
```
modelo_latam_2024        → Profesiones comunes en Latinoamérica
modelo_europa_2024       → Profesiones específicas de Europa
modelo_usa_2024          → Mercado laboral estadounidense
```

## 📁 Estructura de Archivos

Cada modelo guardado genera 4 archivos en la carpeta `models/`:

```
models/
├── modelo_agricultura_2024_vectorizer.pkl    # Procesamiento de texto
├── modelo_agricultura_2024_classifier.pkl    # Algoritmo entrenado
├── modelo_agricultura_2024_encoder.pkl       # Codificación de profesiones
└── modelo_agricultura_2024_metadata.pkl      # Información del modelo
```

## 🔧 Consejos y Mejores Prácticas

### ✅ **Nombres Descriptivos:**
- `modelo_agricultura_enero2024`
- `clasificador_tecnologia_v2`
- `modelo_salud_especialistas`

### ✅ **Organización por Propósito:**
- Modelos por industria
- Modelos por nivel de experiencia
- Modelos por región geográfica

### ✅ **Versionado:**
- `modelo_base_v1`, `modelo_base_v2`
- Incluye fecha en el nombre
- Documenta cambios importantes

### ❌ **Evitar:**
- Nombres genéricos como "modelo1", "test"
- Caracteres especiales (solo letras, números, guiones)
- Sobrescribir modelos importantes sin respaldo

## 🎯 Flujo de Trabajo Recomendado

### **Para Empresas de Reclutamiento:**
1. **Crear modelos especializados:**
   - `modelo_it_2024` para posiciones tecnológicas
   - `modelo_ventas_2024` para roles comerciales
   - `modelo_admin_2024` para posiciones administrativas

2. **Usar el modelo apropiado:**
   - Cargar `modelo_it_2024` cuando lleguen CVs de tecnología
   - Cambiar a `modelo_ventas_2024` para posiciones comerciales

### **Para Consultores de Carrera:**
1. **Modelos por nivel:**
   - `modelo_recien_graduados` para estudiantes
   - `modelo_profesionales_senior` para ejecutivos

2. **Análisis comparativo:**
   - Probar el mismo CV con diferentes modelos
   - Ver en qué áreas encaja mejor la persona

## 🔄 Migración de Modelos Anteriores

Si ya tenías un modelo entrenado antes de esta actualización:

1. **El modelo anterior seguirá funcionando** en la pestaña de clasificación
2. **Para guardarlo con nombre:** Entrena un nuevo modelo y guárdalo con el nombre que prefieras
3. **Los archivos antiguos** están en `models/` con nombres genéricos

## 🆘 Solución de Problemas

### **Error: "No se encontraron modelos"**
- Verifica que la carpeta `models/` exista
- Entrena al menos un modelo primero

### **Error: "Nombre inválido"**
- Usa solo letras, números, guiones y guiones bajos
- No uses espacios ni caracteres especiales

### **Error: "No se puede cargar el modelo"**
- Verifica que todos los archivos del modelo existan
- Refresca la lista con el botón "🔄 Actualizar Lista"

### **Modelo no aparece en la lista**
- Haz clic en "🔄 Actualizar Lista"
- Verifica que se guardó correctamente

## 🎉 ¡Beneficios de la Gestión de Modelos!

✅ **Flexibilidad**: Diferentes modelos para diferentes necesidades
✅ **Organización**: Mantén tus modelos ordenados y documentados
✅ **Eficiencia**: Cambia rápidamente entre modelos especializados
✅ **Seguridad**: No pierdas modelos importantes por sobrescritura
✅ **Escalabilidad**: Crea tantos modelos como necesites

---

**¡Ahora puedes tener una biblioteca completa de modelos especializados! 🚀**
