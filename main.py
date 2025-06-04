#!/usr/bin/env python3
"""
CV Classifier v2.0 - Archivo principal de ejecución
Clasificador inteligente de CVs por profesiones

Uso:
    python main.py              # Ejecutar interfaz gráfica
    python main.py --help       # Mostrar ayuda
    python main.py --test       # Ejecutar pruebas básicas
"""

import sys
import os
import argparse
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def check_dependencies():
    """Verifica que las dependencias básicas estén instaladas"""
    print("🔍 Verificando dependencias del CV Classifier v2.0...")
    print("=" * 50)

    missing_deps = []
    optional_deps = []

    # Dependencias básicas requeridas
    basic_deps = [
        ("PyQt6", "PyQt6", "Interfaz gráfica"),
        ("scikit-learn", "sklearn", "Machine Learning"),
        ("pandas", "pandas", "Manipulación de datos"),
        ("numpy", "numpy", "Operaciones numéricas"),
        ("joblib", "joblib", "Persistencia de modelos")
    ]

    print("📦 Dependencias básicas:")
    for name, module, description in basic_deps:
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'desconocida')
            print(f"   ✅ {name} ({version}) - {description}")
        except ImportError:
            missing_deps.append(name)
            print(f"   ❌ {name} - {description}")

    # Dependencias de procesamiento de documentos
    doc_deps = [
        ("python-docx", "docx", "Archivos Word"),
        ("PyPDF2", "PyPDF2", "Archivos PDF"),
        ("Pillow", "PIL", "Procesamiento de imágenes"),
        ("pytesseract", "pytesseract", "OCR"),
        ("opencv-python", "cv2", "Visión computacional")
    ]

    print(f"\n📄 Procesamiento de documentos:")
    for name, module, description in doc_deps:
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'desconocida')
            print(f"   ✅ {name} ({version}) - {description}")
        except ImportError:
            optional_deps.append(name)
            print(f"   ⚠️ {name} - {description} (opcional)")

    # Dependencias de Deep Learning (opcionales)
    dl_deps = [
        ("tensorflow", "tensorflow", "Deep Learning (LSTM, CNN)"),
        ("transformers", "transformers", "Modelos Transformer (BERT)"),
        ("torch", "torch", "PyTorch (backend alternativo)")
    ]

    print(f"\n🧠 Deep Learning (opcional):")
    dl_available = 0
    for name, module, description in dl_deps:
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'desconocida')
            print(f"   ✅ {name} ({version}) - {description}")
            dl_available += 1
        except ImportError:
            print(f"   ⚠️ {name} - {description} (opcional)")

    # Resumen
    print(f"\n📊 Resumen:")
    print(f"   🎯 Dependencias básicas: {len(basic_deps) - len(missing_deps)}/{len(basic_deps)}")
    print(f"   📄 Procesamiento docs: {len(doc_deps) - len(optional_deps)}/{len(doc_deps)}")
    print(f"   🧠 Deep Learning: {dl_available}/{len(dl_deps)}")

    if missing_deps:
        print(f"\n❌ Dependencias críticas faltantes:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print(f"\n💡 Instalar con:")
        print(f"   pip install {' '.join(missing_deps)}")
        print(f"   O: pip install -r requirements.txt")
        return False

    if optional_deps:
        print(f"\n⚠️ Dependencias opcionales faltantes:")
        for dep in optional_deps:
            print(f"   • {dep}")
        print(f"\n💡 Para funcionalidad completa:")
        print(f"   pip install {' '.join(optional_deps)}")

    if dl_available == 0:
        print(f"\n💡 Para habilitar Deep Learning:")
        print(f"   pip install tensorflow transformers")
        print(f"   O: pip install -r requirements-deep.txt")

    print(f"\n✅ Sistema básico listo para usar!")
    return True

def run_gui():
    """Ejecuta la interfaz gráfica"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.main_gui import CVClassifierGUI
        from src.config.settings import Settings
        
        # Asegurar que los directorios existan
        Settings.ensure_directories()
        
        # Crear aplicación
        app = QApplication(sys.argv)
        
        # Crear ventana principal
        window = CVClassifierGUI()
        window.show()
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Error importando GUI: {e}")
        print("Verifica que PyQt6 esté instalado: pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error ejecutando GUI: {e}")
        sys.exit(1)

def run_tests():
    """Ejecuta pruebas básicas del sistema"""
    print("🧪 Ejecutando pruebas básicas...")
    
    try:
        # Importar módulos principales
        from src.models.cv_classifier import CVClassifier
        from src.utils.cv_processor import CVProcessor
        from src.config.settings import Settings
        
        print("✅ Importaciones básicas exitosas")
        
        # Verificar configuración
        Settings.ensure_directories()
        print("✅ Directorios creados/verificados")
        
        # Probar procesador de CVs
        processor = CVProcessor()
        print("✅ CVProcessor inicializado")
        
        # Probar clasificador
        classifier = CVClassifier()
        print("✅ CVClassifier inicializado")
        
        # Verificar CVs de ejemplo
        sample_cvs_path = Settings.get_sample_cvs_path()
        if sample_cvs_path.exists():
            print(f"✅ CVs de ejemplo encontrados en: {sample_cvs_path}")
        else:
            print(f"⚠️ CVs de ejemplo no encontrados en: {sample_cvs_path}")
        
        print("\n🎉 Todas las pruebas básicas pasaron!")
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False

def show_info():
    """Muestra información del sistema"""
    print("=" * 60)
    print("🎯 CV CLASSIFIER v2.0")
    print("=" * 60)
    print("Clasificador inteligente de CVs por profesiones")
    print("Incluye Machine Learning tradicional y Deep Learning")
    print()
    print("📁 Estructura del proyecto:")
    print("├── main.py                 # Archivo principal (este)")
    print("├── src/")
    print("│   ├── models/             # Modelos ML y DL")
    print("│   ├── gui/                # Interfaz gráfica")
    print("│   ├── utils/              # Utilidades")
    print("│   └── config/             # Configuraciones")
    print("├── data/")
    print("│   └── sample_cvs/         # CVs de ejemplo")
    print("├── models/                 # Modelos entrenados")
    print("├── deep_models/            # Modelos Deep Learning")
    print("├── docs/                   # Documentación")
    print("└── tests/                  # Pruebas")
    print()
    print("🚀 Uso:")
    print("   python main.py           # Ejecutar interfaz gráfica")
    print("   python main.py --test    # Ejecutar pruebas")
    print("   python main.py --info    # Mostrar esta información")
    print()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="CV Classifier v2.0 - Clasificador inteligente de CVs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py              # Ejecutar interfaz gráfica
  python main.py --test       # Ejecutar pruebas básicas
  python main.py --info       # Mostrar información del sistema
        """
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Ejecutar pruebas básicas del sistema'
    )
    
    parser.add_argument(
        '--info', 
        action='store_true',
        help='Mostrar información del sistema'
    )
    
    parser.add_argument(
        '--check-deps', 
        action='store_true',
        help='Verificar dependencias'
    )
    
    args = parser.parse_args()
    
    # Mostrar información si se solicita
    if args.info:
        show_info()
        return
    
    # Verificar dependencias si se solicita
    if args.check_deps:
        print("🔍 Verificando dependencias...")
        if check_dependencies():
            print("\n✅ Todas las dependencias están disponibles")
        else:
            print("\n❌ Algunas dependencias faltan")
        return
    
    # Ejecutar pruebas si se solicita
    if args.test:
        if run_tests():
            print("\n✅ Sistema listo para usar")
        else:
            print("\n❌ Hay problemas con el sistema")
        return
    
    # Por defecto, ejecutar GUI
    print("🚀 Iniciando CV Classifier v2.0...")
    
    # Verificar dependencias básicas
    if not check_dependencies():
        print("\n❌ No se puede ejecutar sin las dependencias básicas")
        sys.exit(1)
    
    # Ejecutar interfaz gráfica
    run_gui()

if __name__ == "__main__":
    main()
