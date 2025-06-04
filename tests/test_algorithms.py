#!/usr/bin/env python3
"""
Prueba todos los algoritmos de machine learning disponibles
"""

import os
import time
from cv_classifier import CVClassifier
from cv_processor import CVProcessor

def test_all_algorithms():
    """Prueba todos los algoritmos disponibles"""
    print("=" * 60)
    print("🧪 PRUEBA DE TODOS LOS ALGORITMOS - CV CLASSIFIER v2.0")
    print("=" * 60)
    
    # Preparar datos de prueba
    processor = CVProcessor()
    
    # Datos de prueba simples
    test_data = [
        {
            'profession': 'Agrónomo',
            'text': 'Ingeniero agrónomo con experiencia en cultivos, agricultura sostenible, manejo de suelos, riego, fertilización, control de plagas, producción agrícola, investigación agrícola.',
            'status': 'success'
        },
        {
            'profession': 'Ingeniero de Software',
            'text': 'Desarrollador de software con experiencia en Python, JavaScript, React, Django, bases de datos, APIs, desarrollo web, programación, algoritmos, estructuras de datos.',
            'status': 'success'
        },
        {
            'profession': 'Agrónomo',
            'text': 'Especialista en agricultura con conocimientos en botánica, fitotecnia, entomología, fitopatología, mejoramiento genético, biotecnología agrícola, sistemas de producción.',
            'status': 'success'
        },
        {
            'profession': 'Ingeniero de Software',
            'text': 'Programador full-stack con experiencia en desarrollo de aplicaciones, software engineering, DevOps, cloud computing, microservicios, testing, CI/CD.',
            'status': 'success'
        }
    ]
    
    # Algoritmos a probar
    algorithms = [
        ('random_forest', 'Random Forest'),
        ('logistic_regression', 'Logistic Regression'),
        ('svm', 'Support Vector Machine'),
        ('naive_bayes', 'Naive Bayes')
    ]
    
    results = {}
    
    for algo_key, algo_name in algorithms:
        print(f"\n🤖 Probando {algo_name}...")
        print("-" * 40)
        
        try:
            # Crear clasificador
            classifier = CVClassifier()
            
            # Medir tiempo de entrenamiento
            start_time = time.time()
            
            # Entrenar modelo
            training_results = classifier.train_model(test_data, model_type=algo_key)
            
            training_time = time.time() - start_time
            
            # Probar predicción
            test_text = "Desarrollador Python con experiencia en machine learning y análisis de datos"
            
            start_pred_time = time.time()
            prediction = classifier.predict_cv(test_text)
            prediction_time = time.time() - start_pred_time
            
            # Guardar resultados
            results[algo_key] = {
                'name': algo_name,
                'accuracy': training_results['accuracy'],
                'training_time': training_time,
                'prediction_time': prediction_time,
                'prediction': prediction['predicted_profession'] if not prediction['error'] else 'Error',
                'confidence': prediction['confidence'] if not prediction['error'] else 0,
                'success': True,
                'error': None
            }
            
            print(f"✅ Entrenamiento exitoso")
            print(f"   Precisión: {training_results['accuracy']:.1%}")
            print(f"   Tiempo de entrenamiento: {training_time:.3f}s")
            print(f"   Tiempo de predicción: {prediction_time:.3f}s")
            print(f"   Predicción de prueba: {prediction['predicted_profession']} ({prediction['confidence']:.1%})")
            
        except Exception as e:
            print(f"❌ Error con {algo_name}: {str(e)}")
            results[algo_key] = {
                'name': algo_name,
                'success': False,
                'error': str(e)
            }
    
    # Mostrar resumen comparativo
    print("\n" + "=" * 60)
    print("📊 RESUMEN COMPARATIVO DE ALGORITMOS")
    print("=" * 60)
    
    successful_algos = [r for r in results.values() if r['success']]
    
    if successful_algos:
        print(f"{'Algoritmo':<25} {'Precisión':<12} {'T.Entrena':<12} {'T.Predice':<12} {'Predicción'}")
        print("-" * 75)
        
        for result in successful_algos:
            print(f"{result['name']:<25} "
                  f"{result['accuracy']:.1%}{'':>7} "
                  f"{result['training_time']:.3f}s{'':>6} "
                  f"{result['prediction_time']:.3f}s{'':>6} "
                  f"{result['prediction']}")
        
        # Encontrar el mejor en cada categoría
        print("\n🏆 MEJORES EN CADA CATEGORÍA:")
        
        best_accuracy = max(successful_algos, key=lambda x: x['accuracy'])
        print(f"   🎯 Mayor precisión: {best_accuracy['name']} ({best_accuracy['accuracy']:.1%})")
        
        fastest_training = min(successful_algos, key=lambda x: x['training_time'])
        print(f"   ⚡ Entrenamiento más rápido: {fastest_training['name']} ({fastest_training['training_time']:.3f}s)")
        
        fastest_prediction = min(successful_algos, key=lambda x: x['prediction_time'])
        print(f"   🚀 Predicción más rápida: {fastest_prediction['name']} ({fastest_prediction['prediction_time']:.3f}s)")
        
        highest_confidence = max(successful_algos, key=lambda x: x['confidence'])
        print(f"   🔒 Mayor confianza: {highest_confidence['name']} ({highest_confidence['confidence']:.1%})")
    
    # Mostrar errores si los hay
    failed_algos = [r for r in results.values() if not r['success']]
    if failed_algos:
        print(f"\n❌ ALGORITMOS CON ERRORES:")
        for result in failed_algos:
            print(f"   {result['name']}: {result['error']}")
    
    print(f"\n✅ Prueba completada: {len(successful_algos)}/{len(algorithms)} algoritmos funcionando")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if len(successful_algos) >= 2:
        print("   🌲 Para uso general: Random Forest (balance entre precisión y velocidad)")
        print("   ⚡ Para velocidad: Naive Bayes o Logistic Regression")
        print("   🎯 Para máxima precisión: Probar Random Forest y SVM")
        print("   📊 Para datasets pequeños: Logistic Regression o Naive Bayes")
    else:
        print("   ⚠️ Pocos algoritmos funcionando - verificar instalación de scikit-learn")
    
    return results

if __name__ == "__main__":
    test_all_algorithms()
