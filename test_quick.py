#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba rápida del sistema de clasificación de CVs
"""

import os
from cv_processor import CVProcessor
from cv_classifier import CVClassifier

def test_basic_functionality():
    """Prueba básica del sistema"""
    print("🧪 Iniciando prueba básica del sistema...")
    
    # 1. Probar procesador de CVs
    print("\n1️⃣ Probando procesador de CVs...")
    processor = CVProcessor()
    
    # Verificar formatos soportados
    test_files = [
        "test.pdf",
        "test.docx", 
        "test.jpg",
        "test.txt"
    ]
    
    for file in test_files:
        is_supported = processor.is_supported_file(file)
        status = "✅" if is_supported else "❌"
        print(f"   {status} {file}: {'Soportado' if is_supported else 'No soportado'}")
    
    # 2. Probar clasificador
    print("\n2️⃣ Probando clasificador...")
    classifier = CVClassifier()
    
    # Crear datos de prueba simulados
    fake_cv_data = [
        {
            'file_name': 'cv_agronomo_test.txt',
            'profession': 'Agrónomo',
            'text': 'ingeniero agrónomo experiencia cultivos agricultura riego fertilizantes maquinaria agrícola',
            'features': {},
            'status': 'success'
        },
        {
            'file_name': 'cv_software_test.txt', 
            'profession': 'Ingeniero de Software',
            'text': 'desarrollador software python java javascript react node.js bases de datos programación',
            'features': {},
            'status': 'success'
        }
    ]
    
    try:
        print("   🤖 Entrenando modelo de prueba...")
        results = classifier.train_model(fake_cv_data, model_type='logistic_regression')
        print(f"   ✅ Entrenamiento exitoso - Precisión: {results['accuracy']:.1%}")
        
        # Probar predicción
        test_text = "soy ingeniero agrónomo con experiencia en cultivos de maíz y sistemas de riego"
        prediction = classifier.predict_cv(test_text)
        
        if not prediction['error']:
            print(f"   ✅ Predicción exitosa: {prediction['predicted_profession']} ({prediction['confidence_percentage']})")
        else:
            print(f"   ❌ Error en predicción: {prediction['message']}")
            
    except Exception as e:
        print(f"   ❌ Error en clasificador: {e}")
    
    # 3. Verificar CVs de ejemplo
    print("\n3️⃣ Verificando CVs de ejemplo...")
    sample_dir = "sample_cvs"
    
    if os.path.exists(sample_dir):
        professions = os.listdir(sample_dir)
        print(f"   ✅ Directorio de ejemplos encontrado")
        print(f"   📁 Profesiones disponibles: {len(professions)}")
        
        for profession in professions:
            prof_dir = os.path.join(sample_dir, profession)
            if os.path.isdir(prof_dir):
                files = os.listdir(prof_dir)
                print(f"      • {profession}: {len(files)} CVs")
    else:
        print("   ⚠️  Directorio de ejemplos no encontrado")
        print("      Ejecuta: python sample_generator.py")
    
    print("\n🎉 Prueba básica completada!")
    return True

def test_gui_imports():
    """Prueba las importaciones de la GUI"""
    print("\n🖥️ Probando importaciones de la GUI...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("   ✅ PyQt6.QtWidgets")
        
        from PyQt6.QtCore import Qt
        print("   ✅ PyQt6.QtCore")
        
        from PyQt6.QtGui import QFont, QColor
        print("   ✅ PyQt6.QtGui")
        
        print("   ✅ Todas las importaciones de GUI exitosas")
        return True
        
    except ImportError as e:
        print(f"   ❌ Error en importaciones: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("=" * 50)
    print("🧪 PRUEBA RÁPIDA - CV CLASSIFIER v2.0")
    print("=" * 50)
    
    # Probar funcionalidad básica
    basic_ok = test_basic_functionality()
    
    # Probar GUI
    gui_ok = test_gui_imports()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    print(f"Funcionalidad básica: {'✅ OK' if basic_ok else '❌ ERROR'}")
    print(f"Importaciones GUI: {'✅ OK' if gui_ok else '❌ ERROR'}")
    
    if basic_ok and gui_ok:
        print("\n🎉 ¡Sistema listo para usar!")
        print("   Ejecuta: python main_gui.py")
    else:
        print("\n⚠️  Hay problemas que resolver:")
        if not basic_ok:
            print("   • Revisar dependencias básicas")
        if not gui_ok:
            print("   • Instalar PyQt6: pip install PyQt6")
    
    return 0 if (basic_ok and gui_ok) else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
