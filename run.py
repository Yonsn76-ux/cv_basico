#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejecución para el Clasificador de CVs por Profesiones v2.0
Incluye verificación de dependencias y configuración automática
"""

import sys
import os
import subprocess
import importlib

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required_packages = [
        'PyQt6',
        'PyPDF2', 
        'pytesseract',
        'docx',
        'cv2',
        'PIL',
        'pandas',
        'numpy',
        'sklearn',
        'tensorflow',
        'matplotlib',
        'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'docx':
                importlib.import_module('docx')
            elif package == 'cv2':
                importlib.import_module('cv2')
            elif package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'sklearn':
                importlib.import_module('sklearn')
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    return missing_packages

def install_dependencies():
    """Instala las dependencias faltantes"""
    print("\n📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def check_tesseract():
    """Verifica Tesseract OCR"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR {version} encontrado")
        return True
    except Exception:
        print("⚠️  Tesseract OCR no encontrado")
        return False

def create_sample_data():
    """Pregunta si crear datos de ejemplo"""
    response = input("\n¿Crear CVs de ejemplo para probar el sistema? (s/n): ").lower()
    if response == 's':
        try:
            from sample_generator import create_sample_cvs
            files, directory = create_sample_cvs()
            print(f"\n✅ CVs de ejemplo creados en: {directory}")
            print("   Puedes usar estos CVs para entrenar tu primer modelo")
            return True
        except Exception as e:
            print(f"❌ Error creando CVs de ejemplo: {e}")
            return False
    return False

def run_application():
    """Ejecuta la aplicación principal"""
    try:
        print("\n🚀 Iniciando Clasificador de CVs por Profesiones v2.0...")
        from main_gui import main
        return main()
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Función principal"""
    print("=" * 60)
    print("🎯 CLASIFICADOR DE CVs POR PROFESIONES v2.0")
    print("=" * 60)
    print()
    
    # Verificar Python
    if not check_python_version():
        input("\nPresiona Enter para salir...")
        return 1
    
    print("\n🔍 Verificando dependencias...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n❌ Faltan {len(missing)} dependencias:")
        for pkg in missing:
            print(f"   • {pkg}")
        
        response = input("\n¿Instalar dependencias automáticamente? (s/n): ").lower()
        if response == 's':
            if not install_dependencies():
                print("\n❌ Error en la instalación")
                input("Presiona Enter para salir...")
                return 1
        else:
            print("\nInstala las dependencias manualmente:")
            print("pip install -r requirements.txt")
            input("Presiona Enter para salir...")
            return 1
    
    # Verificar Tesseract
    print("\n🔍 Verificando Tesseract OCR...")
    tesseract_ok = check_tesseract()
    
    if not tesseract_ok:
        print("\n⚠️  Tesseract OCR no está instalado")
        print("Sin Tesseract no podrás procesar imágenes con OCR")
        print("\nInstrucciones de instalación:")
        print("• Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("• Linux: sudo apt-get install tesseract-ocr tesseract-ocr-spa")
        print("• macOS: brew install tesseract tesseract-lang")
        
        response = input("\n¿Continuar sin OCR? (s/n): ").lower()
        if response != 's':
            return 1
    
    # Crear directorio de modelos
    os.makedirs('models', exist_ok=True)
    
    # Preguntar sobre datos de ejemplo
    create_sample_data()
    
    # Ejecutar aplicación
    print("\n" + "=" * 60)
    print("🎉 ¡TODO LISTO!")
    print("=" * 60)
    
    if tesseract_ok:
        print("✅ Todas las funcionalidades disponibles")
    else:
        print("⚠️  Funcionalidad limitada (sin OCR para imágenes)")
    
    input("\nPresiona Enter para iniciar la aplicación...")
    
    return run_application()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Aplicación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)
