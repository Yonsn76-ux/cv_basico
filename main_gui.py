# -*- coding: utf-8 -*-
"""
Interfaz gráfica principal para el Clasificador de CVs por Profesiones
Versión simplificada y fácil de usar
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QGroupBox, QGridLayout, QFileDialog, QMessageBox,
                            QTabWidget, QListWidget, QComboBox, QProgressBar,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QSplitter, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor

from cv_processor import CVProcessor
from cv_classifier import CVClassifier

class TrainingThread(QThread):
    """Hilo para entrenamiento en segundo plano"""
    progress_updated = pyqtSignal(str)
    training_completed = pyqtSignal(bool, dict, str)
    
    def __init__(self, profession_folders, model_type):
        super().__init__()
        self.profession_folders = profession_folders
        self.model_type = model_type
    
    def run(self):
        try:
            self.progress_updated.emit("🔄 Iniciando procesamiento de CVs...")
            
            # Procesar CVs por profesión
            processor = CVProcessor()
            all_cv_data = []
            
            for profession, folder_path in self.profession_folders.items():
                self.progress_updated.emit(f"📁 Procesando profesión: {profession}")
                cv_results = processor.process_cv_folder(folder_path, profession)
                all_cv_data.extend(cv_results)
            
            if not all_cv_data:
                self.training_completed.emit(False, {}, "No se encontraron CVs válidos")
                return
            
            self.progress_updated.emit(f"✅ Procesados {len(all_cv_data)} CVs")
            
            # Entrenar modelo
            self.progress_updated.emit("🤖 Entrenando modelo de clasificación...")
            classifier = CVClassifier()
            
            results = classifier.train_model(all_cv_data, model_type=self.model_type)
            
            # Guardar modelo
            self.progress_updated.emit("💾 Guardando modelo...")
            classifier.save_model()
            
            self.training_completed.emit(True, results, "¡Entrenamiento completado exitosamente!")
            
        except Exception as e:
            self.training_completed.emit(False, {}, f"Error durante el entrenamiento: {str(e)}")

class CVClassifierGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = CVProcessor()
        self.classifier = CVClassifier()
        self.profession_folders = {}
        self.training_thread = None
        
        self.init_ui()
        self.load_model_if_exists()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("🎯 Clasificador de CVs por Profesiones v2.0")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🎯 Clasificador de CVs por Profesiones")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Crear pestañas
        self.create_tabs(main_layout)
        
        # Aplicar estilos
        self.apply_styles()
    
    def create_tabs(self, layout):
        """Crea las pestañas principales"""
        tabs = QTabWidget()
        
        # Pestaña 1: Entrenamiento
        training_tab = QWidget()
        self.create_training_tab(training_tab)
        tabs.addTab(training_tab, "🎓 Entrenar Modelo")
        
        # Pestaña 2: Clasificación
        classification_tab = QWidget()
        self.create_classification_tab(classification_tab)
        tabs.addTab(classification_tab, "🔍 Clasificar CV")
        
        layout.addWidget(tabs)
    
    def create_training_tab(self, tab):
        """Crea la pestaña de entrenamiento"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Instrucciones
        instructions = QLabel("""
        <b>📋 Instrucciones para entrenar el modelo:</b><br>
        1. Organiza tus CVs en carpetas por profesión (ej: "Agrónomo", "Ingeniero", "Marketing")<br>
        2. Agrega cada profesión y selecciona su carpeta correspondiente<br>
        3. Configura el tipo de modelo y entrena<br>
        4. ¡El modelo estará listo para clasificar nuevos CVs!
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 5px;
                padding: 15px;
                color: #0c5460;
            }
        """)
        layout.addWidget(instructions)
        
        # Configuración de profesiones
        self.create_profession_config(layout)
        
        # Configuración de entrenamiento
        self.create_training_config(layout)
        
        # Log de entrenamiento
        self.create_training_log(layout)
    
    def create_profession_config(self, layout):
        """Crea la sección de configuración de profesiones"""
        prof_group = QGroupBox("👥 Configurar Profesiones")
        prof_layout = QVBoxLayout(prof_group)
        
        # Agregar nueva profesión
        add_layout = QHBoxLayout()
        
        self.profession_name_input = QLineEdit()
        self.profession_name_input.setPlaceholderText("Nombre de la profesión (ej: Agrónomo)")
        
        self.btn_select_folder = QPushButton("📁 Seleccionar Carpeta")
        self.btn_select_folder.clicked.connect(self.select_profession_folder)
        
        self.btn_add_profession = QPushButton("➕ Agregar Profesión")
        self.btn_add_profession.clicked.connect(self.add_profession)
        self.btn_add_profession.setEnabled(False)
        
        add_layout.addWidget(QLabel("Profesión:"))
        add_layout.addWidget(self.profession_name_input)
        add_layout.addWidget(self.btn_select_folder)
        add_layout.addWidget(self.btn_add_profession)
        
        prof_layout.addLayout(add_layout)
        
        # Lista de profesiones configuradas
        self.profession_list = QListWidget()
        self.profession_list.setMaximumHeight(150)
        prof_layout.addWidget(QLabel("Profesiones configuradas:"))
        prof_layout.addWidget(self.profession_list)
        
        # Botón para limpiar lista
        self.btn_clear_professions = QPushButton("🗑️ Limpiar Lista")
        self.btn_clear_professions.clicked.connect(self.clear_professions)
        prof_layout.addWidget(self.btn_clear_professions)
        
        layout.addWidget(prof_group)
    
    def create_training_config(self, layout):
        """Crea la sección de configuración de entrenamiento"""
        config_group = QGroupBox("⚙️ Configuración del Entrenamiento")
        config_layout = QHBoxLayout(config_group)
        
        # Tipo de modelo
        config_layout.addWidget(QLabel("Tipo de modelo:"))
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["random_forest", "logistic_regression"])
        self.model_type_combo.setCurrentText("random_forest")
        config_layout.addWidget(self.model_type_combo)
        
        # Botón de entrenamiento
        self.btn_train = QPushButton("🚀 Entrenar Modelo")
        self.btn_train.clicked.connect(self.start_training)
        self.btn_train.setEnabled(False)
        self.btn_train.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        config_layout.addWidget(self.btn_train)
        
        config_layout.addStretch()
        layout.addWidget(config_group)
    
    def create_training_log(self, layout):
        """Crea el log de entrenamiento"""
        log_group = QGroupBox("📊 Progreso del Entrenamiento")
        log_layout = QVBoxLayout(log_group)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        log_layout.addWidget(self.progress_bar)
        
        # Log de texto
        self.training_log = QTextEdit()
        self.training_log.setReadOnly(True)
        self.training_log.setMaximumHeight(200)
        self.training_log.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid #34495e;
                border-radius: 5px;
            }
        """)
        log_layout.addWidget(self.training_log)
        
        layout.addWidget(log_group)
    
    def create_classification_tab(self, tab):
        """Crea la pestaña de clasificación"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Estado del modelo
        self.create_model_status(layout)
        
        # Selección de CV
        self.create_cv_selection(layout)
        
        # Resultados
        self.create_results_section(layout)
    
    def create_model_status(self, layout):
        """Crea la sección de estado del modelo"""
        status_group = QGroupBox("🤖 Estado del Modelo")
        status_layout = QVBoxLayout(status_group)
        
        self.model_status_label = QLabel("❌ Modelo no cargado")
        self.model_status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.model_status_label.setStyleSheet("color: #e74c3c; padding: 10px;")
        status_layout.addWidget(self.model_status_label)
        
        # Información del modelo
        self.model_info_text = QTextEdit()
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(100)
        self.model_info_text.setPlaceholderText("La información del modelo aparecerá aquí...")
        status_layout.addWidget(self.model_info_text)
        
        # Botón para recargar modelo
        self.btn_reload_model = QPushButton("🔄 Recargar Modelo")
        self.btn_reload_model.clicked.connect(self.load_model_if_exists)
        status_layout.addWidget(self.btn_reload_model)
        
        layout.addWidget(status_group)
    
    def create_cv_selection(self, layout):
        """Crea la sección de selección de CV"""
        cv_group = QGroupBox("📄 Seleccionar CV para Clasificar")
        cv_layout = QVBoxLayout(cv_group)
        
        # Selección de archivo
        file_layout = QHBoxLayout()
        
        self.selected_file_label = QLabel("Ningún archivo seleccionado")
        self.selected_file_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        self.btn_select_cv = QPushButton("📁 Seleccionar CV")
        self.btn_select_cv.clicked.connect(self.select_cv_file)
        
        self.btn_classify = QPushButton("🎯 Clasificar CV")
        self.btn_classify.clicked.connect(self.classify_cv)
        self.btn_classify.setEnabled(False)
        self.btn_classify.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        file_layout.addWidget(QLabel("Archivo:"))
        file_layout.addWidget(self.selected_file_label, 1)
        file_layout.addWidget(self.btn_select_cv)
        file_layout.addWidget(self.btn_classify)
        
        cv_layout.addLayout(file_layout)
        layout.addWidget(cv_group)
    
    def create_results_section(self, layout):
        """Crea la sección de resultados"""
        results_group = QGroupBox("📊 Resultados de la Clasificación")
        results_layout = QVBoxLayout(results_group)
        
        # Splitter para dividir resultados
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Resultado principal
        self.main_result = QTextEdit()
        self.main_result.setReadOnly(True)
        self.main_result.setPlaceholderText("Los resultados aparecerán aquí después de clasificar un CV...")
        splitter.addWidget(self.main_result)
        
        # Panel derecho - Ranking de profesiones
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(2)
        self.ranking_table.setHorizontalHeaderLabels(["Profesión", "Probabilidad"])
        header = self.ranking_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        splitter.addWidget(self.ranking_table)
        
        splitter.setSizes([400, 300])
        results_layout.addWidget(splitter)
        
        layout.addWidget(results_group)

    def apply_styles(self):
        """Aplica estilos generales"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

    def select_profession_folder(self):
        """Selecciona carpeta para una profesión"""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta con CVs de la profesión")
        if folder:
            self.selected_folder = folder
            self.btn_add_profession.setEnabled(bool(self.profession_name_input.text().strip()))

    def add_profession(self):
        """Agrega una profesión a la lista"""
        profession_name = self.profession_name_input.text().strip()

        if not profession_name:
            QMessageBox.warning(self, "Advertencia", "Ingresa el nombre de la profesión")
            return

        if not hasattr(self, 'selected_folder'):
            QMessageBox.warning(self, "Advertencia", "Selecciona una carpeta primero")
            return

        if profession_name in self.profession_folders:
            QMessageBox.warning(self, "Advertencia", "Esta profesión ya está agregada")
            return

        # Verificar que la carpeta tenga archivos válidos
        valid_files = [f for f in os.listdir(self.selected_folder)
                      if self.processor.is_supported_file(os.path.join(self.selected_folder, f))]

        if not valid_files:
            QMessageBox.warning(self, "Advertencia",
                              "La carpeta seleccionada no contiene archivos de CV válidos")
            return

        # Agregar profesión
        self.profession_folders[profession_name] = self.selected_folder
        self.profession_list.addItem(f"📁 {profession_name} ({len(valid_files)} CVs)")

        # Limpiar campos
        self.profession_name_input.clear()
        delattr(self, 'selected_folder')
        self.btn_add_profession.setEnabled(False)

        # Habilitar entrenamiento si hay al menos 2 profesiones
        self.btn_train.setEnabled(len(self.profession_folders) >= 2)

        QMessageBox.information(self, "Éxito",
                              f"Profesión '{profession_name}' agregada con {len(valid_files)} CVs")

    def clear_professions(self):
        """Limpia la lista de profesiones"""
        self.profession_folders.clear()
        self.profession_list.clear()
        self.btn_train.setEnabled(False)

    def start_training(self):
        """Inicia el entrenamiento del modelo"""
        if len(self.profession_folders) < 2:
            QMessageBox.warning(self, "Advertencia",
                              "Se necesitan al menos 2 profesiones para entrenar")
            return

        # Confirmar entrenamiento
        reply = QMessageBox.question(self, 'Confirmar entrenamiento',
                                   f'¿Entrenar modelo con {len(self.profession_folders)} profesiones?\n'
                                   f'Profesiones: {", ".join(self.profession_folders.keys())}',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.Yes)

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Configurar UI para entrenamiento
        self.btn_train.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Progreso indeterminado
        self.training_log.clear()

        # Iniciar entrenamiento en hilo separado
        model_type = self.model_type_combo.currentText()
        self.training_thread = TrainingThread(self.profession_folders, model_type)
        self.training_thread.progress_updated.connect(self.update_training_log)
        self.training_thread.training_completed.connect(self.training_finished)
        self.training_thread.start()

    def update_training_log(self, message):
        """Actualiza el log de entrenamiento"""
        self.training_log.append(f"[{QTimer().remainingTime()}] {message}")
        cursor = self.training_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.training_log.setTextCursor(cursor)

    def training_finished(self, success, results, message):
        """Maneja la finalización del entrenamiento"""
        # Restaurar UI
        self.btn_train.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            # Mostrar resultados
            results_text = f"""
            ✅ ¡Entrenamiento completado exitosamente!

            📊 Resultados:
            • Precisión: {results['accuracy']:.1%}
            • Muestras de entrenamiento: {results['train_samples']}
            • Muestras de prueba: {results['test_samples']}
            • Características extraídas: {results['features']}
            • Profesiones: {', '.join(results['classes'])}

            💾 Modelo guardado en la carpeta 'models/'
            """

            self.update_training_log(results_text)
            QMessageBox.information(self, "Entrenamiento completado",
                                  "¡El modelo se entrenó exitosamente!\n"
                                  f"Precisión: {results['accuracy']:.1%}")

            # Cargar el modelo recién entrenado
            self.load_model_if_exists()
        else:
            self.update_training_log(f"❌ Error: {message}")
            QMessageBox.critical(self, "Error en entrenamiento", f"El entrenamiento falló:\n{message}")

    def load_model_if_exists(self):
        """Carga el modelo si existe"""
        try:
            success = self.classifier.load_model()
            if success:
                self.model_status_label.setText("✅ Modelo cargado correctamente")
                self.model_status_label.setStyleSheet("color: #27ae60; padding: 10px; font-weight: bold;")

                # Mostrar información del modelo
                info = self.classifier.get_model_info()
                if info:
                    info_text = f"""
                    <b>Información del Modelo:</b><br>
                    • Tipo: {info['model_type']}<br>
                    • Profesiones: {info['num_professions']}<br>
                    • Lista: {', '.join(info['professions'])}<br>
                    • Características: {info['num_features']:,}
                    """
                    self.model_info_text.setHtml(info_text)

                # Habilitar clasificación
                self.update_classification_ui()
            else:
                self.model_status_label.setText("❌ No hay modelo entrenado")
                self.model_status_label.setStyleSheet("color: #e74c3c; padding: 10px; font-weight: bold;")
                self.model_info_text.clear()
        except Exception as e:
            print(f"Error cargando modelo: {e}")

    def update_classification_ui(self):
        """Actualiza la UI de clasificación según el estado del modelo"""
        model_loaded = self.classifier.is_trained
        # La clasificación se habilitará cuando se seleccione un archivo

    def select_cv_file(self):
        """Selecciona un archivo CV para clasificar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar CV para clasificar",
            "",
            "Archivos CV (*.pdf *.docx *.doc *.jpg *.jpeg *.png *.bmp *.tiff);;Todos los archivos (*)"
        )

        if file_path:
            if self.processor.is_supported_file(file_path):
                self.selected_cv_file = file_path
                self.selected_file_label.setText(os.path.basename(file_path))
                self.selected_file_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.btn_classify.setEnabled(self.classifier.is_trained)
            else:
                QMessageBox.warning(self, "Formato no soportado",
                                  "El archivo seleccionado no tiene un formato soportado")

    def classify_cv(self):
        """Clasifica el CV seleccionado"""
        if not self.classifier.is_trained:
            QMessageBox.warning(self, "Modelo no cargado", "Primero entrena o carga un modelo")
            return

        if not hasattr(self, 'selected_cv_file'):
            QMessageBox.warning(self, "Archivo no seleccionado", "Selecciona un archivo CV primero")
            return

        try:
            # Extraer texto del CV
            self.main_result.setText("🔄 Procesando CV...")
            QApplication.processEvents()  # Actualizar UI

            raw_text = self.processor.extract_text_from_file(self.selected_cv_file)
            clean_text = self.processor.clean_text(raw_text)

            if not clean_text:
                QMessageBox.warning(self, "Error", "No se pudo extraer texto del CV")
                return

            # Clasificar
            self.main_result.setText("🤖 Clasificando...")
            QApplication.processEvents()

            result = self.classifier.predict_cv(clean_text)

            if result['error']:
                QMessageBox.critical(self, "Error", f"Error en la clasificación:\n{result['message']}")
                return

            # Mostrar resultado principal
            main_text = f"""
            <h2>🎯 Resultado de la Clasificación</h2>

            <p><b>Archivo:</b> {os.path.basename(self.selected_cv_file)}</p>

            <h3>📊 Profesión Recomendada:</h3>
            <p style="font-size: 18px; color: #27ae60; font-weight: bold;">
            {result['predicted_profession']}
            </p>

            <p><b>Confianza:</b> {result['confidence_percentage']} ({result['confidence_level']})</p>

            <h3>📝 Interpretación:</h3>
            """

            if result['confidence'] > 0.8:
                main_text += "<p style='color: #27ae60;'>✅ <b>Alta confianza:</b> El CV coincide muy bien con esta profesión.</p>"
            elif result['confidence'] > 0.6:
                main_text += "<p style='color: #f39c12;'>⚠️ <b>Confianza media:</b> El CV tiene características de esta profesión, pero también podría encajar en otras.</p>"
            else:
                main_text += "<p style='color: #e74c3c;'>❓ <b>Baja confianza:</b> El CV no coincide claramente con ninguna profesión específica.</p>"

            self.main_result.setHtml(main_text)

            # Mostrar ranking en tabla
            self.ranking_table.setRowCount(len(result['profession_ranking']))
            for i, prof_data in enumerate(result['profession_ranking']):
                self.ranking_table.setItem(i, 0, QTableWidgetItem(prof_data['profession']))
                self.ranking_table.setItem(i, 1, QTableWidgetItem(prof_data['percentage']))

                # Resaltar la profesión seleccionada
                if prof_data['profession'] == result['predicted_profession']:
                    for j in range(2):
                        item = self.ranking_table.item(i, j)
                        item.setBackground(QColor(144, 238, 144))  # Light green color

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante la clasificación:\n{str(e)}")
            self.main_result.setText("❌ Error en la clasificación")

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("Clasificador de CVs por Profesiones v2.0")

    # Configurar fuente
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Crear y mostrar ventana principal
    window = CVClassifierGUI()
    window.show()

    # Mostrar mensaje de bienvenida
    QTimer.singleShot(500, lambda: show_welcome_message(window))

    return app.exec()

def show_welcome_message(parent):
    """Muestra mensaje de bienvenida"""
    message = """
    🎯 ¡Bienvenido al Clasificador de CVs por Profesiones v2.0!

    Esta versión simplificada te permite:

    🎓 Entrenar modelos por profesión:
    • Organiza CVs en carpetas por profesión
    • Agrega cada profesión y su carpeta
    • Entrena el modelo automáticamente

    🔍 Clasificar nuevos CVs:
    • Selecciona cualquier CV
    • Obtén la profesión más adecuada
    • Ve el ranking de todas las profesiones

    💡 Consejos:
    • Usa al menos 5-10 CVs por profesión para mejores resultados
    • Incluye profesiones variadas (ej: Agrónomo, Ingeniero, Marketing)
    • El modelo mejora con más datos de entrenamiento

    ¡Comienza entrenando tu primer modelo! 🚀
    """

    QMessageBox.information(parent, "¡Bienvenido!", message)

if __name__ == "__main__":
    sys.exit(main())
