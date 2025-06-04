# 🚀 Guía de Instalación - CV Classifier v2.0

## 📋 Opciones de Instalación

### **🎯 Opción 1: Instalación Básica (Recomendada)**
Solo Machine Learning tradicional (Random Forest, SVM, etc.)

```bash
pip install -r requirements.txt
```

### **🧠 Opción 2: Instalación Completa**
Incluye Deep Learning (LSTM, CNN, BERT)

```bash
pip install -r requirements.txt -r requirements-deep.txt
```

### **⚡ Opción 3: Instalación Rápida**
Dependencias mínimas para probar

```bash
pip install PyQt6 scikit-learn pandas numpy joblib python-docx PyPDF2 Pillow
```

## 🔧 Dependencias por Categoría

### **📦 Básicas (Siempre Requeridas):**
```bash
PyQt6                     # Interfaz gráfica
scikit-learn              # Machine Learning
pandas                    # Datos
numpy                     # Cálculos
joblib                    # Persistencia
```

### **📄 Procesamiento de Documentos:**
```bash
python-docx               # Word (.docx)
PyPDF2                    # PDF
Pillow                    # Imágenes
pytesseract               # OCR
opencv-python             # Visión computacional
```

### **🧠 Deep Learning (Opcional):**
```bash
tensorflow                # LSTM, CNN
transformers              # BERT
torch                     # PyTorch
```

## 🖥️ Instalación por Sistema Operativo

### **🪟 Windows:**
```bash
# Instalar Python 3.8+ desde python.org
pip install -r requirements.txt

# Para Deep Learning:
pip install tensorflow transformers
```

### **🐧 Linux (Ubuntu/Debian):**
```bash
# Actualizar sistema
sudo apt update
sudo apt install python3-pip python3-venv

# Crear entorno virtual
python3 -m venv cv_classifier_env
source cv_classifier_env/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### **🍎 macOS:**
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python

# Instalar dependencias
pip3 install -r requirements.txt
```

## 🔍 Verificación de Instalación

### **✅ Verificar Dependencias:**
```bash
python main.py --check-deps
```

### **🧪 Ejecutar Pruebas:**
```bash
python main.py --test
```

### **🚀 Ejecutar Aplicación:**
```bash
python main.py
```

## 🛠️ Solución de Problemas Comunes

### **❌ Error: "No module named 'PyQt6'"**
```bash
pip install PyQt6
```

### **❌ Error: "TensorFlow no disponible"**
```bash
# Para CPU solamente:
pip install tensorflow-cpu

# Para GPU (requiere CUDA):
pip install tensorflow-gpu
```

### **❌ Error: "pytesseract no encontrado"**
```bash
# Windows: Descargar e instalar Tesseract OCR
# https://github.com/UB-Mannheim/tesseract/wiki

# Linux:
sudo apt install tesseract-ocr

# macOS:
brew install tesseract
```

### **❌ Error de memoria con Deep Learning**
- Reducir `batch_size` en configuración
- Usar modelos más pequeños (CNN en lugar de BERT)
- Cerrar otras aplicaciones

### **❌ Error: "CUDA out of memory"**
```bash
# Instalar versión CPU:
pip uninstall tensorflow
pip install tensorflow-cpu
```

## 🎯 Configuraciones Recomendadas

### **💻 Computadora Básica:**
```bash
# Solo dependencias básicas
pip install PyQt6 scikit-learn pandas numpy joblib python-docx PyPDF2
```

### **🖥️ Computadora Potente:**
```bash
# Instalación completa
pip install -r requirements.txt -r requirements-deep.txt
```

### **🏢 Servidor/Producción:**
```bash
# Sin GUI (solo procesamiento)
pip install scikit-learn pandas numpy joblib python-docx PyPDF2 tensorflow transformers
```

## 📊 Verificación Final

Después de la instalación, ejecuta:

```bash
python main.py --info
```

Deberías ver:
```
🎯 CV CLASSIFIER v2.0
✅ PyQt6 disponible
✅ scikit-learn disponible  
✅ pandas disponible
✅ TensorFlow disponible (si instalaste Deep Learning)
✅ Transformers disponible (si instalaste Deep Learning)

🎉 ¡Sistema listo para usar!
```

## 🚀 Primeros Pasos

1. **Ejecutar aplicación:**
   ```bash
   python main.py
   ```

2. **Entrenar primer modelo:**
   - Ir a pestaña "🎓 Entrenar Modelo"
   - Agregar profesiones con CVs
   - Entrenar y guardar

3. **Clasificar CVs:**
   - Ir a pestaña "🔍 Clasificar CV"
   - Seleccionar modelo
   - Cargar archivo CV
   - ¡Clasificar!

## 📞 Soporte

Si tienes problemas:

1. **Verificar dependencias:** `python main.py --check-deps`
2. **Ejecutar pruebas:** `python main.py --test`
3. **Revisar logs** en la aplicación
4. **Consultar documentación** en `docs/`

---

**¡Listo para clasificar CVs con inteligencia artificial! 🎯**
