#!/usr/bin/env python3
"""
Prueba la funcionalidad de Deep Learning (sin entrenar modelos reales)
"""

import os
import sys

def test_deep_learning_imports():
    """Prueba las importaciones de Deep Learning"""
    print("=" * 60)
    print("🧪 PRUEBA DE DEEP LEARNING - CV CLASSIFIER v2.0")
    print("=" * 60)
    
    print("🔍 Verificando importaciones...")
    
    # Probar importación del clasificador DL
    try:
        from deep_learning_classifier import DeepLearningClassifier
        print("✅ DeepLearningClassifier importado correctamente")
        dl_available = True
    except ImportError as e:
        print(f"❌ Error importando DeepLearningClassifier: {e}")
        dl_available = False
    
    # Probar TensorFlow
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow disponible: {tf.__version__}")
        tf_available = True
    except ImportError:
        print("❌ TensorFlow no disponible")
        print("   Instalar con: pip install tensorflow")
        tf_available = False
    
    # Probar Transformers
    try:
        import transformers
        print(f"✅ Transformers disponible: {transformers.__version__}")
        transformers_available = True
    except ImportError:
        print("❌ Transformers no disponible")
        print("   Instalar con: pip install transformers")
        transformers_available = False
    
    return dl_available, tf_available, transformers_available

def test_deep_learning_classifier():
    """Prueba la funcionalidad básica del clasificador DL"""
    print(f"\n🧠 Probando DeepLearningClassifier...")
    
    try:
        from deep_learning_classifier import DeepLearningClassifier
        
        # Crear instancia
        dl_classifier = DeepLearningClassifier()
        print("✅ Instancia creada correctamente")
        
        # Verificar métodos
        methods = [
            'check_dependencies',
            'prepare_data_traditional', 
            'prepare_data_bert',
            'create_lstm_model',
            'create_cnn_model', 
            'create_bert_model',
            'train_model',
            'predict_cv',
            'save_model',
            'load_model'
        ]
        
        for method in methods:
            if hasattr(dl_classifier, method):
                print(f"✅ Método {method} disponible")
            else:
                print(f"❌ Método {method} no encontrado")
        
        # Probar verificación de dependencias
        try:
            dl_classifier.check_dependencies('lstm')
            print("✅ Verificación de dependencias LSTM exitosa")
        except ImportError as e:
            print(f"⚠️ Dependencias LSTM no disponibles: {e}")
        
        try:
            dl_classifier.check_dependencies('bert')
            print("✅ Verificación de dependencias BERT exitosa")
        except ImportError as e:
            print(f"⚠️ Dependencias BERT no disponibles: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando DeepLearningClassifier: {e}")
        return False

def test_gui_integration():
    """Prueba la integración con la GUI"""
    print(f"\n🖥️ Probando integración con GUI...")
    
    try:
        # Probar importación de GUI
        from main_gui import CVClassifierGUI, DEEP_LEARNING_AVAILABLE
        print("✅ GUI importada correctamente")
        print(f"   Deep Learning disponible en GUI: {DEEP_LEARNING_AVAILABLE}")
        
        # Verificar que la clase DeepLearningTrainingThread existe
        from main_gui import DeepLearningTrainingThread
        print("✅ DeepLearningTrainingThread disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando integración GUI: {e}")
        return False

def show_installation_guide():
    """Muestra guía de instalación"""
    print(f"\n📚 GUÍA DE INSTALACIÓN DEEP LEARNING")
    print("=" * 50)
    
    print("Para usar Deep Learning, instala las dependencias:")
    print()
    print("🔧 Instalación básica:")
    print("   pip install tensorflow")
    print("   pip install transformers")
    print()
    print("🚀 Instalación con GPU (opcional):")
    print("   pip install tensorflow-gpu")
    print()
    print("📦 Instalación completa:")
    print("   pip install tensorflow transformers torch")
    print()
    print("✅ Verificar instalación:")
    print("   python -c \"import tensorflow; print('TF:', tensorflow.__version__)\"")
    print("   python -c \"import transformers; print('HF:', transformers.__version__)\"")

def main():
    """Función principal de prueba"""
    
    # Probar importaciones
    dl_available, tf_available, transformers_available = test_deep_learning_imports()
    
    # Probar clasificador si está disponible
    if dl_available:
        classifier_ok = test_deep_learning_classifier()
    else:
        classifier_ok = False
    
    # Probar integración GUI
    gui_ok = test_gui_integration()
    
    # Resumen
    print(f"\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    print(f"DeepLearningClassifier: {'✅ OK' if dl_available else '❌ Error'}")
    print(f"TensorFlow: {'✅ OK' if tf_available else '❌ No disponible'}")
    print(f"Transformers: {'✅ OK' if transformers_available else '❌ No disponible'}")
    print(f"Funcionalidad básica: {'✅ OK' if classifier_ok else '❌ Error'}")
    print(f"Integración GUI: {'✅ OK' if gui_ok else '❌ Error'}")
    
    # Estado general
    if dl_available and tf_available and transformers_available:
        print(f"\n🎉 ¡Deep Learning completamente funcional!")
        print(f"   Puedes usar LSTM, CNN y BERT en la pestaña '🧠 Deep Learning'")
    elif dl_available:
        print(f"\n⚠️ Deep Learning parcialmente disponible")
        print(f"   Instala dependencias para funcionalidad completa")
        show_installation_guide()
    else:
        print(f"\n❌ Deep Learning no disponible")
        print(f"   Revisa la instalación del módulo deep_learning_classifier.py")
        show_installation_guide()
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if not tf_available:
        print("   🔧 Instalar TensorFlow para LSTM y CNN")
    if not transformers_available:
        print("   🤖 Instalar Transformers para BERT")
    if dl_available and tf_available:
        print("   🧪 Probar con datos reales en la GUI")
        print("   📊 Comparar con algoritmos tradicionales")
    
    return dl_available and gui_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
