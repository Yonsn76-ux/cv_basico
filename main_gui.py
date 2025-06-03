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

    def __init__(self, profession_folders, model_type, model_name):
        super().__init__()
        self.profession_folders = profession_folders
        self.model_type = model_type
        self.model_name = model_name
    
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
            
            # Guardar modelo con el nombre especificado
            self.progress_updated.emit(f"💾 Guardando modelo '{self.model_name}'...")
            classifier.save_model(self.model_name)

            self.training_completed.emit(True, results, f"¡Entrenamiento completado exitosamente!\nModelo '{self.model_name}' guardado.")
            
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

        # Inicializar listas de modelos
        self.refresh_models_list()
        self.refresh_model_selector()
    
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

        # Pestaña 2: Gestión de Modelos
        models_tab = QWidget()
        self.create_models_tab(models_tab)
        tabs.addTab(models_tab, "📚 Mis Modelos")

        # Pestaña 3: Clasificación
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
        config_layout = QVBoxLayout(config_group)

        # Primera fila: Nombre del modelo
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nombre del modelo:"))
        self.training_model_name_input = QLineEdit()
        self.training_model_name_input.setPlaceholderText("Ej: modelo_agricultura_2024")
        name_layout.addWidget(self.training_model_name_input)
        config_layout.addLayout(name_layout)

        # Segunda fila: Tipo de modelo y botón
        options_layout = QHBoxLayout()

        # Tipo de modelo
        options_layout.addWidget(QLabel("Tipo de algoritmo:"))
        self.model_type_combo = QComboBox()

        # Agregar algoritmos con nombres amigables
        algorithms = [
            ("random_forest", "Random Forest (Recomendado)"),
            ("logistic_regression", "Logistic Regression"),
            ("svm", "Support Vector Machine (SVM)"),
            ("naive_bayes", "Naive Bayes")
        ]

        for value, display_name in algorithms:
            self.model_type_combo.addItem(display_name, value)

        self.model_type_combo.setCurrentIndex(0)  # Random Forest por defecto

        # Agregar tooltips para explicar cada algoritmo
        self.model_type_combo.setToolTip(
            "🌲 Random Forest: Robusto y preciso, funciona bien con pocos datos (RECOMENDADO)\n"
            "📈 Logistic Regression: Rápido y simple, bueno para datasets pequeños\n"
            "🎯 SVM: Excelente para datos complejos, puede ser lento con muchos datos\n"
            "⚡ Naive Bayes: Muy rápido, especialmente bueno para clasificación de textos"
        )

        options_layout.addWidget(self.model_type_combo)

        options_layout.addStretch()

        # Botón de entrenamiento
        self.btn_train = QPushButton("🚀 Entrenar y Guardar Modelo")
        self.btn_train.clicked.connect(self.start_training)
        self.btn_train.setEnabled(False)
        self.btn_train.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
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
        options_layout.addWidget(self.btn_train)

        config_layout.addLayout(options_layout)
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

    def create_models_tab(self, tab):
        """Crea la pestaña de gestión de modelos"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Instrucciones
        instructions = QLabel("""
        <b>📚 Gestión de Modelos Entrenados:</b><br>
        Aquí puedes ver, cargar, renombrar y eliminar tus modelos entrenados.<br>
        Cada modelo puede tener diferentes profesiones y características.
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #f0f8ff;
                border: 1px solid #b0d4f1;
                border-radius: 5px;
                padding: 15px;
                color: #1e3a8a;
            }
        """)
        layout.addWidget(instructions)

        # Sección de guardado de modelo actual
        self.create_save_model_section(layout)

        # Lista de modelos disponibles
        self.create_models_list_section(layout)

        # Acciones de modelos
        self.create_model_actions_section(layout)

    def create_save_model_section(self, layout):
        """Crea la sección para guardar el modelo actual"""
        save_group = QGroupBox("💾 Guardar Modelo Actual")
        save_layout = QVBoxLayout(save_group)

        # Input para nombre del modelo
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nombre del modelo:"))

        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("Ej: modelo_agricultura_2024")
        name_layout.addWidget(self.model_name_input)

        self.btn_save_current_model = QPushButton("💾 Guardar Modelo")
        self.btn_save_current_model.clicked.connect(self.save_current_model)
        self.btn_save_current_model.setEnabled(False)
        self.btn_save_current_model.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        name_layout.addWidget(self.btn_save_current_model)

        save_layout.addLayout(name_layout)

        # Estado del modelo actual
        self.current_model_status = QLabel("❌ No hay modelo entrenado para guardar")
        self.current_model_status.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
        save_layout.addWidget(self.current_model_status)

        layout.addWidget(save_group)

    def create_models_list_section(self, layout):
        """Crea la sección de lista de modelos"""
        list_group = QGroupBox("📋 Modelos Disponibles")
        list_layout = QVBoxLayout(list_group)

        # Botón para refrescar lista
        refresh_layout = QHBoxLayout()
        self.btn_refresh_models = QPushButton("🔄 Actualizar Lista")
        self.btn_refresh_models.clicked.connect(self.refresh_models_list)
        refresh_layout.addWidget(self.btn_refresh_models)
        refresh_layout.addStretch()
        list_layout.addLayout(refresh_layout)

        # Tabla de modelos
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(5)
        self.models_table.setHorizontalHeaderLabels([
            "Nombre", "Tipo", "Profesiones", "Fecha", "Estado"
        ])

        # Configurar tabla
        header = self.models_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.models_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.models_table.setAlternatingRowColors(True)

        list_layout.addWidget(self.models_table)
        layout.addWidget(list_group)

    def create_model_actions_section(self, layout):
        """Crea la sección de acciones de modelos"""
        actions_group = QGroupBox("⚡ Acciones")
        actions_layout = QHBoxLayout(actions_group)

        self.btn_load_model = QPushButton("📂 Cargar Modelo")
        self.btn_load_model.clicked.connect(self.load_selected_model)
        self.btn_load_model.setEnabled(False)
        self.btn_load_model.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)

        self.btn_delete_model = QPushButton("🗑️ Eliminar Modelo")
        self.btn_delete_model.clicked.connect(self.delete_selected_model)
        self.btn_delete_model.setEnabled(False)
        self.btn_delete_model.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)

        self.btn_view_model_details = QPushButton("ℹ️ Ver Detalles")
        self.btn_view_model_details.clicked.connect(self.view_model_details)
        self.btn_view_model_details.setEnabled(False)

        actions_layout.addWidget(self.btn_load_model)
        actions_layout.addWidget(self.btn_view_model_details)
        actions_layout.addWidget(self.btn_delete_model)
        actions_layout.addStretch()

        # Conectar selección de tabla con botones
        self.models_table.selectionModel().selectionChanged.connect(self.on_model_selection_changed)

        layout.addWidget(actions_group)

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
        status_group = QGroupBox("🤖 Seleccionar y Cargar Modelo")
        status_layout = QVBoxLayout(status_group)

        # Selector de modelo
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Modelo a usar:"))

        self.model_selector_combo = QComboBox()
        self.model_selector_combo.setMinimumWidth(200)
        self.model_selector_combo.currentTextChanged.connect(self.on_model_selector_changed)
        selector_layout.addWidget(self.model_selector_combo)

        self.btn_load_selected_model = QPushButton("📂 Cargar Modelo")
        self.btn_load_selected_model.clicked.connect(self.load_model_from_selector)
        self.btn_load_selected_model.setEnabled(False)
        self.btn_load_selected_model.setStyleSheet("""
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
        """)
        selector_layout.addWidget(self.btn_load_selected_model)

        self.btn_refresh_selector = QPushButton("🔄")
        self.btn_refresh_selector.clicked.connect(self.refresh_model_selector)
        self.btn_refresh_selector.setToolTip("Actualizar lista de modelos")
        selector_layout.addWidget(self.btn_refresh_selector)

        status_layout.addLayout(selector_layout)

        # Estado actual del modelo
        self.model_status_label = QLabel("❌ Ningún modelo cargado")
        self.model_status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.model_status_label.setStyleSheet("color: #e74c3c; padding: 10px;")
        status_layout.addWidget(self.model_status_label)

        # Información del modelo
        self.model_info_text = QTextEdit()
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(100)
        self.model_info_text.setPlaceholderText("La información del modelo aparecerá aquí...")
        status_layout.addWidget(self.model_info_text)

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

        # Validar nombre del modelo
        model_name = self.training_model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Nombre requerido",
                              "Ingresa un nombre para el modelo antes de entrenar")
            return

        # Validar formato del nombre
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre inválido",
                              "El nombre solo puede contener letras, números, guiones y guiones bajos")
            return

        # Verificar si ya existe
        existing_models = self.classifier.list_available_models()
        if any(model['name'] == model_name for model in existing_models):
            reply = QMessageBox.question(self, 'Modelo existente',
                                       f'Ya existe un modelo con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Confirmar entrenamiento
        reply = QMessageBox.question(self, 'Confirmar entrenamiento',
                                   f'¿Entrenar modelo "{model_name}" con {len(self.profession_folders)} profesiones?\n'
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
        # Mapear desde el texto mostrado para asegurar compatibilidad
        text = self.model_type_combo.currentText()
        model_type_map = {
            "Random Forest (Recomendado)": "random_forest",
            "Logistic Regression": "logistic_regression",
            "Support Vector Machine (SVM)": "svm",
            "Naive Bayes": "naive_bayes"
        }
        model_type = model_type_map.get(text, "random_forest")

        print(f"Texto seleccionado: '{text}'")  # Debug
        print(f"Algoritmo mapeado: '{model_type}'")  # Debug

        self.training_thread = TrainingThread(self.profession_folders, model_type, model_name)
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

            # Actualizar listas de modelos
            self.refresh_models_list()
            self.refresh_model_selector()

            # Cargar el modelo recién entrenado
            model_name = self.training_model_name_input.text().strip()
            if model_name:
                try:
                    self.classifier.load_model(model_name)
                    self.current_loaded_model = model_name
                    self.update_model_status_ui()
                except:
                    pass  # Si no se puede cargar, no es crítico

            # Limpiar campo de nombre
            self.training_model_name_input.clear()

        else:
            self.update_training_log(f"❌ Error: {message}")
            QMessageBox.critical(self, "Error en entrenamiento", f"El entrenamiento falló:\n{message}")

    def update_save_model_ui(self):
        """Actualiza la UI para guardar modelo"""
        if self.classifier.is_trained:
            self.current_model_status.setText("✅ Modelo entrenado listo para guardar")
            self.current_model_status.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
            self.btn_save_current_model.setEnabled(True)
        else:
            self.current_model_status.setText("❌ No hay modelo entrenado para guardar")
            self.current_model_status.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
            self.btn_save_current_model.setEnabled(False)

    def save_current_model(self):
        """Guarda el modelo actual con el nombre especificado"""
        if not self.classifier.is_trained:
            QMessageBox.warning(self, "Sin modelo", "No hay modelo entrenado para guardar")
            return

        model_name = self.model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Nombre requerido", "Ingresa un nombre para el modelo")
            return

        # Validar nombre del modelo
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre inválido",
                              "El nombre solo puede contener letras, números, guiones y guiones bajos")
            return

        # Verificar si ya existe
        existing_models = self.classifier.list_available_models()
        if any(model['name'] == model_name for model in existing_models):
            reply = QMessageBox.question(self, 'Modelo existente',
                                       f'Ya existe un modelo con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            success = self.classifier.save_model(model_name)
            if success:
                QMessageBox.information(self, "Modelo guardado",
                                      f"El modelo '{model_name}' se guardó exitosamente")
                self.model_name_input.clear()
                self.refresh_models_list()
            else:
                QMessageBox.critical(self, "Error", "Error al guardar el modelo")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando modelo:\n{str(e)}")

    def refresh_models_list(self):
        """Actualiza la lista de modelos disponibles"""
        try:
            models = self.classifier.list_available_models()

            self.models_table.setRowCount(len(models))

            for i, model in enumerate(models):
                # Nombre
                self.models_table.setItem(i, 0, QTableWidgetItem(model['display_name']))

                # Tipo
                self.models_table.setItem(i, 1, QTableWidgetItem(model['model_type']))

                # Profesiones
                professions_text = ', '.join(model['professions'][:3])  # Mostrar solo las primeras 3
                if len(model['professions']) > 3:
                    professions_text += f" (+{len(model['professions'])-3} más)"
                self.models_table.setItem(i, 2, QTableWidgetItem(professions_text))

                # Fecha
                self.models_table.setItem(i, 3, QTableWidgetItem(model['creation_date']))

                # Estado
                status = "🔄 Cargado" if (self.classifier.is_trained and
                                        hasattr(self, 'current_loaded_model') and
                                        self.current_loaded_model == model['name']) else "💤 Disponible"
                self.models_table.setItem(i, 4, QTableWidgetItem(status))

                # Guardar nombre del modelo en la fila para referencia
                self.models_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, model['name'])

            print(f"Lista actualizada: {len(models)} modelos encontrados")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando lista de modelos:\n{str(e)}")

    def on_model_selection_changed(self):
        """Maneja el cambio de selección en la tabla de modelos"""
        selected_rows = self.models_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0

        self.btn_load_model.setEnabled(has_selection)
        self.btn_delete_model.setEnabled(has_selection)
        self.btn_view_model_details.setEnabled(has_selection)

    def get_selected_model_name(self):
        """Obtiene el nombre del modelo seleccionado"""
        selected_rows = self.models_table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.models_table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def load_selected_model(self):
        """Carga el modelo seleccionado"""
        model_name = self.get_selected_model_name()
        if not model_name:
            QMessageBox.warning(self, "Sin selección", "Selecciona un modelo para cargar")
            return

        try:
            success = self.classifier.load_model(model_name)
            if success:
                self.current_loaded_model = model_name
                QMessageBox.information(self, "Modelo cargado",
                                      f"El modelo '{model_name}' se cargó exitosamente")
                self.refresh_models_list()
                self.load_model_if_exists()  # Actualizar UI de clasificación
            else:
                QMessageBox.critical(self, "Error", f"Error al cargar el modelo '{model_name}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando modelo:\n{str(e)}")

    def delete_selected_model(self):
        """Elimina el modelo seleccionado"""
        model_name = self.get_selected_model_name()
        if not model_name:
            QMessageBox.warning(self, "Sin selección", "Selecciona un modelo para eliminar")
            return

        reply = QMessageBox.question(self, 'Confirmar eliminación',
                                   f'¿Estás seguro de que quieres eliminar el modelo "{model_name}"?\n'
                                   'Esta acción no se puede deshacer.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.classifier.delete_model(model_name)
                if success:
                    QMessageBox.information(self, "Modelo eliminado",
                                          f"El modelo '{model_name}' se eliminó exitosamente")
                    self.refresh_models_list()

                    # Si era el modelo cargado, limpiar estado
                    if (hasattr(self, 'current_loaded_model') and
                        self.current_loaded_model == model_name):
                        self.current_loaded_model = None
                        self.load_model_if_exists()
                else:
                    QMessageBox.critical(self, "Error", f"Error al eliminar el modelo '{model_name}'")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando modelo:\n{str(e)}")

    def view_model_details(self):
        """Muestra los detalles del modelo seleccionado"""
        model_name = self.get_selected_model_name()
        if not model_name:
            QMessageBox.warning(self, "Sin selección", "Selecciona un modelo para ver detalles")
            return

        try:
            models = self.classifier.list_available_models()
            model_data = next((m for m in models if m['name'] == model_name), None)

            if not model_data:
                QMessageBox.warning(self, "Error", "No se encontraron detalles del modelo")
                return

            details_text = f"""
            <h2>📊 Detalles del Modelo: {model_data['display_name']}</h2>

            <p><b>Nombre:</b> {model_data['name']}</p>
            <p><b>Tipo de algoritmo:</b> {model_data['model_type']}</p>
            <p><b>Fecha de creación:</b> {model_data['creation_date']}</p>
            <p><b>Número de características:</b> {model_data['num_features']:,}</p>

            <h3>🎯 Profesiones ({model_data['num_professions']}):</h3>
            <ul>
            """

            for profession in model_data['professions']:
                details_text += f"<li>{profession}</li>"

            details_text += """
            </ul>

            <p><i>Este modelo puede clasificar CVs en las profesiones listadas arriba.</i></p>
            """

            msg = QMessageBox()
            msg.setWindowTitle(f"Detalles - {model_data['display_name']}")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText(details_text)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error obteniendo detalles:\n{str(e)}")

    def refresh_model_selector(self):
        """Actualiza el selector de modelos en la pestaña de clasificación"""
        try:
            models = self.classifier.list_available_models()

            # Limpiar selector
            self.model_selector_combo.clear()

            if not models:
                self.model_selector_combo.addItem("No hay modelos disponibles")
                self.btn_load_selected_model.setEnabled(False)
                return

            # Agregar modelos al selector
            for model in models:
                display_text = f"{model['display_name']} ({len(model['professions'])} profesiones)"
                self.model_selector_combo.addItem(display_text, model['name'])

            # Habilitar botón si hay modelos
            self.btn_load_selected_model.setEnabled(len(models) > 0)

            # Si hay un modelo cargado actualmente, seleccionarlo
            if hasattr(self, 'current_loaded_model') and self.current_loaded_model:
                for i in range(self.model_selector_combo.count()):
                    if self.model_selector_combo.itemData(i) == self.current_loaded_model:
                        self.model_selector_combo.setCurrentIndex(i)
                        break

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando selector de modelos:\n{str(e)}")

    def on_model_selector_changed(self):
        """Maneja el cambio en el selector de modelos"""
        current_data = self.model_selector_combo.currentData()
        self.btn_load_selected_model.setEnabled(current_data is not None)

    def load_model_from_selector(self):
        """Carga el modelo seleccionado en el selector"""
        model_name = self.model_selector_combo.currentData()
        if not model_name:
            QMessageBox.warning(self, "Sin selección", "No hay modelo seleccionado")
            return

        try:
            success = self.classifier.load_model(model_name)
            if success:
                self.current_loaded_model = model_name
                self.update_model_status_ui()
                QMessageBox.information(self, "Modelo cargado",
                                      f"El modelo '{model_name}' se cargó exitosamente")
            else:
                QMessageBox.critical(self, "Error", f"Error al cargar el modelo '{model_name}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando modelo:\n{str(e)}")

    def update_model_status_ui(self):
        """Actualiza la UI del estado del modelo en clasificación"""
        if self.classifier.is_trained:
            model_name = getattr(self, 'current_loaded_model', 'Desconocido')
            self.model_status_label.setText(f"✅ Modelo '{model_name}' cargado")
            self.model_status_label.setStyleSheet("color: #27ae60; padding: 10px; font-weight: bold;")

            # Mostrar información del modelo
            info = self.classifier.get_model_info()
            if info:
                info_text = f"""
                <b>Modelo Activo:</b> {model_name}<br>
                <b>Tipo:</b> {info['model_type']}<br>
                <b>Profesiones:</b> {info['num_professions']}<br>
                <b>Lista:</b> {', '.join(info['professions'])}<br>
                <b>Características:</b> {info['num_features']:,}
                """
                self.model_info_text.setHtml(info_text)
        else:
            self.model_status_label.setText("❌ Ningún modelo cargado")
            self.model_status_label.setStyleSheet("color: #e74c3c; padding: 10px; font-weight: bold;")
            self.model_info_text.clear()

    def load_model_if_exists(self):
        """Carga el modelo si existe y actualiza la UI"""
        try:
            # Intentar cargar el modelo por defecto
            success = self.classifier.load_model()
            if success:
                self.current_loaded_model = 'cv_classifier'  # Nombre por defecto
                self.update_model_status_ui()
                self.update_classification_ui()
            else:
                self.update_model_status_ui()

            # Actualizar selector de modelos
            self.refresh_model_selector()

        except Exception as e:
            print(f"Error cargando modelo: {e}")
            self.update_model_status_ui()

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
