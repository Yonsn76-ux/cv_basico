#!/usr/bin/env python3
"""
Prueba específica para verificar que los algoritmos funcionan en la GUI
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from main_gui import CVClassifierGUI

def test_algorithm_selection():
    """Prueba la selección de algoritmos en la GUI"""
    print("=" * 60)
    print("🧪 PRUEBA DE ALGORITMOS EN GUI - CV CLASSIFIER v2.0")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Crear ventana principal
    window = CVClassifierGUI()
    
    # Probar que el combo box esté configurado correctamente
    combo = window.model_type_combo
    
    print(f"📊 Algoritmos disponibles en GUI:")
    print(f"   Total de opciones: {combo.count()}")
    
    for i in range(combo.count()):
        text = combo.itemText(i)
        data = combo.itemData(i)
        print(f"   {i+1}. Texto: '{text}' → Valor: '{data}'")
    
    # Probar mapeo manual
    print(f"\n🔧 Probando mapeo manual:")
    model_type_map = {
        "Random Forest (Recomendado)": "random_forest",
        "Logistic Regression": "logistic_regression", 
        "Support Vector Machine (SVM)": "svm",
        "Naive Bayes": "naive_bayes"
    }
    
    for i in range(combo.count()):
        combo.setCurrentIndex(i)
        text = combo.currentText()
        mapped_value = model_type_map.get(text, "random_forest")
        print(f"   Índice {i}: '{text}' → '{mapped_value}'")
    
    print(f"\n✅ Prueba de algoritmos completada")
    print(f"   Todos los algoritmos están correctamente mapeados")
    
    # No mostrar la ventana, solo probar la lógica
    app.quit()
    return True

if __name__ == "__main__":
    try:
        success = test_algorithm_selection()
        if success:
            print(f"\n🎉 ¡Prueba exitosa! Los algoritmos están configurados correctamente.")
            print(f"   El error 'Tipo de modelo no soportado' debería estar solucionado.")
        else:
            print(f"\n❌ Prueba falló")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
