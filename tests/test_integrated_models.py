#!/usr/bin/env python3
"""
Prueba la integración de modelos tradicionales y Deep Learning
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_model_listing():
    """Prueba que se listen ambos tipos de modelos"""
    print("=" * 60)
    print("🧪 PRUEBA DE INTEGRACIÓN DE MODELOS")
    print("=" * 60)
    
    try:
        from src.models.cv_classifier import CVClassifier
        
        # Crear clasificador
        classifier = CVClassifier()
        
        # Listar modelos disponibles
        print("📋 Listando modelos disponibles...")
        models = classifier.list_available_models()
        
        if not models:
            print("⚠️ No se encontraron modelos")
            return True
        
        print(f"✅ Encontrados {len(models)} modelos:")
        
        traditional_models = []
        dl_models = []
        
        for model in models:
            is_dl = model.get('is_deep_learning', False)
            category = "🧠 Deep Learning" if is_dl else "🤖 ML Tradicional"
            
            print(f"   {category}: {model['display_name']}")
            print(f"      Tipo: {model['model_type']}")
            print(f"      Profesiones: {len(model['professions'])}")
            print(f"      Fecha: {model['creation_date']}")
            print()
            
            if is_dl:
                dl_models.append(model)
            else:
                traditional_models.append(model)
        
        print(f"📊 Resumen:")
        print(f"   🤖 Modelos ML Tradicional: {len(traditional_models)}")
        print(f"   🧠 Modelos Deep Learning: {len(dl_models)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def test_gui_integration():
    """Prueba la integración con la GUI"""
    print(f"\n🖥️ Probando integración con GUI...")
    
    try:
        # Verificar que las importaciones funcionen
        from src.gui.main_gui import CVClassifierGUI, DEEP_LEARNING_AVAILABLE
        
        print("✅ GUI importada correctamente")
        print(f"   Deep Learning disponible: {DEEP_LEARNING_AVAILABLE}")
        
        # Verificar que los métodos existan
        methods_to_check = [
            'refresh_models_list',
            'get_selected_model_info',
            'load_selected_model',
            'delete_selected_model',
            'refresh_model_selector',
            'load_model_from_selector'
        ]
        
        for method in methods_to_check:
            if hasattr(CVClassifierGUI, method):
                print(f"✅ Método {method} disponible")
            else:
                print(f"❌ Método {method} no encontrado")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración GUI: {e}")
        return False

def test_model_structure():
    """Prueba la estructura de datos de los modelos"""
    print(f"\n📊 Probando estructura de datos...")
    
    try:
        from src.models.cv_classifier import CVClassifier
        
        classifier = CVClassifier()
        models = classifier.list_available_models()
        
        if not models:
            print("⚠️ No hay modelos para probar estructura")
            return True
        
        # Verificar estructura del primer modelo
        model = models[0]
        required_fields = [
            'name', 'display_name', 'model_type', 'professions',
            'num_professions', 'creation_date', 'num_features', 'is_deep_learning'
        ]
        
        print(f"🔍 Verificando estructura del modelo: {model['display_name']}")
        
        for field in required_fields:
            if field in model:
                print(f"✅ Campo '{field}': {type(model[field]).__name__}")
            else:
                print(f"❌ Campo '{field}' faltante")
                return False
        
        # Verificar tipo de is_deep_learning
        if isinstance(model['is_deep_learning'], bool):
            print(f"✅ Campo 'is_deep_learning' es booleano: {model['is_deep_learning']}")
        else:
            print(f"❌ Campo 'is_deep_learning' no es booleano: {type(model['is_deep_learning'])}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def test_delete_functionality():
    """Prueba la funcionalidad de eliminación"""
    print(f"\n🗑️ Probando funcionalidad de eliminación...")
    
    try:
        from src.models.cv_classifier import CVClassifier
        
        classifier = CVClassifier()
        
        # Verificar que el método delete_model acepta el parámetro is_deep_learning
        import inspect
        sig = inspect.signature(classifier.delete_model)
        params = list(sig.parameters.keys())
        
        if 'is_deep_learning' in params:
            print("✅ Método delete_model acepta parámetro is_deep_learning")
        else:
            print("❌ Método delete_model no acepta parámetro is_deep_learning")
            return False
        
        print("✅ Funcionalidad de eliminación actualizada")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando eliminación: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de integración...")
    
    tests = [
        ("Listado de modelos", test_model_listing),
        ("Integración GUI", test_gui_integration),
        ("Estructura de datos", test_model_structure),
        ("Funcionalidad de eliminación", test_delete_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ ERROR en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print(f"\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas de integración pasaron!")
        print("   Los modelos tradicionales y Deep Learning están integrados correctamente")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("   Revisar la integración de modelos")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
