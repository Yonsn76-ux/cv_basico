# -*- coding: utf-8 -*-
"""
Interfaz gráfica principal para el Clasificador de CVs por Profesiones
Versión con diseño inspirado en Bulma.
"""

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTextEdit,
                             QGroupBox, QGridLayout, QFileDialog, QMessageBox,
                             QTabWidget, QListWidget, QComboBox, QProgressBar,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QSplitter, QLineEdit, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from PyQt6.QtGui import QFont, QTextCursor, QColor

# Asegurar que el path a src sea correcto para los imports locales
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.cv_processor import CVProcessor
from src.models.cv_classifier import CVClassifier
from src.config.settings import Settings

# Importar Deep Learning Classifier (opcional)
try:
    from src.models.deep_learning_classifier import DeepLearningClassifier
    DEEP_LEARNING_AVAILABLE = True
    print("✅ Deep Learning disponible")
except ImportError as e:
    DEEP_LEARNING_AVAILABLE = False
    print(f"⚠️ Deep Learning no disponible: {e}")
    print("    Para usar Deep Learning, instala: pip install tensorflow transformers")

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
            
            self.progress_updated.emit("🤖 Entrenando modelo de clasificación...")
            classifier = CVClassifier()
            
            results = classifier.train_model(all_cv_data, model_type=self.model_type)
            
            self.progress_updated.emit(f"💾 Guardando modelo '{self.model_name}'...")
            classifier.save_model(self.model_name)

            self.training_completed.emit(True, results, f"¡Entrenamiento completado exitosamente!\nModelo '{self.model_name}' guardado.")
            
        except Exception as e:
            self.training_completed.emit(False, {}, f"Error durante el entrenamiento: {str(e)}")

class DeepLearningTrainingThread(QThread):
    """Hilo para entrenamiento de Deep Learning en segundo plano"""
    progress_updated = pyqtSignal(str)
    training_completed = pyqtSignal(bool, dict, str)

    def __init__(self, profession_folders, model_type, model_name, epochs, batch_size):
        super().__init__()
        self.profession_folders = profession_folders
        self.model_type = model_type
        self.model_name = model_name
        self.epochs = epochs
        self.batch_size = batch_size

    def run(self):
        try:
            if not DEEP_LEARNING_AVAILABLE:
                self.training_completed.emit(False, {}, "Deep Learning no está disponible")
                return

            self.progress_updated.emit("🔄 Iniciando procesamiento de CVs para Deep Learning...")

            from src.utils.cv_processor import CVProcessor # Import local para el hilo
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

            self.progress_updated.emit(f"🧠 Entrenando modelo {self.model_type.upper()}...")
            dl_classifier = DeepLearningClassifier()

            results = dl_classifier.train_model(
                all_cv_data,
                model_type=self.model_type,
                epochs=self.epochs,
                batch_size=self.batch_size
            )

            if not results.get('success', False): 
                self.training_completed.emit(False, {}, results.get('error', 'Error desconocido durante el entrenamiento DL.'))
                return

            self.progress_updated.emit(f"💾 Guardando modelo Deep Learning '{self.model_name}'...")
            dl_classifier.save_model(self.model_name)

            accuracy_str = f"{results.get('accuracy', 0):.1%}" if results.get('accuracy') is not None else "N/A"
            epochs_trained_str = str(results.get('epochs_trained', 'N/A'))
            
            message = (f"¡Entrenamiento Deep Learning completado!\n"
                       f"Modelo '{self.model_name}' guardado.\n"
                       f"Precisión: {accuracy_str}\n"
                       f"Épocas: {epochs_trained_str}")
            self.training_completed.emit(True, results, message)

        except Exception as e:
            self.training_completed.emit(False, {}, f"Error durante el entrenamiento Deep Learning: {str(e)}")


class CVClassifierGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = CVProcessor()
        self.classifier = CVClassifier()
        if DEEP_LEARNING_AVAILABLE:
            self.dl_classifier = DeepLearningClassifier()
        else:
            self.dl_classifier = None

        self.profession_folders = {}
        self.dl_profession_folders = {} 
        self.training_thread = None
        self.dl_training_thread = None 

        self.current_loaded_model = None
        self.current_model_is_dl = False
        
        self.init_ui()
        self.load_model_if_exists() 

        self.refresh_models_list()
        self.refresh_model_selector()
        self.update_save_model_ui() 
        self.update_classification_ui() 

    def get_modern_stylesheet(self):
        # Paleta de colores inspirada en Bulma
        BULMA_PRIMARY = "#485fc7"      # Azul fuerte (Bulma 'link')
        BULMA_PRIMARY_HOVER = "#3a52a3" # Más oscuro
        BULMA_SUCCESS = "#48c78e"      # Verde (Bulma 'success')
        BULMA_SUCCESS_HOVER = "#3aac7a"
        BULMA_DANGER = "#f14668"       # Rojo (Bulma 'danger')
        BULMA_DANGER_HOVER = "#e93459"
        BULMA_WARNING = "#ffdd57"      # Amarillo (Bulma 'warning')
        BULMA_WARNING_TEXT = "#363636" # Texto oscuro para fondo amarillo
        BULMA_INFO = "#3e8ed0"         # Azul claro (Bulma 'info')
        BULMA_INFO_HOVER = "#307bbd"

        BULMA_LIGHT_GREY = "#f5f5f5"   # Gris muy claro (Bulma 'light')
        BULMA_BORDER = "#dbdbdb"       # Gris para bordes (Bulma 'border')
        BULMA_TEXT_COLOR = "#4a4a4a"   # Color de texto principal
        BULMA_TEXT_LIGHT = "#ffffff"   # Texto blanco para fondos oscuros
        BULMA_BACKGROUND = "#ffffff"   # Fondo general de widgets como GroupBox
        BULMA_INPUT_BG = "#ffffff"
        BULMA_DISABLED_BG = "#f0f0f0"
        BULMA_DISABLED_TEXT = "#ababab"
        
        CONSOLE_BG_COLOR = "#2b2b2b"
        CONSOLE_TEXT_COLOR = "#e0e0e0"

        # Colores para mensajes tipo Bulma
        MESSAGE_PRIMARY_BG = "#ebf1fe" 
        MESSAGE_PRIMARY_BORDER = BULMA_PRIMARY
        MESSAGE_PRIMARY_TEXT = "#2f4687"

        MESSAGE_INFO_BG = "#eef6fc" 
        MESSAGE_INFO_BORDER = BULMA_INFO
        MESSAGE_INFO_TEXT = "#1d5f91"

        MESSAGE_WARNING_BG = "#fffbeb"
        MESSAGE_WARNING_BORDER = BULMA_WARNING 
        MESSAGE_WARNING_TEXT_COLOR = BULMA_WARNING_TEXT

        # Hoja de estilos QSS con inspiración Bulma
        return f"""
            QMainWindow {{
                background-color: {BULMA_LIGHT_GREY}; /* Fondo principal de la ventana */
            }}
            QWidget {{
                color: {BULMA_TEXT_COLOR};
                font-family: "Segoe UI", Arial, sans-serif; /* Fuente limpia */
                font-size: 10pt;
            }}
            QScrollArea {{
                border: none;
            }}

            QTabWidget::pane {{
                border-top: 1px solid {BULMA_BORDER};
                background-color: {BULMA_LIGHT_GREY};
            }}
            QTabBar::tab {{
                background: transparent; /* Pestañas más integradas */
                border: none;
                border-bottom: 2px solid transparent; /* Borde inferior sutil */
                padding: 10px 18px;
                margin-right: 1px;
                color: {BULMA_TEXT_COLOR};
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: transparent;
                color: {BULMA_PRIMARY};
                border-bottom: 2px solid {BULMA_PRIMARY}; /* Borde inferior acentuado */
            }}
            QTabBar::tab:!selected:hover {{
                background: transparent;
                color: {BULMA_PRIMARY};
                border-bottom: 2px solid #e0e0e0; /* Borde sutil en hover */
            }}

            QGroupBox {{
                background-color: {BULMA_BACKGROUND}; /* Fondo blanco como "box" de Bulma */
                border: 1px solid {BULMA_BORDER};
                border-radius: 6px; /* Bordes redondeados de Bulma */
                margin-top: 12px;  
                padding: 20px 15px 15px 15px; /* Padding interno */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                left: 10px;
                top: -2px; 
                color: {BULMA_PRIMARY};
                background-color: {BULMA_BACKGROUND}; /* Fondo del título igual al GroupBox */
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }}

            /* Estilo base para QPushButton - similar a Bulma default */
            QPushButton {{
                background-color: #f5f5f5; /* Botón default de Bulma */
                color: #363636;
                border: 1px solid {BULMA_BORDER};
                border-radius: 4px; /* Radio de Bulma */
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: #b5b5b5;
                background-color: #e8e8e8;
            }}
            QPushButton:pressed {{
                background-color: #dddddd;
                border-color: #a0a0a0;
            }}
            QPushButton:disabled {{
                background-color: {BULMA_DISABLED_BG};
                color: {BULMA_DISABLED_TEXT};
                border-color: #e0e0e0;
            }}

            /* Botones de acción primaria (Azul - 'is-link' o 'is-primary' de Bulma) */
            QPushButton#btn_classify, QPushButton#btn_save_current_model, 
            QPushButton#btn_load_selected_model, QPushButton#btn_load_model,
            QPushButton#btn_add_profession, QPushButton#btn_dl_add_profession {{
                background-color: {BULMA_PRIMARY};
                color: {BULMA_TEXT_LIGHT};
                border: 1px solid {BULMA_PRIMARY};
                padding: 9px 18px; /* Ligeramente más grandes */
            }}
            QPushButton#btn_classify:hover, QPushButton#btn_save_current_model:hover,
            QPushButton#btn_load_selected_model:hover, QPushButton#btn_load_model:hover,
            QPushButton#btn_add_profession:hover, QPushButton#btn_dl_add_profession:hover {{
                background-color: {BULMA_PRIMARY_HOVER};
                border-color: {BULMA_PRIMARY_HOVER};
            }}
            
            /* Botones de entrenamiento (Verde - 'is-success' de Bulma) */
            QPushButton#btn_train, QPushButton#btn_dl_train {{
                background-color: {BULMA_SUCCESS};
                color: {BULMA_TEXT_LIGHT};
                border: 1px solid {BULMA_SUCCESS};
                padding: 9px 18px;
            }}
            QPushButton#btn_train:hover, QPushButton#btn_dl_train:hover {{
                background-color: {BULMA_SUCCESS_HOVER};
                border-color: {BULMA_SUCCESS_HOVER};
            }}

            /* Botones de acción destructiva (Rojo - 'is-danger' de Bulma) */
            QPushButton#btn_delete_model {{
                background-color: {BULMA_DANGER};
                color: {BULMA_TEXT_LIGHT};
                border: 1px solid {BULMA_DANGER};
            }}
            QPushButton#btn_delete_model:hover {{
                background-color: {BULMA_DANGER_HOVER};
                border-color: {BULMA_DANGER_HOVER};
            }}

            QLineEdit, QComboBox, QTextEdit {{
                border: 1px solid {BULMA_BORDER};
                border-radius: 4px;
                padding: 7px 10px; /* Padding de inputs de Bulma */
                background-color: {BULMA_INPUT_BG};
                min-height: 20px; /* Para que QComboBox y QLineEdit tengan altura similar */
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border-color: {BULMA_PRIMARY}; 
                /* QSS no tiene box-shadow directo como CSS, el cambio de borde es la principal indicación */
            }}
             QComboBox::item:selected {{
                background-color: {BULMA_PRIMARY};
                color: {BULMA_TEXT_LIGHT};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: {BULMA_BORDER};
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QComboBox::down-arrow {{
                /* Qt usualmente provee una flecha por defecto, se puede personalizar con image: url(...) */
            }}

            QTextEdit#training_log, QTextEdit#dl_training_log {{
                background-color: {CONSOLE_BG_COLOR};
                color: {CONSOLE_TEXT_COLOR};
                font-family: "Consolas", "Courier New", monospace;
                font-size: 9pt;
                border-radius: 4px;
            }}
            QTextEdit#model_info_text, QTextEdit#main_result {{
                background-color: #fafafa; /* Fondo ligeramente diferente para áreas de info */
                border-radius: 4px;
            }}

            QListWidget {{
                border: 1px solid {BULMA_BORDER};
                border-radius: 4px;
                background-color: {BULMA_INPUT_BG};
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 3px;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{
                background-color: {BULMA_PRIMARY};
                color: {BULMA_TEXT_LIGHT};
                border: none; /* Sin borde extra en selección */
            }}
            QListWidget::item:hover:!selected {{ /* Hover solo si no está seleccionado */
                background-color: {BULMA_LIGHT_GREY};
                color: {BULMA_TEXT_COLOR};
            }}

            QTableWidget {{
                border: 1px solid {BULMA_BORDER};
                border-radius: 4px;
                gridline-color: #e8e8e8; 
                background-color: {BULMA_INPUT_BG};
                selection-background-color: {BULMA_PRIMARY};
                selection-color: {BULMA_TEXT_LIGHT};
                alternate-background-color: {BULMA_LIGHT_GREY};
            }}
            QHeaderView::section {{
                background-color: {BULMA_LIGHT_GREY}; /* Cabeceras más claras */
                padding: 8px;
                border: none; /* Sin bordes internos en cabecera */
                border-bottom: 1px solid {BULMA_BORDER}; /* Línea inferior */
                font-weight: bold;
                font-size: 9.5pt;
            }}
            QHeaderView::section:horizontal {{
                border-right: 1px solid {BULMA_BORDER}; /* Líneas verticales entre cabeceras */
            }}
             QHeaderView::section:horizontal:last {{
                border-right: none;
            }}


            QProgressBar {{
                border: 1px solid {BULMA_BORDER};
                border-radius: 4px;
                text-align: center;
                background-color: {BULMA_INPUT_BG};
                color: {BULMA_TEXT_COLOR};
                font-weight: bold;
                height: 20px; /* Altura consistente */
            }}
            QProgressBar::chunk {{
                background-color: {BULMA_SUCCESS}; /* Color de progreso de Bulma */
                border-radius: 3px;
                margin: 1px; /* Pequeño margen para ver el borde de la barra */
            }}

            QLabel {{
                background-color: transparent;
                padding: 2px;
            }}
            QLabel#model_status_label {{
                font-size: 11pt;
                font-weight: bold;
                padding: 8px 0; 
            }}
            QLabel#selected_file_label {{
                font-weight: normal; /* No siempre en negrita, se actualiza en código */
                padding: 5px;
                border: 1px dashed transparent; /* Espacio reservado */
            }}

            /* Estilo para etiquetas de instrucciones tipo "message" de Bulma */
            .InstructionLabel {{ 
                border-radius: 4px;
                padding: 12px 15px;
                margin-bottom: 8px; 
                border-width: 1px;
                border-style: solid;
            }}
            QLabel#training_instructions {{ /* 'is-info' de Bulma */
                background-color: {MESSAGE_INFO_BG}; 
                border-color: {MESSAGE_INFO_BORDER};
                color: {MESSAGE_INFO_TEXT};
            }}
            QLabel#dl_instructions {{ /* 'is-primary' de Bulma */
                background-color: {MESSAGE_PRIMARY_BG}; 
                border-color: {MESSAGE_PRIMARY_BORDER};
                color: {MESSAGE_PRIMARY_TEXT};
            }}
            QLabel#dl_warning_label {{ /* 'is-warning' de Bulma */
                background-color: {MESSAGE_WARNING_BG}; 
                border-color: {MESSAGE_WARNING_BORDER};
                color: {MESSAGE_WARNING_TEXT_COLOR};
            }}
            QLabel#dl_note_label {{ /* Un color neutro, como un gris claro */
                background-color: #fafafa; 
                border: 1px solid #ededed;
                color: #5a5a5a; 
                font-size: 9pt;
            }}
            QLabel#models_instructions {{ /* 'is-info' suave */
                background-color: {MESSAGE_INFO_BG}; 
                border-color: {MESSAGE_INFO_BORDER};
                color: {MESSAGE_INFO_TEXT};
            }}

            /* Estilo del Header */
            QWidget#app_header {{
                background: {BULMA_PRIMARY}; /* Fondo sólido primario */
                border-radius: 0px; 
                margin-bottom: 15px; 
            }}
            QLabel#header_title {{
                color: {BULMA_TEXT_LIGHT};
                font-size: 18pt; /* Ligeramente más pequeño */
                font-weight: bold;
                background: transparent;
                padding: 3px 0;
            }}
            QLabel#header_subtitle {{
                color: rgba(255, 255, 255, 0.9); /* Más opaco */
                font-size: 10pt;
                background: transparent;
                padding: 0 0 3px 0;
            }}

            QSplitter::handle {{
                background-color: {BULMA_BORDER};
            }}
            QSplitter::handle:horizontal {{
                height: 2px; /* Más delgado */
            }}
            QSplitter::handle:vertical {{
                width: 2px; /* Más delgado */
            }}
            QSplitter::handle:hover {{
                background-color: {BULMA_PRIMARY};
            }}
        """

    def init_ui(self):
        self.setWindowTitle("🎯 Clasificador de CVs por Profesiones v2.0 (Estilo Bulma)")
        self.setMinimumSize(1000, 750)
        self.resize(1400, 900)
        self.center_window()

        self.setStyleSheet(self.get_modern_stylesheet())

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        central_widget_for_scroll = QWidget()
        scroll_area.setWidget(central_widget_for_scroll)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout(central_widget_for_scroll)
        main_layout.setSpacing(18) # Espaciado general
        main_layout.setContentsMargins(20, 20, 20, 20) # Márgenes generales

        self.create_header(main_layout)
        self.create_tabs(main_layout)
        
        if self.classifier:
            if hasattr(self.classifier, 'model_changed_signal'): 
                self.classifier.model_changed_signal.connect(self.update_save_model_ui)

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        window_rect.moveCenter(screen.center())
        self.move(window_rect.topLeft())

    def create_header(self, layout):
        header_widget = QWidget()
        header_widget.setObjectName("app_header")
        header_widget.setFixedHeight(75) # Altura del header

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(25, 10, 25, 10)

        title_vbox = QVBoxLayout()
        title = QLabel("🎯 Clasificador de CVs")
        title.setObjectName("header_title")
        
        subtitle = QLabel("v2.0 - Estilo Bulma")
        subtitle.setObjectName("header_subtitle")

        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        title_vbox.setSpacing(0)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addWidget(header_widget)

    def create_tabs(self, layout):
        tabs = QTabWidget()

        training_tab = QWidget()
        self.create_training_tab(training_tab)
        tabs.addTab(training_tab, "🎓 Entrenar Modelo")

        if DEEP_LEARNING_AVAILABLE:
            deep_learning_tab = QWidget()
            self.create_deep_learning_tab(deep_learning_tab)
            tabs.addTab(deep_learning_tab, "🧠 Deep Learning")

        models_tab = QWidget()
        self.create_models_tab(models_tab)
        tabs.addTab(models_tab, "📚 Mis Modelos")

        classification_tab = QWidget()
        self.create_classification_tab(classification_tab)
        tabs.addTab(classification_tab, "🔍 Clasificar CV")

        layout.addWidget(tabs)

    def create_training_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        instructions = QLabel("""
        <b>📋 Instrucciones para entrenar el modelo:</b><br>
        1. Organiza tus CVs en carpetas por profesión (ej: "Agrónomo", "Ingeniero")<br>
        2. Agrega cada profesión y selecciona su carpeta correspondiente<br>
        3. Elige un nombre para tu modelo y el tipo de algoritmo<br>
        4. ¡Entrena! El modelo se guardará automáticamente.
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("training_instructions") 
        instructions.setProperty("class", "InstructionLabel") 
        layout.addWidget(instructions)
        
        self.create_profession_config(layout, is_dl=False)
        self.create_training_config(layout)
        self.create_training_log(layout)

    def create_profession_config(self, layout, is_dl=False):
        group_title = "👥 Configurar Profesiones"
        if is_dl:
            group_title += " para Deep Learning"
        
        prof_group = QGroupBox(group_title)
        prof_layout = QVBoxLayout(prof_group)

        if is_dl: 
            note = QLabel("""
            <b>📝 Nota:</b> Los modelos de Deep Learning suelen requerir más datos.<br>
            Se recomienda al menos 20-50 CVs por profesión para buenos resultados.
            """)
            note.setWordWrap(True)
            note.setObjectName("dl_note_label")
            note.setProperty("class", "InstructionLabel")
            prof_layout.addWidget(note)

        add_layout = QHBoxLayout()
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nombre de la profesión (ej: Agrónomo)")
        
        btn_select_folder = QPushButton("📁 Seleccionar Carpeta")
        btn_add_profession = QPushButton("➕ Agregar Profesión")
        btn_add_profession.setObjectName("btn_add_profession" if not is_dl else "btn_dl_add_profession")
        btn_add_profession.setEnabled(False)

        add_layout.addWidget(QLabel("Profesión:"))
        add_layout.addWidget(name_input, 1) 
        add_layout.addWidget(btn_select_folder)
        add_layout.addWidget(btn_add_profession)
        prof_layout.addLayout(add_layout)
        
        list_widget = QListWidget()
        list_widget.setMaximumHeight(150) 
        prof_layout.addWidget(QLabel("Profesiones configuradas:"))
        prof_layout.addWidget(list_widget)
        
        btn_clear_professions = QPushButton("🗑️ Limpiar Lista")
        prof_layout.addWidget(btn_clear_professions, 0, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(prof_group)

        if is_dl:
            self.dl_profession_name_input = name_input
            self.btn_dl_select_folder = btn_select_folder
            self.btn_dl_add_profession = btn_add_profession
            self.dl_profession_list = list_widget
            self.btn_dl_clear_professions = btn_clear_professions
            btn_select_folder.clicked.connect(self.select_dl_profession_folder)
            btn_add_profession.clicked.connect(self.add_dl_profession)
            btn_clear_professions.clicked.connect(self.clear_dl_professions)
            name_input.textChanged.connect(lambda text: self.btn_dl_add_profession.setEnabled(bool(text.strip()) and hasattr(self, 'dl_selected_folder')))
        else:
            self.profession_name_input = name_input
            self.btn_select_folder = btn_select_folder
            self.btn_add_profession = btn_add_profession
            self.profession_list = list_widget
            self.btn_clear_professions = btn_clear_professions
            btn_select_folder.clicked.connect(self.select_profession_folder)
            btn_add_profession.clicked.connect(self.add_profession)
            btn_clear_professions.clicked.connect(self.clear_professions)
            name_input.textChanged.connect(lambda text: self.btn_add_profession.setEnabled(bool(text.strip()) and hasattr(self, 'selected_folder')))

    def create_training_config(self, layout):
        config_group = QGroupBox("⚙️ Configuración del Entrenamiento")
        config_layout = QGridLayout(config_group)

        config_layout.addWidget(QLabel("Nombre del modelo:"), 0, 0)
        self.training_model_name_input = QLineEdit()
        self.training_model_name_input.setPlaceholderText("Ej: modelo_agronomos_2024")
        config_layout.addWidget(self.training_model_name_input, 0, 1, 1, 2)

        config_layout.addWidget(QLabel("Tipo de algoritmo:"), 1, 0)
        self.model_type_combo = QComboBox()
        algorithms = [
            ("random_forest", "Random Forest (Recomendado)"),
            ("logistic_regression", "Logistic Regression"),
            ("svm", "Support Vector Machine (SVM)"),
            ("naive_bayes", "Naive Bayes")
        ]
        for value, display_name in algorithms:
            self.model_type_combo.addItem(display_name, value)
        self.model_type_combo.setCurrentIndex(0)
        self.model_type_combo.setToolTip(
             "🌲 Random Forest: Robusto y preciso (RECOMENDADO)\n"
             "📈 Logistic Regression: Rápido y simple\n"
             "🎯 SVM: Bueno para datos complejos, puede ser lento\n"
             "⚡ Naive Bayes: Muy rápido, bueno para texto"
        )
        config_layout.addWidget(self.model_type_combo, 1, 1, 1, 2)

        self.btn_train = QPushButton("🚀 Entrenar y Guardar")
        self.btn_train.setObjectName("btn_train")
        self.btn_train.clicked.connect(self.start_training)
        self.btn_train.setEnabled(False)
        config_layout.addWidget(self.btn_train, 2, 1, 1, 2, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(config_group)

    def create_training_log(self, layout):
        log_group = QGroupBox("📊 Progreso del Entrenamiento")
        log_layout = QVBoxLayout(log_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        log_layout.addWidget(self.progress_bar)
        
        self.training_log = QTextEdit()
        self.training_log.setObjectName("training_log")
        self.training_log.setReadOnly(True)
        self.training_log.setMaximumHeight(200)
        log_layout.addWidget(self.training_log)
        
        layout.addWidget(log_group)

    def create_deep_learning_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        instructions = QLabel("""
        <b>🧠 Modelos de Deep Learning:</b><br>
        Entrena modelos avanzados (LSTM, CNN, BERT) para una clasificación de CVs más profunda.<br>
        Estos modelos pueden capturar matices complejos en el texto, pero requieren más datos y tiempo de entrenamiento.
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("dl_instructions")
        instructions.setProperty("class", "InstructionLabel")
        layout.addWidget(instructions)

        if not DEEP_LEARNING_AVAILABLE:
            warning = QLabel("""
            <b>⚠️ Deep Learning no disponible</b><br>
            Para usar modelos de Deep Learning, instala las dependencias:<br>
            <code>pip install tensorflow transformers</code>
            """)
            warning.setWordWrap(True)
            warning.setObjectName("dl_warning_label")
            warning.setProperty("class", "InstructionLabel")
            layout.addWidget(warning)
            return

        self.create_profession_config(layout, is_dl=True)
        self.create_dl_training_config(layout)
        self.create_dl_training_log(layout)

    def create_dl_training_config(self, layout):
        config_group = QGroupBox("🧠 Configuración de Deep Learning")
        config_layout = QGridLayout(config_group)

        config_layout.addWidget(QLabel("Nombre del modelo:"), 0, 0)
        self.dl_model_name_input = QLineEdit()
        self.dl_model_name_input.setPlaceholderText("Ej: dl_modelo_ingenieros_bert")
        config_layout.addWidget(self.dl_model_name_input, 0, 1, 1, 3)

        config_layout.addWidget(QLabel("Tipo de modelo:"), 1, 0)
        self.dl_model_type_combo = QComboBox()
        dl_models = [
            ("lstm", "LSTM (Long Short-Term Memory)"),
            ("cnn", "CNN (Convolutional Neural Network)"),
            ("bert", "BERT (Transformer - Lento, Preciso)")
        ]
        for value, display_name in dl_models:
            self.dl_model_type_combo.addItem(display_name, value)
        self.dl_model_type_combo.setCurrentIndex(0)
        self.dl_model_type_combo.setToolTip(
            "🔄 LSTM: Bueno para secuencias de texto\n"
            "🔍 CNN: Rápido, detecta patrones locales\n"
            "🤖 BERT: Estado del arte, alta precisión, más lento"
        )
        config_layout.addWidget(self.dl_model_type_combo, 1, 1, 1, 3)

        config_layout.addWidget(QLabel("Épocas:"), 2, 0)
        self.dl_epochs_input = QLineEdit("10")
        self.dl_epochs_input.setMaximumWidth(80)
        config_layout.addWidget(self.dl_epochs_input, 2, 1)

        config_layout.addWidget(QLabel("Batch Size:"), 2, 2)
        self.dl_batch_size_input = QLineEdit("32")
        self.dl_batch_size_input.setMaximumWidth(80)
        config_layout.addWidget(self.dl_batch_size_input, 2, 3)

        self.btn_dl_train = QPushButton("🧠 Entrenar Modelo DL")
        self.btn_dl_train.setObjectName("btn_dl_train")
        self.btn_dl_train.clicked.connect(self.start_dl_training)
        self.btn_dl_train.setEnabled(False)
        config_layout.addWidget(self.btn_dl_train, 3, 1, 1, 3, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(config_group)

    def create_dl_training_log(self, layout):
        log_group = QGroupBox("📊 Progreso del Entrenamiento Deep Learning")
        log_layout = QVBoxLayout(log_group)

        self.dl_progress_bar = QProgressBar()
        self.dl_progress_bar.setVisible(False)
        log_layout.addWidget(self.dl_progress_bar)

        self.dl_training_log = QTextEdit()
        self.dl_training_log.setObjectName("dl_training_log")
        self.dl_training_log.setReadOnly(True)
        self.dl_training_log.setMaximumHeight(200)
        log_layout.addWidget(self.dl_training_log)

        layout.addWidget(log_group)

    def create_models_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        instructions = QLabel("""
        <b>📚 Gestión de Modelos Entrenados:</b><br>
        Visualiza, carga, y elimina tus modelos de Machine Learning y Deep Learning.<br>
        Selecciona un modelo de la lista para ver detalles o realizar acciones.
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("models_instructions")
        instructions.setProperty("class", "InstructionLabel")
        layout.addWidget(instructions)
        
        # self.create_save_model_section(layout) # Eliminado, el guardado es post-entrenamiento
        self.create_models_list_section(layout)
        self.create_model_actions_section(layout)

    def create_save_model_section(self, layout): 
        # Esta función se mantiene por si se decide añadir "Guardar como..." en el futuro
        save_group = QGroupBox("💾 Guardar Modelo Actual (Entrenado)")
        save_layout = QHBoxLayout(save_group)

        save_layout.addWidget(QLabel("Nombre del modelo:"))
        self.model_name_input = QLineEdit() 
        self.model_name_input.setPlaceholderText("Ej: modelo_general_v1")
        save_layout.addWidget(self.model_name_input, 1)

        self.btn_save_current_model = QPushButton("💾 Guardar Modelo")
        self.btn_save_current_model.setObjectName("btn_save_current_model")
        self.btn_save_current_model.clicked.connect(self.save_current_model)
        self.btn_save_current_model.setEnabled(False) 
        save_layout.addWidget(self.btn_save_current_model)
        
        layout.addWidget(save_group)


    def create_models_list_section(self, layout):
        list_group = QGroupBox("📋 Modelos Disponibles")
        list_layout = QVBoxLayout(list_group)

        btn_refresh_layout = QHBoxLayout()
        self.btn_refresh_models = QPushButton("🔄 Actualizar Lista")
        self.btn_refresh_models.clicked.connect(self.refresh_models_list)
        btn_refresh_layout.addWidget(self.btn_refresh_models)
        btn_refresh_layout.addStretch()
        list_layout.addLayout(btn_refresh_layout)

        self.models_table = QTableWidget()
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels([
            "Nombre", "Tipo Algoritmo", "Categoría", "Profesiones", "Fecha Creación", "Estado"
        ])
        
        header = self.models_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents) 
        
        self.models_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.models_table.setAlternatingRowColors(True)
        self.models_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.models_table.setShowGrid(True) 
        self.models_table.selectionModel().selectionChanged.connect(self.on_model_selection_changed)

        list_layout.addWidget(self.models_table)
        layout.addWidget(list_group)

    def create_model_actions_section(self, layout):
        actions_group = QGroupBox("⚡ Acciones sobre Modelo Seleccionado")
        actions_layout = QHBoxLayout(actions_group)

        self.btn_load_model = QPushButton("📂 Cargar")
        self.btn_load_model.setObjectName("btn_load_model")
        self.btn_load_model.clicked.connect(self.load_selected_model)
        self.btn_load_model.setEnabled(False)

        self.btn_view_model_details = QPushButton("ℹ️ Ver Detalles")
        self.btn_view_model_details.clicked.connect(self.view_model_details)
        self.btn_view_model_details.setEnabled(False)

        self.btn_delete_model = QPushButton("🗑️ Eliminar")
        self.btn_delete_model.setObjectName("btn_delete_model")
        self.btn_delete_model.clicked.connect(self.delete_selected_model)
        self.btn_delete_model.setEnabled(False)

        actions_layout.addWidget(self.btn_load_model)
        actions_layout.addWidget(self.btn_view_model_details)
        actions_layout.addStretch() 
        actions_layout.addWidget(self.btn_delete_model)
        
        layout.addWidget(actions_group)

    def create_classification_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        self.create_model_status(layout)
        self.create_cv_selection(layout)
        self.create_results_section(layout)

    def create_model_status(self, layout):
        status_group = QGroupBox("🤖 Modelo para Clasificación")
        status_layout = QVBoxLayout(status_group)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Seleccionar modelo:"))
        self.model_selector_combo = QComboBox()
        self.model_selector_combo.setMinimumWidth(300)
        self.model_selector_combo.currentTextChanged.connect(self.on_model_selector_changed)
        selector_layout.addWidget(self.model_selector_combo, 1)

        self.btn_load_selected_model = QPushButton("📂 Cargar")
        self.btn_load_selected_model.setObjectName("btn_load_selected_model")
        self.btn_load_selected_model.clicked.connect(self.load_model_from_selector)
        self.btn_load_selected_model.setEnabled(False)
        selector_layout.addWidget(self.btn_load_selected_model)

        self.btn_refresh_selector = QPushButton("🔄")
        self.btn_refresh_selector.setToolTip("Actualizar lista de modelos")
        self.btn_refresh_selector.clicked.connect(self.refresh_model_selector)
        selector_layout.addWidget(self.btn_refresh_selector)
        status_layout.addLayout(selector_layout)

        self.model_status_label = QLabel("❌ Ningún modelo cargado")
        self.model_status_label.setObjectName("model_status_label")
        status_layout.addWidget(self.model_status_label)

        self.model_info_text = QTextEdit()
        self.model_info_text.setObjectName("model_info_text")
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(120)
        self.model_info_text.setPlaceholderText("La información del modelo cargado aparecerá aquí...")
        status_layout.addWidget(self.model_info_text)

        layout.addWidget(status_group)
    
    def create_cv_selection(self, layout):
        cv_group = QGroupBox("📄 Seleccionar CV para Clasificar")
        cv_layout = QHBoxLayout(cv_group) 

        cv_layout.addWidget(QLabel("Archivo:"))
        self.selected_file_label = QLabel("Ningún archivo seleccionado")
        self.selected_file_label.setObjectName("selected_file_label")
        cv_layout.addWidget(self.selected_file_label, 1)

        self.btn_select_cv = QPushButton("📁 Examinar CV")
        self.btn_select_cv.clicked.connect(self.select_cv_file)
        cv_layout.addWidget(self.btn_select_cv)
        
        self.btn_classify = QPushButton("🎯 Clasificar CV")
        self.btn_classify.setObjectName("btn_classify")
        self.btn_classify.clicked.connect(self.classify_cv)
        self.btn_classify.setEnabled(False)
        cv_layout.addWidget(self.btn_classify)
        
        layout.addWidget(cv_group)

    def create_results_section(self, layout):
        results_group = QGroupBox("📊 Resultados de la Clasificación")
        results_layout = QVBoxLayout(results_group)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.main_result = QTextEdit()
        self.main_result.setObjectName("main_result")
        self.main_result.setReadOnly(True)
        self.main_result.setPlaceholderText("El resultado principal y la interpretación aparecerán aquí...")
        splitter.addWidget(self.main_result)
        
        ranking_widget = QWidget() 
        ranking_layout = QVBoxLayout(ranking_widget)
        ranking_layout.setContentsMargins(0,0,0,0)
        
        ranking_label = QLabel("🏆 Ranking de Profesiones:")
        ranking_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        ranking_layout.addWidget(ranking_label)

        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(2)
        self.ranking_table.setHorizontalHeaderLabels(["Profesión", "Probabilidad"])
        header = self.ranking_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.ranking_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        ranking_layout.addWidget(self.ranking_table)
        splitter.addWidget(ranking_widget)
        
        # Intentar obtener el ancho de la ventana principal para el splitter,
        # pero esto podría ser problemático si la ventana aún no se ha mostrado.
        # Usar proporciones fijas es más seguro inicialmente.
        initial_width = self.width() if self.width() > 0 else 800 # fallback
        splitter.setSizes([int(initial_width * 0.6), int(initial_width * 0.4)])
        results_layout.addWidget(splitter)
        
        layout.addWidget(results_group)

    # --- Métodos de Lógica y Eventos (sin cambios significativos en el diseño) ---
    def select_profession_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de CVs")
        if folder:
            self.selected_folder = folder 
            self.profession_name_input.setFocus() 
            self.btn_add_profession.setEnabled(bool(self.profession_name_input.text().strip()))


    def add_profession_logic(self, name_input_widget, list_widget, folders_dict, btn_add, btn_train_widget, selected_folder_attr_name):
        profession_name = name_input_widget.text().strip()
        selected_folder = getattr(self, selected_folder_attr_name, None)

        if not profession_name:
            QMessageBox.warning(self, "Advertencia", "Ingresa el nombre de la profesión.")
            return
        if not selected_folder:
            QMessageBox.warning(self, "Advertencia", "Selecciona una carpeta primero.")
            return
        if profession_name in folders_dict:
            QMessageBox.warning(self, "Advertencia", f"La profesión '{profession_name}' ya está agregada.")
            return

        try:
            valid_files = [f for f in os.listdir(selected_folder)
                           if self.processor.is_supported_file(os.path.join(selected_folder, f))]
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"La carpeta '{selected_folder}' no fue encontrada.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo acceder a la carpeta: {e}")
            return


        if not valid_files:
            QMessageBox.warning(self, "Advertencia", "La carpeta seleccionada no contiene archivos de CV soportados (pdf, docx, doc, txt, png, jpg).")
            return

        folders_dict[profession_name] = selected_folder
        list_widget.addItem(f"📁 {profession_name} ({len(valid_files)} CVs)")
        
        name_input_widget.clear()
        if hasattr(self, selected_folder_attr_name):
            delattr(self, selected_folder_attr_name)
        btn_add.setEnabled(False)
        
        if btn_train_widget: 
             btn_train_widget.setEnabled(len(folders_dict) >= 2)

        QMessageBox.information(self, "Éxito", f"Profesión '{profession_name}' agregada con {len(valid_files)} CVs.")


    def add_profession(self):
        self.add_profession_logic(
            self.profession_name_input, 
            self.profession_list, 
            self.profession_folders, 
            self.btn_add_profession, 
            self.btn_train,
            'selected_folder'
        )

    def clear_professions_logic(self, list_widget, folders_dict, btn_train_widget):
        reply = QMessageBox.question(self, "Confirmar", 
                                     "¿Estás seguro de que quieres limpiar la lista de profesiones?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            folders_dict.clear()
            list_widget.clear()
            if btn_train_widget:
                btn_train_widget.setEnabled(False)

    def clear_professions(self):
        self.clear_professions_logic(self.profession_list, self.profession_folders, self.btn_train)
    
    def start_training(self):
        if len(self.profession_folders) < 2:
            QMessageBox.warning(self, "Advertencia", "Se necesitan al menos 2 profesiones para entrenar.")
            return

        model_name = self.training_model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Nombre Requerido", "Ingresa un nombre para el modelo.")
            return
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre Inválido", "El nombre solo puede contener letras, números, guiones y guiones bajos.")
            return

        existing_models = self.classifier.list_available_models()
        if any(m['name'] == model_name and not m.get('is_deep_learning', False) for m in existing_models):
            reply = QMessageBox.question(self, 'Modelo Existente',
                                       f'Ya existe un modelo tradicional con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        reply = QMessageBox.question(self, 'Confirmar Entrenamiento',
                                   f'¿Entrenar modelo "{model_name}" con {len(self.profession_folders)} profesiones?\n'
                                   f'Profesiones: {", ".join(self.profession_folders.keys())}',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_train.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) 
        self.training_log.clear()
        self.update_training_log(f"🚀 Iniciando entrenamiento del modelo '{model_name}'...")

        model_type = self.model_type_combo.currentData()

        self.training_thread = TrainingThread(self.profession_folders, model_type, model_name)
        self.training_thread.progress_updated.connect(self.update_training_log)
        self.training_thread.training_completed.connect(self.training_finished)
        self.training_thread.start()

    def update_training_log(self, message):
        # timestamp = QTimer.singleShot(0, lambda: None) # Para obtener un timestamp aproximado
        self.training_log.append(f"[{QTime.currentTime().toString('hh:mm:ss')}] {message}")
        self.training_log.moveCursor(QTextCursor.MoveOperation.End)


    def training_finished(self, success, results, message):
        self.btn_train.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0,100)

        if success:
            accuracy_str = f"{results.get('accuracy', 0):.1%}" if results.get('accuracy') is not None else "N/A"
            results_text = f"""
            ✅ ¡Entrenamiento completado exitosamente!
            Modelo: {self.training_model_name_input.text().strip()}
            -------------------------------------------
            📊 Resultados:
            • Precisión: {accuracy_str}
            • Muestras de entrenamiento: {results.get('train_samples', 'N/A')}
            • Muestras de prueba: {results.get('test_samples', 'N/A')}
            • Características extraídas: {results.get('features', 'N/A')}
            • Profesiones: {', '.join(results.get('classes', []))}
            -------------------------------------------
            💾 Modelo guardado en la carpeta 'models/'
            """
            self.update_training_log(results_text)
            QMessageBox.information(self, "Entrenamiento Completado", message)
            
            self.refresh_models_list()
            self.refresh_model_selector()
            
            model_name_trained = self.training_model_name_input.text().strip()
            if model_name_trained:
                self.current_loaded_model = model_name_trained
                self.current_model_is_dl = False 
                self.classifier.load_model(model_name_trained) 
                self.update_model_status_ui()
                self.update_classification_ui() 

            self.training_model_name_input.clear() 
            self.update_save_model_ui() 
        else:
            self.update_training_log(f"❌ Error: {message}")
            QMessageBox.critical(self, "Error en Entrenamiento", f"El entrenamiento falló:\n{message}")
        self.update_save_model_ui()


    def update_save_model_ui(self):
        is_model_ready_to_be_saved_separately = self.classifier.is_trained 
        
        if hasattr(self, 'btn_save_current_model'):
            self.btn_save_current_model.setEnabled(is_model_ready_to_be_saved_separately)
        
        if hasattr(self, 'current_model_status'): # Este widget no existe, revisar si es necesario
            if is_model_ready_to_be_saved_separately:
                self.current_model_status.setText("✅ Modelo entrenado listo para guardar (o ya guardado).")
                # self.current_model_status.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
            else:
                self.current_model_status.setText("❌ No hay modelo entrenado para guardar.")
                # self.current_model_status.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")


    def save_current_model(self): 
        active_classifier = self.dl_classifier if self.current_model_is_dl and self.dl_classifier else self.classifier
        
        if not active_classifier or not active_classifier.is_trained:
            QMessageBox.warning(self, "Sin Modelo", "No hay un modelo activo entrenado para guardar.")
            return

        # Asumimos que self.model_name_input es el de la pestaña "Mis Modelos" si se reimplementa esa sección.
        # Por ahora, este botón no está en la UI principal de "Mis Modelos".
        # Si se refiere al input de la pestaña de entrenamiento, no debería usarse aquí.
        # Para este ejemplo, asumiré que existe un self.model_name_input dedicado si esta función se usa.
        if not hasattr(self, 'model_name_input'):
             QMessageBox.critical(self, "Error de UI", "Input para nombre de modelo no encontrado para esta acción.")
             return

        model_name = self.model_name_input.text().strip() 
        if not model_name:
            QMessageBox.warning(self, "Nombre Requerido", "Ingresa un nombre para guardar el modelo.")
            return
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre Inválido", "El nombre solo puede contener letras, números, guiones y guiones bajos.")
            return

        existing_models = self.classifier.list_available_models() 
        if any(m['name'] == model_name and m.get('is_deep_learning', False) == self.current_model_is_dl for m in existing_models):
            reply = QMessageBox.question(self, 'Modelo Existente',
                                       f'Ya existe un modelo con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        try:
            success = active_classifier.save_model(model_name)
            if success:
                QMessageBox.information(self, "Modelo Guardado", f"El modelo '{model_name}' se guardó exitosamente.")
                self.model_name_input.clear()
                self.refresh_models_list()
                self.refresh_model_selector()
            else:
                QMessageBox.critical(self, "Error", "Error al guardar el modelo.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando modelo:\n{str(e)}")


    def refresh_models_list(self):
        try:
            models = self.classifier.list_available_models() 
            self.models_table.setRowCount(0)

            for model in models:
                row_position = self.models_table.rowCount()
                self.models_table.insertRow(row_position)

                self.models_table.setItem(row_position, 0, QTableWidgetItem(model.get('display_name', model['name'])))
                self.models_table.setItem(row_position, 1, QTableWidgetItem(model.get('model_type', 'N/A')))
                
                is_dl = model.get('is_deep_learning', False)
                category = "🧠 Deep Learning" if is_dl else "🤖 ML Tradicional"
                category_item = QTableWidgetItem(category)
                # category_item.setBackground(QColor("#eef2ff") if is_dl else QColor("#e7f3fe")) # Bulma: usar colores neutros
                self.models_table.setItem(row_position, 2, category_item)

                professions = model.get('professions', [])
                prof_text = ', '.join(professions[:3])
                if len(professions) > 3:
                    prof_text += f" (+{len(professions)-3} más)"
                self.models_table.setItem(row_position, 3, QTableWidgetItem(prof_text))
                
                self.models_table.setItem(row_position, 4, QTableWidgetItem(model.get('creation_date', 'N/A')))

                is_current_loaded = (self.current_loaded_model == model['name'] and 
                                     self.current_model_is_dl == is_dl)
                status = "🔄 Cargado" if is_current_loaded else "💤 Disponible"
                status_item = QTableWidgetItem(status)
                if is_current_loaded:
                    status_item.setForeground(QColor("#48c78e")) # Bulma success color
                    status_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                self.models_table.setItem(row_position, 5, status_item)
                
                self.models_table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, model) 

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando lista de modelos:\n{str(e)}")
            print(f"Error en refresh_models_list: {e}")


    def on_model_selection_changed(self):
        selected_rows = self.models_table.selectionModel().selectedRows()
        has_selection = bool(selected_rows)
        self.btn_load_model.setEnabled(has_selection)
        self.btn_delete_model.setEnabled(has_selection)
        self.btn_view_model_details.setEnabled(has_selection)

    def get_selected_model_data_from_table(self):
        selected_rows = self.models_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        return self.models_table.item(selected_rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def load_selected_model(self): 
        model_data = self.get_selected_model_data_from_table()
        if not model_data:
            QMessageBox.warning(self, "Sin Selección", "Selecciona un modelo de la tabla para cargar.")
            return
        
        self._load_model_by_data(model_data)

    def _load_model_by_data(self, model_data):
        model_name = model_data['name']
        is_deep_learning = model_data.get('is_deep_learning', False)
        
        try:
            classifier_to_use = None
            if is_deep_learning:
                if not DEEP_LEARNING_AVAILABLE or not self.dl_classifier:
                    QMessageBox.critical(self, "Error", "Módulo Deep Learning no disponible o no inicializado.")
                    return
                classifier_to_use = self.dl_classifier
            else:
                classifier_to_use = self.classifier

            success = classifier_to_use.load_model(model_name)
            if success:
                self.current_loaded_model = model_name
                self.current_model_is_dl = is_deep_learning
                QMessageBox.information(self, "Modelo Cargado", 
                                      f"El modelo '{model_data.get('display_name', model_name)}' se cargó exitosamente.")
                self.update_all_ui_after_model_change()
            else:
                QMessageBox.critical(self, "Error", f"Error al cargar el modelo '{model_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Excepción al cargar modelo '{model_name}':\n{str(e)}")
            print(f"Excepción en _load_model_by_data: {e}")

    def update_all_ui_after_model_change(self):
        self.refresh_models_list() 
        self.refresh_model_selector() 
        self.update_model_status_ui() 
        self.update_classification_ui() 
        self.update_save_model_ui() 


    def delete_selected_model(self):
        model_data = self.get_selected_model_data_from_table()
        if not model_data:
            QMessageBox.warning(self, "Sin Selección", "Selecciona un modelo para eliminar.")
            return

        model_name = model_data['name']
        is_dl = model_data.get('is_deep_learning', False)
        model_type_str = "Deep Learning" if is_dl else "Tradicional"

        reply = QMessageBox.question(self, 'Confirmar Eliminación',
                                   f'¿Estás seguro de que quieres eliminar el modelo {model_type_str} "{model_data.get("display_name", model_name)}"?\n'
                                   'Esta acción no se puede deshacer.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.classifier.delete_model(model_name, is_deep_learning=is_dl)
                if success:
                    QMessageBox.information(self, "Modelo Eliminado", 
                                          f"El modelo '{model_data.get('display_name', model_name)}' se eliminó.")
                    if self.current_loaded_model == model_name and self.current_model_is_dl == is_dl:
                        self.current_loaded_model = None
                        self.current_model_is_dl = False
                        if is_dl and self.dl_classifier:
                            self.dl_classifier.model = None 
                            self.dl_classifier.is_trained = False
                        elif not is_dl and self.classifier:
                            self.classifier.model = None
                            self.classifier.is_trained = False


                    self.update_all_ui_after_model_change()
                else:
                    QMessageBox.critical(self, "Error", f"No se pudo eliminar el modelo '{model_name}'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Excepción al eliminar modelo:\n{str(e)}")

    def view_model_details(self):
        model_data = self.get_selected_model_data_from_table()
        if not model_data:
            QMessageBox.warning(self, "Sin Selección", "Selecciona un modelo para ver sus detalles.")
            return

        details_html = f"""
        <h3 style="color:#485fc7;">📊 Detalles del Modelo: {model_data.get('display_name', model_data['name'])}</h3>
        <p><b>Nombre interno:</b> {model_data['name']}</p>
        <p><b>Tipo de algoritmo:</b> {model_data.get('model_type', 'N/A')}</p>
        <p><b>Categoría:</b> {"Deep Learning" if model_data.get('is_deep_learning', False) else "Machine Learning Tradicional"}</p>
        <p><b>Fecha de creación:</b> {model_data.get('creation_date', 'N/A')}</p>
        <p><b>Número de características:</b> {model_data.get('num_features', 'N/A')}</p>
        <p><b>Número de profesiones:</b> {model_data.get('num_professions', len(model_data.get('professions',[])))}</p>
        """
        
        professions = model_data.get('professions', [])
        if professions:
            details_html += "<p><b>🎯 Profesiones:</b></p><ul>"
            for prof in professions:
                details_html += f"<li>{prof}</li>"
            details_html += "</ul>"
        else:
            details_html += "<p><b>Profesiones:</b> No definidas.</p>"

        if model_data.get('is_deep_learning', False):
            details_html += "<h4 style='color:#485fc7;'>🧠 Detalles Deep Learning:</h4>"
            details_html += f"<p><b>Épocas entrenadas:</b> {model_data.get('epochs_trained', 'N/A')}</p>"
            details_html += f"<p><b>Batch size usado:</b> {model_data.get('batch_size_trained', 'N/A')}</p>"
            accuracy_val = model_data.get('accuracy')
            accuracy_display = f"{accuracy_val:.1%}" if isinstance(accuracy_val, float) else 'N/A'
            details_html += f"<p><b>Precisión (accuracy):</b> {accuracy_display}</p>"


        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Detalles - {model_data.get('display_name', model_data['name'])}")
        msg_box.setTextFormat(Qt.TextFormat.RichText) 
        msg_box.setText(details_html)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    # --- Métodos para Deep Learning (lógica) ---
    def select_dl_profession_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de CVs para DL")
        if folder:
            self.dl_selected_folder = folder
            self.dl_profession_name_input.setFocus()
            self.btn_dl_add_profession.setEnabled(bool(self.dl_profession_name_input.text().strip()))


    def add_dl_profession(self):
        self.add_profession_logic(
            self.dl_profession_name_input,
            self.dl_profession_list,
            self.dl_profession_folders,
            self.btn_dl_add_profession,
            self.btn_dl_train,
            'dl_selected_folder'
        )

    def clear_dl_professions(self):
        self.clear_professions_logic(self.dl_profession_list, self.dl_profession_folders, self.btn_dl_train)

    def start_dl_training(self):
        if not DEEP_LEARNING_AVAILABLE or not self.dl_classifier:
            QMessageBox.critical(self, "Error", "Módulo Deep Learning no disponible.")
            return
        if len(self.dl_profession_folders) < 2:
            QMessageBox.warning(self, "Advertencia", "Se necesitan al menos 2 profesiones para entrenar un modelo Deep Learning.")
            return

        model_name = self.dl_model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Nombre Requerido", "Ingresa un nombre para el modelo Deep Learning.")
            return
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre Inválido", "El nombre solo puede contener letras, números, guiones y guiones bajos.")
            return
        
        existing_models = self.classifier.list_available_models() 
        if any(m['name'] == model_name and m.get('is_deep_learning', False) for m in existing_models):
            reply = QMessageBox.question(self, 'Modelo Existente',
                                       f'Ya existe un modelo Deep Learning con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            epochs = int(self.dl_epochs_input.text())
            batch_size = int(self.dl_batch_size_input.text())
            if epochs <= 0 or batch_size <= 0:
                raise ValueError("Épocas y batch size deben ser positivos.")
        except ValueError as e:
            QMessageBox.warning(self, "Parámetros Inválidos", str(e))
            return

        model_type = self.dl_model_type_combo.currentData()

        reply = QMessageBox.question(self, 'Confirmar Entrenamiento DL',
                                   f'¿Entrenar modelo DL "{model_name}" ({model_type.upper()})?\n'
                                   f'Épocas: {epochs}, Batch Size: {batch_size}\n'
                                   f'Profesiones: {", ".join(self.dl_profession_folders.keys())}\n\n'
                                   f'⚠️ El entrenamiento puede tomar varios minutos.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_dl_train.setEnabled(False)
        self.dl_progress_bar.setVisible(True)
        self.dl_progress_bar.setRange(0, 0)
        self.dl_training_log.clear()
        self.update_dl_training_log(f"🚀 Iniciando entrenamiento del modelo DL '{model_name}' ({model_type.upper()})...")

        self.dl_training_thread = DeepLearningTrainingThread(
            self.dl_profession_folders, model_type, model_name, epochs, batch_size
        )
        self.dl_training_thread.progress_updated.connect(self.update_dl_training_log)
        self.dl_training_thread.training_completed.connect(self.dl_training_finished)
        self.dl_training_thread.start()

    def update_dl_training_log(self, message):
        # from PyQt6.QtCore import QTime # Ya importado globalmente
        self.dl_training_log.append(f"[{QTime.currentTime().toString('hh:mm:ss')}] {message}")
        self.dl_training_log.moveCursor(QTextCursor.MoveOperation.End)


    def dl_training_finished(self, success, results, message):
        self.btn_dl_train.setEnabled(True)
        self.dl_progress_bar.setVisible(False)
        self.dl_progress_bar.setRange(0,100)

        if success:
            self.update_dl_training_log(f"✅ Éxito: {message}")
            QMessageBox.information(self, "Entrenamiento DL Completado", message)
            
            self.refresh_models_list()
            self.refresh_model_selector()

            model_name_trained = self.dl_model_name_input.text().strip()
            if model_name_trained and self.dl_classifier:
                self.current_loaded_model = model_name_trained
                self.current_model_is_dl = True
                self.dl_classifier.load_model(model_name_trained)
                self.update_model_status_ui()
                self.update_classification_ui()

            self.dl_model_name_input.clear()
        else:
            self.update_dl_training_log(f"❌ Error: {message}")
            QMessageBox.critical(self, "Error en Entrenamiento DL", f"El entrenamiento Deep Learning falló:\n{message}")
        self.update_save_model_ui()


    def refresh_model_selector(self): 
        try:
            models = self.classifier.list_available_models()
            self.model_selector_combo.clear()

            if not models:
                self.model_selector_combo.addItem("No hay modelos disponibles")
                self.btn_load_selected_model.setEnabled(False)
                return

            for model_data in models:
                is_dl = model_data.get('is_deep_learning', False)
                category = "🧠 DL" if is_dl else "🤖 ML"
                display_name = model_data.get('display_name', model_data['name'])
                num_prof = len(model_data.get('professions', []))
                text = f"{category} - {display_name} ({num_prof} prof.)"
                self.model_selector_combo.addItem(text, model_data)

            self.btn_load_selected_model.setEnabled(True)

            if self.current_loaded_model:
                for i in range(self.model_selector_combo.count()):
                    item_data = self.model_selector_combo.itemData(i)
                    if (isinstance(item_data, dict) and 
                        item_data['name'] == self.current_loaded_model and
                        item_data.get('is_deep_learning', False) == self.current_model_is_dl):
                        self.model_selector_combo.setCurrentIndex(i)
                        break
            else: 
                if self.model_selector_combo.count() > 0 and self.model_selector_combo.itemText(0) != "No hay modelos disponibles":
                    self.model_selector_combo.setCurrentIndex(0)


        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error actualizando selector de modelos:\n{str(e)}")
            print(f"Error en refresh_model_selector: {e}")


    def on_model_selector_changed(self, text): 
        current_data = self.model_selector_combo.currentData()
        self.btn_load_selected_model.setEnabled(isinstance(current_data, dict))


    def load_model_from_selector(self): 
        model_data = self.model_selector_combo.currentData()
        if not isinstance(model_data, dict): 
            QMessageBox.warning(self, "Sin Selección", "Selecciona un modelo válido de la lista.")
            return
        self._load_model_by_data(model_data)

    def update_model_status_ui(self): 
        model_name_display = "Desconocido"
        info_html = ""

        if self.current_loaded_model:
            active_classifier = self.dl_classifier if self.current_model_is_dl and self.dl_classifier else self.classifier
            
            all_models = self.classifier.list_available_models()
            found_model_data = next((m for m in all_models if m['name'] == self.current_loaded_model and m.get('is_deep_learning', False) == self.current_model_is_dl), None)
            
            if found_model_data:
                model_name_display = found_model_data.get('display_name', self.current_loaded_model)


            model_type_str = "Deep Learning" if self.current_model_is_dl else "Tradicional"
            self.model_status_label.setText(f"✅ Modelo {model_type_str} '{model_name_display}' cargado y listo.")
            self.model_status_label.setStyleSheet("color: #48c78e; font-weight: bold;") # Bulma success

            if active_classifier and active_classifier.is_trained:
                model_info = active_classifier.get_model_info() if hasattr(active_classifier, 'get_model_info') else {}
                
                info_html = f"<b>Modelo Activo:</b> {model_name_display}<br>"
                info_html += f"<b>Tipo:</b> {model_info.get('model_type', model_type_str)}<br>"
                professions = model_info.get('professions', [])
                info_html += f"<b>Profesiones ({len(professions)}):</b> {', '.join(professions[:5])}"
                if len(professions) > 5:
                    info_html += f", ... (+{len(professions)-5})"
                info_html += "<br>"
                info_html += f"<b>Características:</b> {model_info.get('num_features', 'N/A')}"
                if self.current_model_is_dl:
                     info_html += f"<br><b>Max Length (tokens):</b> {getattr(active_classifier, 'max_length', 'N/A')}"


        else:
            self.model_status_label.setText("❌ Ningún modelo cargado. Selecciona uno de la lista.")
            self.model_status_label.setStyleSheet("color: #f14668; font-weight: bold;") # Bulma danger
        
        self.model_info_text.setHtml(info_html)
        self.update_classification_ui()


    def load_model_if_exists(self): 
        self.update_model_status_ui()
        self.update_classification_ui()


    def is_any_model_loaded_and_ready(self):
        if self.current_loaded_model:
            if self.current_model_is_dl:
                return self.dl_classifier and self.dl_classifier.is_trained
            else:
                return self.classifier and self.classifier.is_trained
        return False

    def update_classification_ui(self):
        ready_to_classify = self.is_any_model_loaded_and_ready() and hasattr(self, 'selected_cv_file')
        self.btn_classify.setEnabled(ready_to_classify)


    def select_cv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar CV para clasificar", "",
            "Archivos CV (*.pdf *.docx *.doc *.txt *.png *.jpg *.jpeg);;Todos los archivos (*)"
        )
        if file_path:
            if self.processor.is_supported_file(file_path):
                self.selected_cv_file = file_path
                self.selected_file_label.setText(os.path.basename(file_path))
                self.selected_file_label.setStyleSheet("color: #485fc7; font-weight: bold;") # Bulma primary
            else:
                QMessageBox.warning(self, "Formato No Soportado", 
                                  "El archivo seleccionado no es un formato de CV soportado (pdf, docx, doc, txt, png, jpg).")
                self.selected_file_label.setText("Formato no soportado")
                self.selected_file_label.setStyleSheet("color: #f14668; font-weight: bold;") # Bulma danger
                if hasattr(self, 'selected_cv_file'):
                    delattr(self, 'selected_cv_file')
            self.update_classification_ui()


    def classify_cv(self):
        if not self.is_any_model_loaded_and_ready():
            QMessageBox.warning(self, "Modelo No Cargado", "Carga un modelo antes de clasificar.")
            return
        if not hasattr(self, 'selected_cv_file'):
            QMessageBox.warning(self, "Archivo No Seleccionado", "Selecciona un archivo CV.")
            return

        active_classifier = self.dl_classifier if self.current_model_is_dl else self.classifier
        model_type_str = "Deep Learning" if self.current_model_is_dl else "Tradicional"

        try:
            self.main_result.setText(f"🔄 Procesando CV '{os.path.basename(self.selected_cv_file)}'...")
            QApplication.processEvents()

            raw_text = self.processor.extract_text_from_file(self.selected_cv_file)
            clean_text = self.processor.clean_text(raw_text)

            if not clean_text.strip(): 
                QMessageBox.warning(self, "Error de Extracción", "No se pudo extraer texto útil del CV o el CV está vacío.")
                self.main_result.setText("❌ No se pudo extraer texto del CV.")
                return

            self.main_result.append(f"\n🤖 Clasificando con modelo {model_type_str}...")
            QApplication.processEvents()
            
            prediction_result = active_classifier.predict_cv(clean_text)

            if prediction_result.get('error', False):
                QMessageBox.critical(self, "Error de Clasificación", prediction_result.get('message', 'Error desconocido.'))
                self.main_result.setText(f"❌ Error en clasificación: {prediction_result.get('message', '')}")
                return

            predicted_profession = prediction_result.get('predicted_profession', 'N/A')
            confidence = prediction_result.get('confidence', 0.0)
            confidence_percentage = f"{confidence:.1%}" if isinstance(confidence, float) else "N/A"
            confidence_level = prediction_result.get('confidence_level', 'N/A')

            main_html = f"""
            <h3 style="color:#363636;">🎯 Resultado de la Clasificación</h3>
            <p><b>Archivo:</b> {os.path.basename(self.selected_cv_file)}</p>
            <h3><b style="color:#485fc7;">Profesión Predicha: {predicted_profession}</b></h3>
            <p><b>Confianza:</b> {confidence_percentage} ({confidence_level})</p>
            """

            confidence_color = "#48c78e" # Bulma success (alta)
            if confidence_level == "Media": confidence_color = "#ffdd57"; text_color_conf = "#363636" # Bulma warning
            elif confidence_level == "Baja": confidence_color = "#f14668"; text_color_conf = "#ffffff" # Bulma danger
            else: text_color_conf = "#ffffff"
            
            main_html += f"""
            <p><b>Interpretación:</b> 
            <span style='background-color:{confidence_color}; color:{text_color_conf}; padding: 2px 5px; border-radius:3px;'>{prediction_result.get('interpretation', '')}</span>
            </p>
            """
            self.main_result.setHtml(main_html)

            self.ranking_table.setRowCount(0) 
            profession_ranking = prediction_result.get('profession_ranking', [])
            for i, rank_data in enumerate(profession_ranking):
                self.ranking_table.insertRow(i)
                item_prof = QTableWidgetItem(rank_data['profession'])
                item_perc = QTableWidgetItem(rank_data['percentage'])
                self.ranking_table.setItem(i, 0, item_prof)
                self.ranking_table.setItem(i, 1, item_perc)
                if rank_data['profession'] == predicted_profession:
                    # Usar un color de fondo sutil para la fila destacada
                    highlight_bg_color = QColor(confidence_color).lighter(180) if confidence_level != "Media" else QColor("#fffbeb") # Amarillo claro para media
                    item_prof.setBackground(highlight_bg_color)
                    item_perc.setBackground(highlight_bg_color)
                    item_prof.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                    item_perc.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))


        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Error durante la clasificación:\n{str(e)}")
            self.main_result.setText(f"❌ Error crítico en la clasificación: {str(e)}")
            print(f"Error en classify_cv: {e}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Clasificador de CVs por Profesiones v2.0")

    default_font = QFont("Segoe UI", 10) 
    app.setFont(default_font)

    window = CVClassifierGUI()
    window.show()

    QTimer.singleShot(200, lambda: show_welcome_message(window))

    sys.exit(app.exec())

def show_welcome_message(parent_window):
    welcome_html = """
    <h2 style="color:#485fc7;">🎯 ¡Bienvenido al Clasificador de CVs v2.0!</h2>
    <p>Esta herramienta te permite entrenar modelos de Machine Learning y Deep Learning para clasificar CVs por profesiones.</p>
    
    <h4 style="color:#363636;">🎓 Pestaña "Entrenar Modelo":</h4>
    <ul>
        <li>Organiza CVs en carpetas por profesión.</li>
        <li>Agrega cada profesión y su carpeta.</li>
        <li>Elige un nombre y tipo de algoritmo.</li>
        <li>Entrena y el modelo se guardará.</li>
    </ul>

    <h4 style="color:#363636;">🧠 Pestaña "Deep Learning":</h4>
    <ul>
        <li>Similar al entrenamiento tradicional, pero con modelos más avanzados (LSTM, CNN, BERT).</li>
        <li>Requiere más datos y tiempo, pero puede ofrecer mayor precisión.</li>
        <li>Asegúrate de tener <b>TensorFlow</b> y <b>Transformers</b> instalados.</li>
    </ul>

    <h4 style="color:#363636;">📚 Pestaña "Mis Modelos":</h4>
    <ul>
        <li>Visualiza todos tus modelos entrenados.</li>
        <li>Carga un modelo para usarlo en la pestaña de clasificación.</li>
        <li>Elimina modelos que ya no necesites.</li>
    </ul>

    <h4 style="color:#363636;">🔍 Pestaña "Clasificar CV":</h4>
    <ul>
        <li>Carga un modelo previamente entrenado.</li>
        <li>Selecciona un archivo de CV (pdf, docx, txt, etc.).</li>
        <li>Obtén la profesión predicha y un ranking de probabilidades.</li>
    </ul>
    
    <p><b>💡 Consejo:</b> Para mejores resultados, usa al menos 10-20 CVs por profesión para modelos tradicionales, y más para Deep Learning.</p>
    <p>¡Explora y clasifica!</p>
    """
    msg_box = QMessageBox(parent_window)
    msg_box.setWindowTitle("¡Bienvenido!")
    msg_box.setTextFormat(Qt.TextFormat.RichText) 
    msg_box.setText(welcome_html)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    # Aplicar estilo Bulma al QMessageBox también, si es posible o necesario
    # msg_box.setStyleSheet(parent_window.styleSheet()) # Heredar estilo
    msg_box.exec()


if __name__ == "__main__":
    # Crear stubs si no existen los archivos reales
    # Esto es solo para permitir que el script se ejecute sin errores de importación.
    # Necesitarás tus implementaciones reales para que funcione.
    
    if not os.path.exists("src"): 
        os.makedirs("src/utils", exist_ok=True)
        os.makedirs("src/models", exist_ok=True)
        os.makedirs("src/config", exist_ok=True)
    
    if not os.path.exists("src/utils/cv_processor.py"):
        with open("src/utils/cv_processor.py", "w", encoding="utf-8") as f:
            f.write("""
import os
class CVProcessor:
    def is_supported_file(self, file_path): return file_path.endswith(('.txt', '.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg'))
    def process_cv_folder(self, folder_path, profession): return [{'text': f'cv text from {f} for {profession}', 'profession': profession} for f in os.listdir(folder_path)[:2]] if os.path.exists(folder_path) else []
    def extract_text_from_file(self, file_path): return f'extracted text from {os.path.basename(file_path)} for testing purposes. This should contain actual CV content.'
    def clean_text(self, text): return text.lower().strip()
""")

    if not os.path.exists("src/config/settings.py"):
        with open("src/config/settings.py", "w", encoding="utf-8") as f:
            f.write("""
class Settings:
    MODEL_DIR = "cv_models_storage" 
""")
    if not os.path.exists(Settings.MODEL_DIR):
        os.makedirs(Settings.MODEL_DIR, exist_ok=True)

    if not os.path.exists("src/models/cv_classifier.py"):
        with open("src/models/cv_classifier.py", "w", encoding="utf-8") as f:
            f.write("""
import os, json, datetime
from src.config.settings import Settings
class CVClassifier:
    def __init__(self): self.is_trained = False; self.model = None; self.professions = []; self.model_type = "N/A"; self.num_features = 0
    def train_model(self, data, model_type):
        self.is_trained = True; self.professions = sorted(list(set(d['profession'] for d in data))); self.model_type = model_type
        self.num_features = 100 # Placeholder
        return {'accuracy': 0.95, 'train_samples': len(data), 'test_samples': 0, 'features': self.num_features, 'classes': self.professions}
    def save_model(self, model_name):
        if not os.path.exists(Settings.MODEL_DIR): os.makedirs(Settings.MODEL_DIR)
        path = os.path.join(Settings.MODEL_DIR, f"{model_name}.json")
        metadata = {'name': model_name, 'display_name': model_name.replace('_', ' ').title(), 'model_type': self.model_type, 
                    'creation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'professions': self.professions, 'num_features': self.num_features, 'num_professions': len(self.professions),
                    'is_deep_learning': False}
        with open(path, 'w', encoding='utf-8') as f: json.dump(metadata, f, indent=4)
        return True
    def load_model(self, model_name='cv_classifier'):
        path = os.path.join(Settings.MODEL_DIR, f"{model_name}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: metadata = json.load(f)
            if metadata.get('is_deep_learning', False): return False # This is for traditional ML
            self.professions = metadata.get('professions', [])
            self.model_type = metadata.get('model_type', 'N/A')
            self.num_features = metadata.get('num_features', 0)
            self.is_trained = True; return True
        return False
    def list_available_models(self):
        models = []
        if not os.path.exists(Settings.MODEL_DIR): return []
        for f_name in os.listdir(Settings.MODEL_DIR):
            if f_name.endswith('.json'):
                try:
                    with open(os.path.join(Settings.MODEL_DIR, f_name), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Ensure basic fields for display
                        data.setdefault('name', f_name.replace('.json', ''))
                        data.setdefault('display_name', data['name'].replace('_', ' ').title())
                        data.setdefault('model_type', 'N/A')
                        data.setdefault('creation_date', 'N/A')
                        data.setdefault('professions', [])
                        data.setdefault('is_deep_learning', False)
                        models.append(data)
                except Exception as e: print(f"Error loading model metadata {f_name}: {e}")
        return sorted(models, key=lambda x: x.get('creation_date', ''), reverse=True)
    def delete_model(self, model_name, is_deep_learning=False): 
        fname = f"{model_name}.json" 
        path = os.path.join(Settings.MODEL_DIR, fname)
        if os.path.exists(path): 
            try:
                with open(path, 'r', encoding='utf-8') as f: metadata = json.load(f)
                if metadata.get('is_deep_learning', False) == is_deep_learning: # Match type
                    os.remove(path); return True
            except: pass # Error reading or type mismatch
        return False
    def predict_cv(self, text):
        if not self.is_trained or not self.professions: return {'error': True, 'message': 'Modelo no entrenado o sin profesiones'}
        pred_prof = self.professions[0] if self.professions else "Desconocido"
        confidence = 0.85 + (len(text) % 10) / 100.0 # Dummy confidence
        confidence_level = "Alta" if confidence > 0.8 else ("Media" if confidence > 0.6 else "Baja")
        return {'error': False, 'predicted_profession': pred_prof, 'confidence': confidence, 
                'confidence_level': confidence_level, 
                'interpretation': f'El CV parece corresponder a {pred_prof} con confianza {confidence_level.lower()}.',
                'profession_ranking': [{'profession': p, 'percentage': f'{100/len(self.professions) + (i % 5 - 2):.1f}%'} for i, p in enumerate(self.professions)]}
    def get_model_info(self):
        if not self.is_trained: return {}
        return {'model_type': self.model_type, 'professions': self.professions, 
                'num_professions': len(self.professions), 'num_features': self.num_features,
                'is_deep_learning': False}
""")

    if DEEP_LEARNING_AVAILABLE and not os.path.exists("src/models/deep_learning_classifier.py"):
       with open("src/models/deep_learning_classifier.py", "w", encoding="utf-8") as f:
            f.write("""
from src.models.cv_classifier import CVClassifier # Base class
import os, json, datetime
from src.config.settings import Settings

class DeepLearningClassifier(CVClassifier): 
    def __init__(self):
        super().__init__() 
        self.model_type_dl = "LSTM" 
        self.max_length = 512
        self.epochs_trained = 0
        self.batch_size_trained = 0
        self.accuracy = 0.0

    def train_model(self, data, model_type='lstm', epochs=10, batch_size=32):
        self.is_trained = True
        self.professions = sorted(list(set(d['profession'] for d in data)))
        self.model_type_dl = model_type.upper()
        self.epochs_trained = epochs
        self.batch_size_trained = batch_size
        self.accuracy = 0.92 # Placeholder
        return {'success': True, 'accuracy': self.accuracy, 'epochs_trained': epochs, 
                'train_samples': len(data), 'test_samples': 0, 
                'classes': self.professions}

    def save_model(self, model_name): 
        if not os.path.exists(Settings.MODEL_DIR): os.makedirs(Settings.MODEL_DIR)
        path = os.path.join(Settings.MODEL_DIR, f"{model_name}.json") 
        metadata = {'name': model_name, 'display_name': model_name.replace('_', ' ').title(), 
                    'model_type': self.model_type_dl, 
                    'creation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'professions': self.professions, 'num_features': 'N/A (Embeddings)', 
                    'num_professions': len(self.professions),
                    'is_deep_learning': True, 
                    'epochs_trained': self.epochs_trained, 'batch_size_trained': self.batch_size_trained, 
                    'accuracy': self.accuracy, 
                    'max_length': self.max_length
                    }
        with open(path, 'w', encoding='utf-8') as f: json.dump(metadata, f, indent=4)
        return True

    def load_model(self, model_name): 
        path = os.path.join(Settings.MODEL_DIR, f"{model_name}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: metadata = json.load(f)
            if not metadata.get('is_deep_learning'): return False # Not a DL model
            self.professions = metadata.get('professions', [])
            self.model_type_dl = metadata.get('model_type', 'LSTM')
            self.max_length = metadata.get('max_length', 512)
            self.epochs_trained = metadata.get('epochs_trained', 0)
            self.batch_size_trained = metadata.get('batch_size_trained', 0)
            self.accuracy = metadata.get('accuracy', 0.0)
            self.is_trained = True
            return True
        return False

    def predict_cv(self, text):
        if not self.is_trained or not self.professions: return {'error': True, 'message': 'Modelo DL no entrenado o sin profesiones'}
        pred_prof = self.professions[0] if self.professions else "Desconocido (DL)"
        confidence = 0.88 + (len(text) % 10) / 100.0 # Dummy confidence
        confidence_level = "Alta" if confidence > 0.8 else ("Media" if confidence > 0.6 else "Baja")
        return {'error': False, 'predicted_profession': pred_prof, 'confidence': confidence, 
                'confidence_level': confidence_level, 
                'interpretation': f'El CV (DL) parece corresponder a {pred_prof} con confianza {confidence_level.lower()}.',
                'profession_ranking': [{'profession': p, 'percentage': f'{100/len(self.professions) + (i % 5 - 2):.1f}%'} for i, p in enumerate(self.professions)]}

    def get_model_info(self): 
        if not self.is_trained: return {}
        return {'model_type': self.model_type_dl, 'professions': self.professions, 
                'num_professions': len(self.professions), 'num_features': 'N/A (Embeddings)',
                'max_length': self.max_length, 'is_deep_learning': True,
                'epochs_trained': self.epochs_trained, 'batch_size_trained': self.batch_size_trained,
                'accuracy': self.accuracy}
""")
    # from PyQt6.QtCore import QTime # Ya está importado globalmente
    sys.exit(main())
