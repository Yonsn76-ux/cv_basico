# -*- coding: utf-8 -*-
"""
Interfaz gráfica principal para el Clasificador de CVs por Profesiones
Versión con diseño inspirado en Driver Booster.
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
from PyQt6.QtGui import QFont, QTextCursor, QColor, QIcon, QPixmap, QPainter, QBitmap

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

            from src.utils.cv_processor import CVProcessor 
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

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(40)  # Altura de la barra de título

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)  # Márgenes ajustados
        layout.setSpacing(10)

        # Icono de la aplicación (opcional)
        # Puedes crear un QPixmap simple o cargar una imagen
        icon_label = QLabel()
        # Ejemplo de icono simple (círculo azul)
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#D1001F")) # Rojo Driver Booster
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 22, 22)
        painter.end()
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        self.title_label = QLabel("🎯 Clasificador de CVs ")
        self.title_label.setObjectName("custom_title_label")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Botón para cambiar tema claro/oscuro
        self.theme_button = QPushButton("🌙")
        self.theme_button.setObjectName("window_button")
        self.theme_button.setFixedSize(30, 30)
        self.theme_button.clicked.connect(self.parent_window.toggle_theme)
        layout.addWidget(self.theme_button)

        # Botones de la ventana (Minimizar, Maximizar, Cerrar)
        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("window_button")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton("□") # Podría cambiar a un icono de maximizar/restaurar
        self.maximize_button.setObjectName("window_button")
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        layout.addWidget(self.maximize_button)

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("window_button_close")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_button)

        self.mouse_pressed = False
        self.drag_position = None

    def toggle_maximize_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            # self.maximize_button.setText("□") # Icono de maximizar
        else:
            self.parent_window.showMaximized()
            # self.maximize_button.setText("❐") # Icono de restaurar (o similar)


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = True
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.mouse_pressed:
            if self.parent_window.isMaximized(): # No mover si está maximizado
                 # Opcional: permitir "des-maximizar" al arrastrar desde la barra de título
                self.parent_window.showNormal()
                # Ajustar la posición para que la ventana no salte
                new_pos = event.globalPosition().toPoint()
                self.drag_position = QPoint(self.width() // 2, self.height() // 2) # Centrar cursor
                self.parent_window.move(new_pos - self.drag_position)

            else:
                self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            event.accept()


class CVClassifierGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Configurar ventana sin marco estándar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        # Permitir redimensionar una ventana sin marco (requiere más manejo manual)
        # self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint) # No funciona bien solo

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

        # Indicador de tema oscuro. Por defecto estilo oscuro al estilo Driver Booster
        self.dark_mode = True

        self.init_ui()
        self.load_model_if_exists()

        self.refresh_models_list()
        self.refresh_model_selector()
        self.update_save_model_ui() 
        self.update_classification_ui() 

    def get_stylesheet(self, dark=False):
        """Retorna la hoja de estilos en modo claro u oscuro"""
        # Paleta de colores inspirada en Driver Booster
        GOOGLE_BLUE = "#D1001F"  # rojo principal
        GOOGLE_BLUE_DARK = "#9A0016"
        GOOGLE_GREEN = "#4CAF50"
        GOOGLE_GREEN_DARK = "#388E3C"
        GOOGLE_YELLOW = "#FFCA28"
        GOOGLE_YELLOW_DARK = "#FFA000"
        GOOGLE_RED = "#EF5350"
        GOOGLE_RED_DARK = "#D32F2F"

        GREY_900 = "#FFFFFF"  # Texto principal claro
        GREY_800 = "#E0E0E0"  # Texto secundario
        GREY_700 = "#BDBDBD"  # Bordes, iconos
        GREY_600 = "#9E9E9E"
        GREY_500 = "#757575"
        GREY_400 = "#616161"
        GREY_300 = "#424242"  # Bordes sutiles, fondos de input
        GREY_200 = "#303030"  # Fondos de hover
        GREY_100 = "#212121"  # Paneles
        GREY_50 = "#121212"   # Fondo principal

        WHITE = "#FFFFFF"
        BLACK = "#000000"

        # Valores por defecto para modo claro (estilo Driver Booster)
        _BACKGROUND = WHITE
        _SURFACE = GREY_100
        _TEXT_PRIMARY = GREY_800
        _TEXT_SECONDARY = GREY_700
        _PRIMARY_ACCENT = GOOGLE_BLUE
        _PRIMARY_ACCENT_HOVER = GOOGLE_BLUE_DARK

        CONSOLE_BG = "#F3F3F3"
        CONSOLE_TEXT = "#333333"

        if dark:
            _BACKGROUND = GREY_50
            _SURFACE = GREY_100
            _TEXT_PRIMARY = GREY_900
            _TEXT_SECONDARY = GREY_800
            _PRIMARY_ACCENT = GOOGLE_BLUE
            _PRIMARY_ACCENT_HOVER = GOOGLE_BLUE_DARK
            CONSOLE_BG = "#1E1E1E"
            CONSOLE_TEXT = "#D4D4D4"

        # Hoja de estilos QSS
        return f"""
            QMainWindow {{
                background-color: {_BACKGROUND};
                border-radius: 8px; /* Para la ventana sin marco */
            }}
            QWidget {{
                color: {_TEXT_PRIMARY};
                font-family: "Roboto", "Segoe UI", Arial, sans-serif;
                font-size: 10pt;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QWidget#central_widget_for_scroll {{ /* Widget dentro del QScrollArea */
                 background-color: {_BACKGROUND};
            }}


            /* Custom Title Bar */
            CustomTitleBar {{
                background-color: {GREY_100}; /* Ligeramente diferente del fondo principal */
                border-bottom: 1px solid {GREY_300};
            }}
            QLabel#custom_title_label {{
                color: {_TEXT_PRIMARY};
                font-size: 11pt;
                font-weight: 500; /* Medium weight */
            }}
            QPushButton#window_button, QPushButton#window_button_close {{
                background-color: transparent;
                border: none;
                color: {GREY_700};
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton#window_button:hover {{
                background-color: {GREY_200};
                color: {GREY_900};
            }}
            QPushButton#window_button_close:hover {{
                background-color: #fddddd; /* Rojo muy claro para cerrar */
                color: {GOOGLE_RED};
            }}


            /* Header de la aplicación (debajo de la barra de título personalizada) */
            QWidget#app_header {{
                background: {_SURFACE};
                border-bottom: 1px solid {GREY_300};
                padding: 10px 20px; /* Ajustar padding */
            }}
            QLabel#header_title {{
                color: {_TEXT_PRIMARY};
                font-size: 16pt; 
                font-weight: 500; /* Medium weight */
                background: transparent;
            }}
            QLabel#header_subtitle {{
                color: {_TEXT_SECONDARY};
                font-size: 10pt;
                background: transparent;
            }}

            QTabWidget::pane {{
                border: none; /* Sin borde alrededor del panel de pestañas */
                background-color: {_BACKGROUND};
            }}
            QTabBar::tab {{
                background: transparent;
                border: none;
                border-left: 4px solid transparent;
                padding: 12px 20px;
                margin-bottom: 4px; /* Espacio entre pestañas verticales */
                color: {_TEXT_SECONDARY};
                font-weight: 500; /* Medium */
                font-size: 10.5pt;
            }}
            QTabBar::tab:selected {{
                color: {_PRIMARY_ACCENT};
                background-color: {GREY_50};
                border-left: 4px solid {_PRIMARY_ACCENT};
            }}
            QTabBar::tab:!selected:hover {{
                color: {_TEXT_PRIMARY};
                background-color: {GREY_100}; /* Sutil hover */
                border-left: 4px solid {GREY_100};
            }}

            QGroupBox {{
                background-color: {_SURFACE}; 
                border: 1px solid {GREY_300};
                border-radius: 8px; 
                margin-top: 15px;  
                padding: 25px 20px 20px 20px; 
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                left: 15px;
                top: 0px; 
                color: {_TEXT_PRIMARY};
                background-color: {_SURFACE}; 
                border-radius: 4px;
                font-size: 12pt;
                font-weight: 500; /* Medium */
            }}

            QPushButton {{
                background-color: {GREY_200};
                color: {_TEXT_PRIMARY};
                border: 1px solid {GREY_300};
                border-radius: 6px; 
                padding: 9px 18px;
                font-weight: 500; /* Medium */
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {GREY_300};
                border-color: {GREY_400};
            }}
            QPushButton:pressed {{
                background-color: {GREY_400};
            }}
            QPushButton:disabled {{
                background-color: {GREY_100};
                color: {GREY_500};
                border-color: {GREY_200};
            }}

            QPushButton#btn_classify {{
                background-color: {_PRIMARY_ACCENT};
                color: {WHITE};
                border: none;
                border-radius: 70px;
                min-width: 140px;
                min-height: 140px;
                font-size: 14pt;
            }}
            QPushButton#btn_save_current_model,
            QPushButton#btn_load_selected_model, QPushButton#btn_load_model,
            QPushButton#btn_add_profession, QPushButton#btn_dl_add_profession,
            QPushButton#btn_train, QPushButton#btn_dl_train {{
                background-color: {_PRIMARY_ACCENT};
                color: {WHITE};
                border: none;
            }}
            QPushButton#btn_classify:hover,
            QPushButton#btn_save_current_model:hover,
            QPushButton#btn_load_selected_model:hover, QPushButton#btn_load_model:hover,
            QPushButton#btn_add_profession:hover, QPushButton#btn_dl_add_profession:hover,
            QPushButton#btn_train:hover, QPushButton#btn_dl_train:hover {{
                background-color: {_PRIMARY_ACCENT_HOVER};
            }}
            
            QPushButton#btn_delete_model {{
                background-color: {GOOGLE_RED};
                color: {WHITE};
                border: none;
            }}
            QPushButton#btn_delete_model:hover {{
                background-color: {GOOGLE_RED_DARK};
            }}

            QLineEdit, QComboBox, QTextEdit {{
                border: 1px solid {GREY_400};
                border-radius: 6px;
                padding: 8px 12px; 
                background-color: {_SURFACE};
                min-height: 22px;
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border-color: {_PRIMARY_ACCENT}; 
                /* Podríamos añadir un efecto de sombra sutil si QSS lo permitiera bien */
            }}
            QComboBox::item:selected {{
                background-color: {_PRIMARY_ACCENT};
                color: {WHITE};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 22px;
                border-left-width: 1px;
                border-left-color: {GREY_300};
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }}
            QComboBox::down-arrow {{
                image: url(./assets/down_arrow_grey.svg); /* Requeriría un SVG o PNG */
                 /* Si no hay icono, Qt usa uno por defecto. Para personalizar, necesitarías un archivo de imagen */
            }}
            QComboBox QAbstractItemView {{ /* Para el popup del ComboBox */
                border: 1px solid {GREY_300};
                background-color: {_SURFACE};
                selection-background-color: {_PRIMARY_ACCENT};
                selection-color: {WHITE};
                border-radius: 4px;
                padding: 2px;
            }}


            QTextEdit#training_log, QTextEdit#dl_training_log {{
                background-color: {CONSOLE_BG};
                color: {CONSOLE_TEXT};
                font-family: "Consolas", "Courier New", monospace;
                font-size: 9.5pt;
                border-radius: 6px;
                border: 1px solid {GREY_700};
            }}
            QTextEdit#model_info_text, QTextEdit#main_result {{
                background-color: {GREY_100}; 
                border-radius: 6px;
                border: 1px solid {GREY_300};
            }}

            QListWidget {{
                border: 1px solid {GREY_300};
                border-radius: 6px;
                background-color: {_SURFACE};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 7px 10px;
                border-radius: 4px;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{
                background-color: {_PRIMARY_ACCENT};
                color: {WHITE};
                border: none; 
            }}
            QListWidget::item:hover:!selected {{ 
                background-color: {GREY_100};
                color: {_TEXT_PRIMARY};
            }}

            QTableWidget {{
                border: 1px solid {GREY_300};
                border-radius: 6px;
                gridline-color: {GREY_200}; 
                background-color: {_SURFACE};
                selection-background-color: {_PRIMARY_ACCENT};
                selection-color: {WHITE};
                alternate-background-color: {GREY_50};
            }}
            QHeaderView::section {{
                background-color: {GREY_100}; 
                padding: 10px 8px;
                border: none; 
                border-bottom: 1px solid {GREY_300}; 
                font-weight: 500; /* Medium */
                font-size: 10pt;
            }}
            QHeaderView::section:horizontal {{
                border-right: 1px solid {GREY_300}; 
            }}
             QHeaderView::section:horizontal:last {{
                border-right: none;
            }}

            QProgressBar {{
                border: 1px solid {GREY_300};
                border-radius: 10px; /* Más redondeado */
                text-align: center;
                background-color: {GREY_200};
                color: {_TEXT_SECONDARY};
                font-weight: 500; /* Medium */
                height: 20px; 
            }}
            QProgressBar::chunk {{
                background-color: {_PRIMARY_ACCENT}; 
                border-radius: 9px; /* Para que encaje en la barra redondeada */
                margin: 1px; 
            }}

            QLabel {{
                background-color: transparent;
                padding: 2px;
            }}
            QLabel#model_status_label {{
                font-size: 11pt;
                font-weight: 500; /* Medium */
                padding: 8px 0; 
            }}
            QLabel#selected_file_label {{
                font-weight: normal; 
                padding: 5px;
                border: 1px dashed {GREY_400}; 
                border-radius: 4px;
                background-color: {GREY_50};
            }}

            .InstructionLabel {{ 
                border-radius: 6px;
                padding: 12px 18px;
                margin-bottom: 10px; 
                border-width: 1px;
                border-style: solid;
                font-size: 9.5pt;
            }}
            QLabel#training_instructions {{ 
                background-color: #e3f2fd; /* Azul muy claro */
                border-color: #90caf9;
                color: #1e88e5; /* Texto azul */
            }}
            QLabel#dl_instructions {{ 
                background-color: #e8eaf6; /* Indigo muy claro */
                border-color: #9fa8da;
                color: #3949ab; /* Texto indigo */
            }}
            QLabel#dl_warning_label {{ 
                background-color: #fff3e0; /* Naranja muy claro */
                border-color: #ffcc80;
                color: #ef6c00; /* Texto naranja */
            }}
            QLabel#dl_note_label {{ 
                background-color: {GREY_100}; 
                border: 1px solid {GREY_300};
                color: {_TEXT_SECONDARY}; 
                font-size: 9pt;
            }}
            QLabel#models_instructions {{ 
                background-color: #e0f2f1; /* Teal muy claro */
                border-color: #80cbc4;
                color: #00796b; /* Texto teal */
            }}
            
            QSplitter::handle {{
                background-color: {GREY_300};
            }}
            QSplitter::handle:horizontal {{
                height: 3px; 
            }}
            QSplitter::handle:vertical {{
                width: 3px; 
            }}
            QSplitter::handle:hover {{
                background-color: {_PRIMARY_ACCENT};
            }}

            /* Scrollbars personalizadas */
            QScrollBar:vertical {{
                border: none;
                background: {GREY_100};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {GREY_400};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {GREY_500};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                border: none;
                background: {GREY_100};
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {GREY_400};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {GREY_500};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {{
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """

    def init_ui(self):
        # El título de la ventana ahora se manejará en la CustomTitleBar
        # self.setWindowTitle("🎯 Clasificador de CVs por Profesiones v2.0 (Estilo Google)") 
        self.setMinimumSize(1000, 750)
        self.resize(1400, 900)
        
        # Crear widget central que contendrá la barra de título y el contenido principal
        main_container = QWidget()
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(0,0,0,0) # Sin márgenes para que la barra de título se pegue arriba
        main_container_layout.setSpacing(0)

        # Barra de título personalizada
        self.title_bar = CustomTitleBar(self)
        main_container_layout.addWidget(self.title_bar)

        # Contenido principal de la aplicación (lo que antes era el widget central)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(18) 
        content_layout.setContentsMargins(20, 15, 20, 20) # Ajustar márgenes debajo de la barra de título

        # Aplicar la hoja de estilos inicial
        # Es importante aplicarla al QMainWindow para que CustomTitleBar herede estilos
        self.apply_stylesheet()

        # El QScrollArea ahora va dentro del content_widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setObjectName("main_scroll_area")
        
        central_widget_for_scroll = QWidget() 
        central_widget_for_scroll.setObjectName("central_widget_for_scroll")
        scroll_area.setWidget(central_widget_for_scroll)
        
        # Layout principal para el contenido dentro del scroll
        main_scroll_layout = QVBoxLayout(central_widget_for_scroll)
        main_scroll_layout.setSpacing(20)
        main_scroll_layout.setContentsMargins(0, 0, 0, 0) # El padding lo da content_layout

        self.create_header(main_scroll_layout) # El header de la app, no la barra de título
        self.create_tabs(main_scroll_layout)

        content_layout.addWidget(scroll_area) # Añadir scroll area al content_layout
        main_container_layout.addWidget(content_widget) # Añadir content_widget al layout principal del contenedor

        self.setCentralWidget(main_container) # Establecer el contenedor como widget central
        self.center_window()
        
        if self.classifier:
            if hasattr(self.classifier, 'model_changed_signal'): 
                self.classifier.model_changed_signal.connect(self.update_save_model_ui)

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        window_rect.moveCenter(screen.center())
        self.move(window_rect.topLeft())

    def apply_stylesheet(self):
        """Aplica la hoja de estilos según el modo actual"""
        self.setStyleSheet(self.get_stylesheet(self.dark_mode))
        if hasattr(self, "title_bar"):
            self.title_bar.theme_button.setText("☀️" if self.dark_mode else "🌙")

    def toggle_theme(self):
        """Alterna entre modo claro y oscuro"""
        self.dark_mode = not self.dark_mode
        self.apply_stylesheet()

    def get_basic_stylesheet(self):
        """Hoja de estilos simplificada (no utilizada actualmente)"""
        return """
        QMainWindow {
            background-color: #f8f9fa;
        }

        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: white;
            border-radius: 8px;
            margin-top: 5px;
        }

        QTabWidget::tab-bar {
            alignment: center;
        }

        QTabBar::tab {
            background-color: #e9ecef;
            color: #495057;
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
            min-width: 120px;
        }

        QTabBar::tab:selected {
            background-color: white;
            color: #007bff;
            border-bottom: 2px solid #007bff;
        }

        QTabBar::tab:hover {
            background-color: #f8f9fa;
            color: #0056b3;
        }

        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            color: #343a40;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
            background-color: white;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            background-color: white;
        }

        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: 500;
            font-size: 13px;
            min-height: 20px;
        }

        QPushButton:hover {
            background-color: #0056b3;
        }

        QPushButton:pressed {
            background-color: #004085;
        }

        QPushButton:disabled {
            background-color: #6c757d;
            color: #adb5bd;
        }

        QLineEdit, QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 13px;
            background-color: white;
            min-height: 20px;
        }

        QLineEdit:focus, QComboBox:focus {
            border-color: #007bff;
            outline: none;
        }

        QTextEdit {
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            padding: 8px;
        }

        QListWidget {
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
            alternate-background-color: #f8f9fa;
            padding: 4px;
        }

        QTableWidget {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background-color: white;
            gridline-color: #dee2e6;
            selection-background-color: #e3f2fd;
        }

        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f1f3f4;
        }

        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }

        QHeaderView::section {
            background-color: #f8f9fa;
            color: #495057;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }

        QProgressBar {
            border: 1px solid #ced4da;
            border-radius: 4px;
            text-align: center;
            background-color: #f8f9fa;
            height: 20px;
        }

        QProgressBar::chunk {
            background-color: #28a745;
            border-radius: 3px;
        }

        QLabel {
            color: #495057;
        }

        QScrollArea {
            border: none;
            background-color: transparent;
        }
        """

    def create_header(self, layout): # Este es el header *debajo* de la barra de título personalizada
        header_widget = QWidget()
        header_widget.setObjectName("app_header")
        # header_widget.setFixedHeight(70) # Ajustar altura si es necesario

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0) # El padding ya está en el QSS

        title_vbox = QVBoxLayout()
        title = QLabel("Clasificador Inteligente de CVs") 
        title.setObjectName("header_title")
        
        subtitle = QLabel("Potenciado por Modelos de Machine Learning y Deep Learning")
        subtitle.setObjectName("header_subtitle")

        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        title_vbox.setSpacing(2)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addWidget(header_widget)

    def create_tabs(self, layout):
        tabs = QTabWidget()
        tabs.setObjectName("main_tab_widget")
        tabs.setTabPosition(QTabWidget.TabPosition.West)

        training_tab = QWidget()
        training_tab.setObjectName("training_tab_content")
        self.create_training_tab(training_tab)
        tabs.addTab(training_tab, "🎓 Entrenar Modelo")

        if DEEP_LEARNING_AVAILABLE:
            deep_learning_tab = QWidget()
            deep_learning_tab.setObjectName("dl_tab_content")
            self.create_deep_learning_tab(deep_learning_tab)
            tabs.addTab(deep_learning_tab, "🧠 Deep Learning")

        models_tab = QWidget()
        models_tab.setObjectName("models_tab_content")
        self.create_models_tab(models_tab)
        tabs.addTab(models_tab, "📚 Mis Modelos")

        classification_tab = QWidget()
        classification_tab.setObjectName("classification_tab_content")
        self.create_classification_tab(classification_tab)
        tabs.addTab(classification_tab, "🔍 Clasificar CV")

        layout.addWidget(tabs)

    def create_training_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5) # Pequeño margen interno para la pestaña
        
        instructions = QLabel("""
        <b>Organiza y entrena tus modelos de clasificación de CVs.</b><br>
        1. Define profesiones y asigna carpetas con ejemplos de CVs (.pdf, .docx, .txt).<br>
        2. Elige un nombre descriptivo y el algoritmo de Machine Learning a utilizar.<br>
        3. Inicia el entrenamiento. El progreso se mostrará en el registro.
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("training_instructions") 
        instructions.setProperty("class", "InstructionLabel") 
        layout.addWidget(instructions)
        
        self.create_profession_config(layout, is_dl=False)
        self.create_training_config(layout)
        self.create_training_log(layout)
        layout.addStretch() # Para empujar contenido hacia arriba si hay espacio

    def create_profession_config(self, layout, is_dl=False):
        group_title = "1. Configuración de Profesiones y Datos"
        if is_dl:
            group_title = "1. Configuración de Profesiones para Deep Learning"
        
        prof_group = QGroupBox(group_title)
        prof_layout = QVBoxLayout(prof_group)

        if is_dl: 
            note = QLabel("""
            Los modelos de Deep Learning generalmente requieren un volumen de datos mayor y más diverso para un rendimiento óptimo. Considera al menos 50-100 CVs por cada profesión.
            """)
            note.setWordWrap(True)
            note.setObjectName("dl_note_label")
            note.setProperty("class", "InstructionLabel")
            prof_layout.addWidget(note)

        add_layout = QGridLayout() # Usar GridLayout para mejor alineación
        add_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Ej: Ingeniero de Software, Agrónomo")
        
        btn_select_folder = QPushButton("📁 Seleccionar Carpeta de CVs")
        btn_add_profession = QPushButton("➕ Agregar Profesión")
        btn_add_profession.setObjectName("btn_add_profession" if not is_dl else "btn_dl_add_profession")
        btn_add_profession.setEnabled(False)

        add_layout.addWidget(QLabel("Nombre de Profesión:"), 0, 0)
        add_layout.addWidget(name_input, 0, 1, 1, 2) # Ocupa dos columnas
        add_layout.addWidget(btn_select_folder, 1, 1)
        add_layout.addWidget(btn_add_profession, 1, 2)
        prof_layout.addLayout(add_layout)
        
        list_widget = QListWidget()
        list_widget.setMaximumHeight(180) 
        list_widget.setObjectName("profession_list_widget")
        prof_layout.addWidget(QLabel("Profesiones y carpetas añadidas:"))
        prof_layout.addWidget(list_widget)
        
        btn_clear_professions = QPushButton("🗑️ Limpiar Lista de Profesiones")
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
        config_group = QGroupBox("2. Configuración del Modelo y Entrenamiento")
        config_layout = QGridLayout(config_group)
        config_layout.setSpacing(10)

        config_layout.addWidget(QLabel("Nombre del modelo:"), 0, 0)
        self.training_model_name_input = QLineEdit()
        self.training_model_name_input.setPlaceholderText("Ej: modelo_tecnologia_rf_2025")
        config_layout.addWidget(self.training_model_name_input, 0, 1, 1, 2)

        config_layout.addWidget(QLabel("Tipo de algoritmo (ML):"), 1, 0)
        self.model_type_combo = QComboBox()
        algorithms = [
            ("random_forest", "Random Forest (Recomendado, Equilibrado)"),
            ("logistic_regression", "Regresión Logística (Rápido, Lineal)"),
            ("svm", "Máquina de Vectores de Soporte (SVM)"),
            ("naive_bayes", "Naive Bayes (Simple, Bueno para texto)")
        ]
        for value, display_name in algorithms:
            self.model_type_combo.addItem(display_name, value)
        self.model_type_combo.setCurrentIndex(0)
        self.model_type_combo.setToolTip(
             "Selecciona el algoritmo de Machine Learning para el entrenamiento.\n"
             "Random Forest suele ofrecer un buen balance entre precisión y velocidad."
        )
        config_layout.addWidget(self.model_type_combo, 1, 1, 1, 2)

        self.btn_train = QPushButton("🚀 Iniciar Entrenamiento del Modelo")
        self.btn_train.setObjectName("btn_train")
        self.btn_train.clicked.connect(self.start_training)
        self.btn_train.setEnabled(False)
        config_layout.addWidget(self.btn_train, 2, 1, 1, 2, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(config_group)

    def create_training_log(self, layout):
        log_group = QGroupBox("3. Registro y Progreso del Entrenamiento")
        log_layout = QVBoxLayout(log_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True) # Mostrar porcentaje
        log_layout.addWidget(self.progress_bar)
        
        self.training_log = QTextEdit()
        self.training_log.setObjectName("training_log")
        self.training_log.setReadOnly(True)
        self.training_log.setMinimumHeight(150) # Asegurar altura mínima
        self.training_log.setPlaceholderText("El progreso detallado del entrenamiento aparecerá aquí...")
        log_layout.addWidget(self.training_log)
        
        layout.addWidget(log_group)

    def create_deep_learning_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5)

        instructions = QLabel("""
        <b>Entrena modelos avanzados de Deep Learning (LSTM, CNN, Transformers como BERT).</b><br>
        Estos modelos pueden capturar relaciones más complejas en los datos, pero usualmente requieren más recursos computacionales y tiempo de entrenamiento.
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("dl_instructions")
        instructions.setProperty("class", "InstructionLabel")
        layout.addWidget(instructions)

        if not DEEP_LEARNING_AVAILABLE:
            warning = QLabel("""
            <b>⚠️ Componentes de Deep Learning no disponibles.</b><br>
            Para habilitar esta funcionalidad, por favor instala las bibliotecas necesarias:<br>
            <code>pip install tensorflow tensorflow-text transformers</code><br>
            (Puede requerir configuración adicional dependiendo de tu sistema y hardware).
            """)
            warning.setTextFormat(Qt.TextFormat.RichText)
            warning.setWordWrap(True)
            warning.setObjectName("dl_warning_label")
            warning.setProperty("class", "InstructionLabel")
            layout.addWidget(warning)
            layout.addStretch()
            return

        self.create_profession_config(layout, is_dl=True)
        self.create_dl_training_config(layout)
        self.create_dl_training_log(layout)
        layout.addStretch()

    def create_dl_training_config(self, layout):
        config_group = QGroupBox("2. Configuración del Modelo Deep Learning")
        config_layout = QGridLayout(config_group)
        config_layout.setSpacing(10)

        config_layout.addWidget(QLabel("Nombre del modelo DL:"), 0, 0)
        self.dl_model_name_input = QLineEdit()
        self.dl_model_name_input.setPlaceholderText("Ej: modelo_dl_bert_multilingue")
        config_layout.addWidget(self.dl_model_name_input, 0, 1, 1, 3)

        config_layout.addWidget(QLabel("Tipo de arquitectura DL:"), 1, 0)
        self.dl_model_type_combo = QComboBox()
        dl_models = [
            ("bert", "BERT (Transformer, Alta Precisión)"),
            ("lstm", "LSTM (Red Neuronal Recurrente)"),
            ("cnn", "CNN (Red Neuronal Convolucional para Texto)")
        ]
        for value, display_name in dl_models:
            self.dl_model_type_combo.addItem(display_name, value)
        self.dl_model_type_combo.setCurrentIndex(0)
        self.dl_model_type_combo.setToolTip(
            "Selecciona la arquitectura base para el modelo de Deep Learning.\n"
            "BERT suele ser el más potente pero también el más demandante."
        )
        config_layout.addWidget(self.dl_model_type_combo, 1, 1, 1, 3)

        config_layout.addWidget(QLabel("Número de Épocas:"), 2, 0)
        self.dl_epochs_input = QLineEdit("5") # Menos épocas por defecto para DL
        self.dl_epochs_input.setMaximumWidth(100)
        self.dl_epochs_input.setToolTip("Número de veces que el modelo verá el conjunto de datos completo.")
        config_layout.addWidget(self.dl_epochs_input, 2, 1)

        config_layout.addWidget(QLabel("Tamaño de Batch (Batch Size):"), 2, 2)
        self.dl_batch_size_input = QLineEdit("16") # Batch size más pequeño para DL
        self.dl_batch_size_input.setMaximumWidth(100)
        self.dl_batch_size_input.setToolTip("Número de muestras procesadas antes de actualizar el modelo.")
        config_layout.addWidget(self.dl_batch_size_input, 2, 3)
        
        # Podrían añadirse más hiperparámetros aquí (learning rate, etc.)

        self.btn_dl_train = QPushButton("🧠 Iniciar Entrenamiento Deep Learning")
        self.btn_dl_train.setObjectName("btn_dl_train")
        self.btn_dl_train.clicked.connect(self.start_dl_training)
        self.btn_dl_train.setEnabled(False)
        config_layout.addWidget(self.btn_dl_train, 3, 1, 1, 3, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(config_group)

    def create_dl_training_log(self, layout):
        log_group = QGroupBox("3. Registro y Progreso (Deep Learning)")
        log_layout = QVBoxLayout(log_group)

        self.dl_progress_bar = QProgressBar()
        self.dl_progress_bar.setVisible(False)
        self.dl_progress_bar.setTextVisible(True)
        log_layout.addWidget(self.dl_progress_bar)

        self.dl_training_log = QTextEdit()
        self.dl_training_log.setObjectName("dl_training_log")
        self.dl_training_log.setReadOnly(True)
        self.dl_training_log.setMinimumHeight(150)
        self.dl_training_log.setPlaceholderText("El progreso del entrenamiento Deep Learning aparecerá aquí...")
        log_layout.addWidget(self.dl_training_log)

        layout.addWidget(log_group)

    def create_models_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5)

        instructions = QLabel("""
        <b>Administra tus modelos entrenados.</b><br>
        Visualiza, carga para clasificación, obtén detalles o elimina modelos existentes. 
        Los modelos se guardan localmente en la carpeta designada.
        """)
        instructions.setWordWrap(True)
        instructions.setObjectName("models_instructions")
        instructions.setProperty("class", "InstructionLabel")
        layout.addWidget(instructions)
        
        self.create_models_list_section(layout)
        self.create_model_actions_section(layout)
        layout.addStretch()

    def create_save_model_section(self, layout): 
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
        list_group = QGroupBox("📋 Listado de Modelos Guardados")
        list_layout = QVBoxLayout(list_group)

        btn_refresh_layout = QHBoxLayout()
        self.btn_refresh_models = QPushButton("🔄 Actualizar Lista de Modelos")
        self.btn_refresh_models.clicked.connect(self.refresh_models_list)
        btn_refresh_layout.addWidget(self.btn_refresh_models)
        btn_refresh_layout.addStretch()
        list_layout.addLayout(btn_refresh_layout)

        self.models_table = QTableWidget()
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels([
            "Nombre del Modelo", "Tipo", "Categoría", "Profesiones", "Fecha de Creación", "Estado Actual"
        ])
        self.models_table.setObjectName("models_list_table")
        
        header = self.models_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) 
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive) # Permitir ajustar fecha
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents) 
        self.models_table.setColumnWidth(4, 150) # Ancho para fecha
        
        self.models_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.models_table.setAlternatingRowColors(True)
        self.models_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.models_table.setShowGrid(True) 
        self.models_table.selectionModel().selectionChanged.connect(self.on_model_selection_changed)
        self.models_table.setMinimumHeight(250)

        list_layout.addWidget(self.models_table)
        layout.addWidget(list_group)

    def create_model_actions_section(self, layout):
        actions_group = QGroupBox("⚡ Acciones para el Modelo Seleccionado")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setSpacing(10)

        self.btn_load_model = QPushButton("📂 Cargar para Clasificar")
        self.btn_load_model.setObjectName("btn_load_model")
        self.btn_load_model.clicked.connect(self.load_selected_model)
        self.btn_load_model.setEnabled(False)
        self.btn_load_model.setToolTip("Carga el modelo seleccionado en la pestaña 'Clasificar CV'.")

        self.btn_view_model_details = QPushButton("ℹ️ Ver Detalles del Modelo")
        self.btn_view_model_details.clicked.connect(self.view_model_details)
        self.btn_view_model_details.setEnabled(False)
        self.btn_view_model_details.setToolTip("Muestra información detallada sobre el modelo seleccionado.")


        self.btn_delete_model = QPushButton("🗑️ Eliminar Modelo")
        self.btn_delete_model.setObjectName("btn_delete_model")
        self.btn_delete_model.clicked.connect(self.delete_selected_model)
        self.btn_delete_model.setEnabled(False)
        self.btn_delete_model.setToolTip("Elimina permanentemente el archivo del modelo seleccionado.")


        actions_layout.addWidget(self.btn_load_model)
        actions_layout.addWidget(self.btn_view_model_details)
        actions_layout.addStretch() 
        actions_layout.addWidget(self.btn_delete_model)
        
        layout.addWidget(actions_group)

    def create_classification_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.create_model_status(layout)
        self.create_cv_selection(layout)
        self.create_results_section(layout)
        layout.addStretch()

    def create_model_status(self, layout):
        status_group = QGroupBox("1. Selección del Modelo para Clasificación")
        status_layout = QVBoxLayout(status_group)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Modelo a utilizar:"))
        self.model_selector_combo = QComboBox()
        self.model_selector_combo.setMinimumWidth(350)
        self.model_selector_combo.setToolTip("Selecciona un modelo entrenado de la lista.")
        self.model_selector_combo.currentTextChanged.connect(self.on_model_selector_changed)
        selector_layout.addWidget(self.model_selector_combo, 1)

        self.btn_load_selected_model = QPushButton("📂 Cargar Modelo Seleccionado")
        self.btn_load_selected_model.setObjectName("btn_load_selected_model")
        self.btn_load_selected_model.clicked.connect(self.load_model_from_selector)
        self.btn_load_selected_model.setEnabled(False)
        selector_layout.addWidget(self.btn_load_selected_model)

        self.btn_refresh_selector = QPushButton("🔄")
        self.btn_refresh_selector.setToolTip("Actualizar lista de modelos disponibles")
        self.btn_refresh_selector.clicked.connect(self.refresh_model_selector)
        self.btn_refresh_selector.setFixedWidth(40) # Botón más pequeño
        selector_layout.addWidget(self.btn_refresh_selector)
        status_layout.addLayout(selector_layout)

        self.model_status_label = QLabel("ⓘ Ningún modelo cargado actualmente. Selecciona y carga un modelo.")
        self.model_status_label.setObjectName("model_status_label")
        self.model_status_label.setWordWrap(True)
        status_layout.addWidget(self.model_status_label)

        self.model_info_text = QTextEdit()
        self.model_info_text.setObjectName("model_info_text")
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(100) # Reducir altura
        self.model_info_text.setPlaceholderText("Aquí se mostrarán los detalles del modelo cargado (tipo, profesiones, etc.).")
        status_layout.addWidget(self.model_info_text)

        layout.addWidget(status_group)
    
    def create_cv_selection(self, layout):
        cv_group = QGroupBox("2. Selección de CV y Clasificación")
        cv_layout = QGridLayout(cv_group) 
        cv_layout.setSpacing(10)

        cv_layout.addWidget(QLabel("Archivo de CV:"), 0, 0)
        self.selected_file_label = QLabel("Ningún archivo de CV ha sido seleccionado.")
        self.selected_file_label.setObjectName("selected_file_label")
        self.selected_file_label.setWordWrap(True)
        cv_layout.addWidget(self.selected_file_label, 0, 1, 1, 2) 

        self.btn_select_cv = QPushButton("📁 Examinar y Seleccionar Archivo CV")
        self.btn_select_cv.clicked.connect(self.select_cv_file)
        cv_layout.addWidget(self.btn_select_cv, 1, 1)
        
        self.btn_classify = QPushButton("Escanear CV")
        self.btn_classify.setObjectName("btn_classify")
        self.btn_classify.clicked.connect(self.classify_cv)
        self.btn_classify.setEnabled(False)
        self.btn_classify.setFixedSize(140, 140)  # Botón circular estilo Driver Booster
        cv_layout.addWidget(self.btn_classify, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(cv_group)

    def create_results_section(self, layout):
        results_group = QGroupBox("3. Resultados Detallados de la Clasificación")
        results_layout = QVBoxLayout(results_group)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("results_splitter")
        
        self.main_result = QTextEdit()
        self.main_result.setObjectName("main_result")
        self.main_result.setReadOnly(True)
        self.main_result.setPlaceholderText("La profesión predicha y la confianza del modelo aparecerán aquí después de la clasificación.")
        self.main_result.setMinimumHeight(150)
        splitter.addWidget(self.main_result)
        
        ranking_widget = QWidget() 
        ranking_layout = QVBoxLayout(ranking_widget)
        ranking_layout.setContentsMargins(0,0,0,0) # Sin márgenes para el widget interno
        
        ranking_label = QLabel("🏆 Ranking de Probabilidades por Profesión:")
        ranking_label.setStyleSheet("font-weight: 500; margin-bottom: 5px; font-size: 10pt;") # Medium weight
        ranking_layout.addWidget(ranking_label)

        self.ranking_table = QTableWidget()
        self.ranking_table.setObjectName("ranking_table_results")
        self.ranking_table.setColumnCount(2)
        self.ranking_table.setHorizontalHeaderLabels(["Profesión", "Probabilidad Estimada"])
        header = self.ranking_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.ranking_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ranking_table.setMinimumHeight(150)
        ranking_layout.addWidget(self.ranking_table)
        splitter.addWidget(ranking_widget)
        
        initial_width = self.width() if self.width() > 0 else 800 
        splitter.setSizes([int(initial_width * 0.55), int(initial_width * 0.45)]) # Ajustar proporciones
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
        list_widget.addItem(f"📁 {profession_name} ({len(valid_files)} CVs) -> {selected_folder}")
        
        name_input_widget.clear()
        if hasattr(self, selected_folder_attr_name):
            delattr(self, selected_folder_attr_name)
        btn_add.setEnabled(False)
        
        if btn_train_widget: 
             btn_train_widget.setEnabled(len(folders_dict) >= 2)

        QMessageBox.information(self, "Éxito", f"Profesión '{profession_name}' agregada con {len(valid_files)} CVs desde '{os.path.basename(selected_folder)}'.")


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
        reply = QMessageBox.question(self, "Confirmar Limpieza", 
                                     "¿Estás seguro de que quieres limpiar la lista de todas las profesiones y sus carpetas asociadas?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            folders_dict.clear()
            list_widget.clear()
            if btn_train_widget:
                btn_train_widget.setEnabled(False)
            QMessageBox.information(self, "Lista Limpiada", "Se han eliminado todas las profesiones de la lista.")


    def clear_professions(self):
        self.clear_professions_logic(self.profession_list, self.profession_folders, self.btn_train)
    
    def start_training(self):
        if len(self.profession_folders) < 2:
            QMessageBox.warning(self, "Datos Insuficientes", "Se necesitan al menos dos profesiones configuradas con CVs para iniciar el entrenamiento.")
            return

        model_name = self.training_model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Nombre Requerido", "Por favor, ingresa un nombre único y descriptivo para el modelo.")
            return
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre de Modelo Inválido", "El nombre del modelo solo puede contener letras, números, guiones (-) y guiones bajos (_).")
            return

        existing_models = self.classifier.list_available_models()
        if any(m['name'] == model_name and not m.get('is_deep_learning', False) for m in existing_models):
            reply = QMessageBox.question(self, 'Confirmar Sobrescritura',
                                       f'Ya existe un modelo tradicional con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo con un nuevo entrenamiento?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        prof_summary = "\n".join([f"  - {p} ({len(os.listdir(f))} CVs)" for p, f in self.profession_folders.items()])
        reply = QMessageBox.question(self, 'Confirmar Inicio de Entrenamiento',
                                   f'Se entrenará el modelo "{model_name}" con las siguientes profesiones:\n{prof_summary}\n\n'
                                   f'Algoritmo: {self.model_type_combo.currentText()}\n\n'
                                   'Este proceso puede tomar algunos minutos. ¿Deseas continuar?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_train.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) 
        self.training_log.clear()
        self.update_training_log(f"🚀 Iniciando entrenamiento del modelo '{model_name}' ({self.model_type_combo.currentText()})...")

        model_type = self.model_type_combo.currentData()

        self.training_thread = TrainingThread(self.profession_folders, model_type, model_name)
        self.training_thread.progress_updated.connect(self.update_training_log)
        self.training_thread.training_completed.connect(self.training_finished)
        self.training_thread.start()

    def update_training_log(self, message):
        self.training_log.append(f"[{QTime.currentTime().toString('hh:mm:ss.zzz')}] {message}")
        self.training_log.moveCursor(QTextCursor.MoveOperation.End)


    def training_finished(self, success, results, message):
        self.btn_train.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0,100) # Reset
        self.progress_bar.setValue(100 if success else 0)


        if success:
            accuracy_str = f"{results.get('accuracy', 0):.2%}" if results.get('accuracy') is not None else "N/A"
            model_name_trained = self.training_model_name_input.text().strip()
            results_summary = f"""
            <h4 style="color:#34A853;">✅ ¡Entrenamiento completado exitosamente!</h4>
            <p><b>Modelo:</b> {model_name_trained}</p>
            <p><b>Algoritmo:</b> {self.model_type_combo.currentText()}</p>
            <p><b>Precisión Estimada:</b> {accuracy_str}</p>
            <p><b>Profesiones Entrenadas:</b> {', '.join(results.get('classes', []))}</p>
            <p><b>Muestras Totales:</b> {results.get('train_samples', 'N/A')}</p>
            <p><i>El modelo ha sido guardado y está disponible para su uso.</i></p>
            """
            # Limpiar HTML para el log
            clean_summary = results_summary.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n').replace('<h4>', '').replace('</h4>', '').replace('<i>', '').replace('</i>', '').replace('<b>', '').replace('</b>', '')
            self.update_training_log(f"✅ Entrenamiento finalizado: {message}\n{clean_summary}") # Log sin HTML
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Entrenamiento Exitoso")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setTextFormat(Qt.TextFormat.RichText)
            msg_box.setText(results_summary)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            
            self.refresh_models_list()
            self.refresh_model_selector()
            
            if model_name_trained:
                self.current_loaded_model = model_name_trained
                self.current_model_is_dl = False 
                self.classifier.load_model(model_name_trained) 
                self.update_model_status_ui()
                self.update_classification_ui() 

            self.training_model_name_input.clear() 
            self.update_save_model_ui() 
        else:
            self.update_training_log(f"❌ Error Crítico en Entrenamiento: {message}")
            QMessageBox.critical(self, "Error en Entrenamiento", f"El entrenamiento del modelo falló:\n{message}\n\nPor favor, revisa el registro para más detalles y verifica la configuración de datos.")
        self.update_save_model_ui()


    def update_save_model_ui(self):
        is_model_ready_to_be_saved_separately = self.classifier.is_trained 
        
        if hasattr(self, 'btn_save_current_model'): # Botón no usado actualmente
            self.btn_save_current_model.setEnabled(is_model_ready_to_be_saved_separately)
        

    def save_current_model(self): 
        active_classifier = self.dl_classifier if self.current_model_is_dl and self.dl_classifier else self.classifier
        
        if not active_classifier or not active_classifier.is_trained:
            QMessageBox.warning(self, "Modelo No Disponible", "No hay un modelo activo y entrenado para guardar con otro nombre.")
            return

        # Este input no existe en la UI actual, sería para una función "Guardar como..."
        if not hasattr(self, 'model_name_input_for_save_as'): 
             QMessageBox.critical(self, "Error de Interfaz", "Funcionalidad 'Guardar Como' no completamente implementada.")
             return

        model_name = self.model_name_input_for_save_as.text().strip() 
        if not model_name:
            QMessageBox.warning(self, "Nombre Requerido", "Ingresa un nombre para guardar el modelo.")
            return
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre de Modelo Inválido", "El nombre solo puede contener letras, números, guiones y guiones bajos.")
            return

        existing_models = self.classifier.list_available_models() 
        if any(m['name'] == model_name and m.get('is_deep_learning', False) == self.current_model_is_dl for m in existing_models):
            reply = QMessageBox.question(self, 'Confirmar Sobrescritura',
                                       f'Ya existe un modelo de este tipo con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        try:
            success = active_classifier.save_model(model_name) # El clasificador activo guarda con el nuevo nombre
            if success:
                QMessageBox.information(self, "Modelo Guardado", f"El modelo activo se guardó exitosamente como '{model_name}'.")
                self.model_name_input_for_save_as.clear()
                self.refresh_models_list()
                self.refresh_model_selector() # Actualizar selector, podría estar cargado el nuevo
            else:
                QMessageBox.critical(self, "Error al Guardar", "No se pudo guardar el modelo con el nuevo nombre.")
        except Exception as e:
            QMessageBox.critical(self, "Excepción al Guardar", f"Ocurrió un error guardando el modelo:\n{str(e)}")


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
                category = "🧠 Deep Learning" if is_dl else "🤖 ML Clásico"
                category_item = QTableWidgetItem(category)
                self.models_table.setItem(row_position, 2, category_item)

                professions = model.get('professions', [])
                prof_text = ', '.join(professions[:3])
                if len(professions) > 3:
                    prof_text += f", ... (+{len(professions)-3})"
                elif not professions:
                    prof_text = "No definido"
                self.models_table.setItem(row_position, 3, QTableWidgetItem(prof_text))
                
                self.models_table.setItem(row_position, 4, QTableWidgetItem(model.get('creation_date', 'N/A')))

                is_current_loaded = (self.current_loaded_model == model['name'] and 
                                     self.current_model_is_dl == is_dl)
                status = "🟢 Cargado" if is_current_loaded else "⚪ Disponible"
                status_item = QTableWidgetItem(status)
                if is_current_loaded:
                    font = status_item.font()
                    font.setBold(True)
                    status_item.setFont(font)
                    status_item.setForeground(QColor(Settings.GOOGLE_GREEN if hasattr(Settings, 'GOOGLE_GREEN') else "#34A853"))
                self.models_table.setItem(row_position, 5, status_item)
                
                self.models_table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, model) 

        except Exception as e:
            QMessageBox.critical(self, "Error de Actualización", f"No se pudo actualizar la lista de modelos:\n{str(e)}")
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
            QMessageBox.warning(self, "Sin Selección de Modelo", "Por favor, selecciona un modelo de la tabla para cargar.")
            return
        
        self._load_model_by_data(model_data)

    def _load_model_by_data(self, model_data):
        model_name = model_data['name']
        is_deep_learning = model_data.get('is_deep_learning', False)
        display_name = model_data.get('display_name', model_name)
        
        try:
            classifier_to_use = None
            if is_deep_learning:
                if not DEEP_LEARNING_AVAILABLE or not self.dl_classifier:
                    QMessageBox.critical(self, "Error de Módulo", "El módulo de Deep Learning no está disponible o no se ha inicializado correctamente.")
                    return
                classifier_to_use = self.dl_classifier
            else:
                classifier_to_use = self.classifier

            success = classifier_to_use.load_model(model_name)
            if success:
                self.current_loaded_model = model_name
                self.current_model_is_dl = is_deep_learning
                QMessageBox.information(self, "Modelo Cargado Exitosamente", 
                                      f"El modelo '{display_name}' ha sido cargado y está listo para usarse en la pestaña 'Clasificar CV'.")
                self.update_all_ui_after_model_change()
            else:
                QMessageBox.critical(self, "Error al Cargar Modelo", f"No se pudo cargar el modelo '{display_name}'. Verifica la integridad del archivo del modelo.")
        except Exception as e:
            QMessageBox.critical(self, "Excepción al Cargar Modelo", f"Ocurrió un error inesperado al intentar cargar el modelo '{display_name}':\n{str(e)}")
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
            QMessageBox.warning(self, "Sin Selección de Modelo", "Por favor, selecciona un modelo de la tabla para eliminar.")
            return

        model_name = model_data['name']
        display_name = model_data.get('display_name', model_name)
        is_dl = model_data.get('is_deep_learning', False)
        model_type_str = "Deep Learning" if is_dl else "ML Clásico"

        reply = QMessageBox.question(self, 'Confirmar Eliminación Definitiva',
                                   f'¿Estás completamente seguro de que deseas eliminar el modelo {model_type_str} llamado "{display_name}"?\n\n'
                                   '¡ESTA ACCIÓN ES IRREVERSIBLE Y EL ARCHIVO DEL MODELO SE BORRARÁ PERMANENTEMENTE DEL DISCO!',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.classifier.delete_model(model_name, is_deep_learning=is_dl) # CVClassifier debe manejar la lógica de borrado
                if success:
                    QMessageBox.information(self, "Modelo Eliminado", 
                                          f"El modelo '{display_name}' ha sido eliminado exitosamente del sistema.")
                    if self.current_loaded_model == model_name and self.current_model_is_dl == is_dl:
                        self.current_loaded_model = None
                        self.current_model_is_dl = False
                        # Resetear el clasificador correspondiente
                        if is_dl and self.dl_classifier:
                            self.dl_classifier.model = None 
                            self.dl_classifier.is_trained = False
                        elif not is_dl and self.classifier:
                            self.classifier.model = None
                            self.classifier.is_trained = False
                    self.update_all_ui_after_model_change()
                else:
                    QMessageBox.critical(self, "Error al Eliminar", f"No se pudo eliminar el modelo '{display_name}'. Es posible que el archivo ya no exista o haya un problema de permisos.")
            except Exception as e:
                QMessageBox.critical(self, "Excepción al Eliminar", f"Ocurrió un error inesperado al eliminar el modelo:\n{str(e)}")

    def view_model_details(self):
        model_data = self.get_selected_model_data_from_table()
        if not model_data:
            QMessageBox.warning(self, "Sin Selección de Modelo", "Por favor, selecciona un modelo de la tabla para ver sus detalles.")
            return

        display_name = model_data.get('display_name', model_data['name'])
        is_dl = model_data.get('is_deep_learning', False)
        category_str = "🧠 Deep Learning" if is_dl else "🤖 Machine Learning Clásico"
        
        details_html = f"""
        <h3 style="color:{Settings.GOOGLE_BLUE if hasattr(Settings, 'GOOGLE_BLUE') else '#4285F4'};">Detalles del Modelo: {display_name}</h3>
        <table cellpadding='5' cellspacing='0' width='100%'>
            <tr><td width='150px'><b>Nombre Interno:</b></td><td>{model_data['name']}</td></tr>
            <tr><td><b>Categoría:</b></td><td>{category_str}</td></tr>
            <tr><td><b>Tipo de Algoritmo/Arq.:</b></td><td>{model_data.get('model_type', 'N/A')}</td></tr>
            <tr><td><b>Fecha de Creación:</b></td><td>{model_data.get('creation_date', 'N/A')}</td></tr>
            <tr><td><b>Número de Profesiones:</b></td><td>{len(model_data.get('professions',[]))}</td></tr>
        """
        
        professions = model_data.get('professions', [])
        if professions:
            details_html += "<tr><td valign='top'><b>Profesiones Entrenadas:</b></td><td><ul>"
            for prof in professions:
                details_html += f"<li>{prof}</li>"
            details_html += "</ul></td></tr>"
        else:
            details_html += "<tr><td><b>Profesiones:</b></td><td>No definidas o no disponibles.</td></tr>"

        if is_dl:
            details_html += f"<tr><td colspan='2'><h4 style='color:{Settings.GOOGLE_BLUE if hasattr(Settings, 'GOOGLE_BLUE') else '#4285F4'}; margin-top:10px;'>Parámetros de Deep Learning:</h4></td></tr>"
            details_html += f"<tr><td><b>Épocas Entrenadas:</b></td><td>{model_data.get('epochs_trained', 'N/A')}</td></tr>"
            details_html += f"<tr><td><b>Batch Size Usado:</b></td><td>{model_data.get('batch_size_trained', 'N/A')}</td></tr>"
            accuracy_val = model_data.get('accuracy')
            accuracy_display = f"{accuracy_val:.2%}" if isinstance(accuracy_val, float) else 'N/A'
            details_html += f"<tr><td><b>Precisión (Accuracy):</b></td><td>{accuracy_display}</td></tr>"
            details_html += f"<tr><td><b>Max. Longitud (Tokens):</b></td><td>{model_data.get('max_length', 'N/A')}</td></tr>"
        else: # ML Clásico
            details_html += f"<tr><td><b>Características Usadas:</b></td><td>{model_data.get('num_features', 'N/A')}</td></tr>"


        details_html += "</table>"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"Detalles del Modelo: {display_name}")
        msg_box.setTextFormat(Qt.TextFormat.RichText) 
        msg_box.setText(details_html)
        msg_box.setIcon(QMessageBox.Icon.Information) # Podría ser un icono personalizado
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # msg_box.setStyleSheet(self.styleSheet()) # Para que herede el estilo general
        msg_box.exec()

    # --- Métodos para Deep Learning (lógica) ---
    def select_dl_profession_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de CVs para Deep Learning")
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
            QMessageBox.critical(self, "Módulo No Disponible", "El módulo de Deep Learning no está habilitado o no se ha podido inicializar.")
            return
        if len(self.dl_profession_folders) < 2:
            QMessageBox.warning(self, "Datos Insuficientes", "Se necesitan al menos dos profesiones configuradas para entrenar un modelo de Deep Learning.")
            return

        model_name = self.dl_model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Nombre Requerido", "Por favor, ingresa un nombre único y descriptivo para el modelo de Deep Learning.")
            return
        if not model_name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Nombre de Modelo Inválido", "El nombre del modelo solo puede contener letras, números, guiones (-) y guiones bajos (_).")
            return
        
        existing_models = self.classifier.list_available_models() 
        if any(m['name'] == model_name and m.get('is_deep_learning', False) for m in existing_models):
            reply = QMessageBox.question(self, 'Confirmar Sobrescritura',
                                       f'Ya existe un modelo de Deep Learning con el nombre "{model_name}".\n'
                                       '¿Deseas sobrescribirlo con un nuevo entrenamiento?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            epochs = int(self.dl_epochs_input.text())
            batch_size = int(self.dl_batch_size_input.text())
            if epochs <= 0 or batch_size <= 0:
                raise ValueError("El número de épocas y el tamaño del batch deben ser enteros positivos.")
        except ValueError as e:
            QMessageBox.warning(self, "Parámetros de Entrenamiento Inválidos", str(e))
            return

        model_type = self.dl_model_type_combo.currentData()
        prof_summary_dl = "\n".join([f"  - {p} ({len(os.listdir(f))} CVs)" for p, f in self.dl_profession_folders.items()])

        reply = QMessageBox.question(self, 'Confirmar Inicio de Entrenamiento Deep Learning',
                                   f'Se entrenará el modelo de Deep Learning "{model_name}" ({self.dl_model_type_combo.currentText()}) con:\n'
                                   f'{prof_summary_dl}\n\n'
                                   f'Parámetros: {epochs} épocas, tamaño de batch {batch_size}.\n\n'
                                   f'⚠️ ADVERTENCIA: El entrenamiento de modelos Deep Learning puede ser intensivo en recursos y tomar un tiempo considerable (varios minutos a horas, dependiendo de los datos y hardware).\n\n'
                                   '¿Estás seguro de que deseas continuar?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_dl_train.setEnabled(False)
        self.dl_progress_bar.setVisible(True)
        self.dl_progress_bar.setRange(0, 0) # Modo indeterminado
        self.dl_training_log.clear()
        self.update_dl_training_log(f"🚀 Iniciando entrenamiento del modelo Deep Learning '{model_name}' ({self.dl_model_type_combo.currentText()})...")

        self.dl_training_thread = DeepLearningTrainingThread(
            self.dl_profession_folders, model_type, model_name, epochs, batch_size
        )
        self.dl_training_thread.progress_updated.connect(self.update_dl_training_log)
        self.dl_training_thread.training_completed.connect(self.dl_training_finished)
        self.dl_training_thread.start()

    def update_dl_training_log(self, message):
        self.dl_training_log.append(f"[{QTime.currentTime().toString('hh:mm:ss.zzz')}] {message}")
        self.dl_training_log.moveCursor(QTextCursor.MoveOperation.End)


    def dl_training_finished(self, success, results, message):
        self.btn_dl_train.setEnabled(True)
        self.dl_progress_bar.setVisible(False)
        self.dl_progress_bar.setRange(0,100)
        self.dl_progress_bar.setValue(100 if success else 0)

        if success:
            model_name_trained_dl = self.dl_model_name_input.text().strip()
            accuracy_dl_str = f"{results.get('accuracy', 0):.2%}" if results.get('accuracy') is not None else "N/A"
            epochs_trained_dl = results.get('epochs_trained', 'N/A')
            
            results_summary_dl = f"""
            <h4 style="color:#34A853;">✅ ¡Entrenamiento Deep Learning completado!</h4>
            <p><b>Modelo:</b> {model_name_trained_dl}</p>
            <p><b>Arquitectura:</b> {self.dl_model_type_combo.currentText()}</p>
            <p><b>Precisión Estimada:</b> {accuracy_dl_str}</p>
            <p><b>Épocas Entrenadas:</b> {epochs_trained_dl}</p>
            <p><b>Profesiones:</b> {', '.join(results.get('classes', []))}</p>
            <p><i>El modelo ha sido guardado y está disponible.</i></p>
            """
            # Limpiar HTML para el log DL
            clean_summary_dl = results_summary_dl.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n').replace('<h4>', '').replace('</h4>', '').replace('<i>', '').replace('</i>', '').replace('<b>', '').replace('</b>', '')
            self.update_dl_training_log(f"✅ Entrenamiento DL finalizado: {message}\n{clean_summary_dl}")

            msg_box_dl = QMessageBox(self)
            msg_box_dl.setWindowTitle("Entrenamiento Deep Learning Exitoso")
            msg_box_dl.setIcon(QMessageBox.Icon.Information)
            msg_box_dl.setTextFormat(Qt.TextFormat.RichText)
            msg_box_dl.setText(results_summary_dl)
            msg_box_dl.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box_dl.exec()
            
            self.refresh_models_list()
            self.refresh_model_selector()

            if model_name_trained_dl and self.dl_classifier:
                self.current_loaded_model = model_name_trained_dl
                self.current_model_is_dl = True
                self.dl_classifier.load_model(model_name_trained_dl)
                self.update_model_status_ui()
                self.update_classification_ui()

            self.dl_model_name_input.clear()
        else:
            self.update_dl_training_log(f"❌ Error Crítico en Entrenamiento DL: {message}")
            QMessageBox.critical(self, "Error en Entrenamiento Deep Learning", f"El entrenamiento del modelo Deep Learning falló:\n{message}\n\nRevisa el registro y la configuración.")
        self.update_save_model_ui()


    def refresh_model_selector(self): 
        try:
            models = self.classifier.list_available_models()
            self.model_selector_combo.clear()
            self.model_selector_combo.addItem("--- Selecciona un modelo ---", None) # Placeholder

            if not models:
                self.model_selector_combo.addItem("No hay modelos entrenados disponibles")
                self.btn_load_selected_model.setEnabled(False)
                return

            for model_data in models:
                is_dl = model_data.get('is_deep_learning', False)
                category_icon = "🧠" if is_dl else "🤖"
                display_name = model_data.get('display_name', model_data['name'])
                num_prof = len(model_data.get('professions', []))
                model_type_short = model_data.get('model_type', 'N/A').split('(')[0].strip()
                text = f"{category_icon} {display_name} ({model_type_short}, {num_prof} prof.)"
                self.model_selector_combo.addItem(text, model_data)

            # Habilitar botón de cargar si hay más que el placeholder
            self.btn_load_selected_model.setEnabled(self.model_selector_combo.count() > 1)


            if self.current_loaded_model:
                for i in range(self.model_selector_combo.count()):
                    item_data = self.model_selector_combo.itemData(i)
                    if (isinstance(item_data, dict) and 
                        item_data['name'] == self.current_loaded_model and
                        item_data.get('is_deep_learning', False) == self.current_model_is_dl):
                        self.model_selector_combo.setCurrentIndex(i)
                        break
            else: 
                 self.model_selector_combo.setCurrentIndex(0) # Seleccionar placeholder


        except Exception as e:
            QMessageBox.critical(self, "Error de Actualización", f"No se pudo actualizar el selector de modelos:\n{str(e)}")
            print(f"Error en refresh_model_selector: {e}")


    def on_model_selector_changed(self, index_or_text): # El argumento puede ser índice o texto
        current_data = self.model_selector_combo.currentData()
        self.btn_load_selected_model.setEnabled(isinstance(current_data, dict)) # Habilitar solo si hay datos de modelo


    def load_model_from_selector(self): 
        model_data = self.model_selector_combo.currentData()
        if not isinstance(model_data, dict): 
            QMessageBox.warning(self, "Selección Inválida", "Por favor, selecciona un modelo válido de la lista desplegable.")
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


            model_type_str = "Deep Learning" if self.current_model_is_dl else "ML Clásico"
            self.model_status_label.setText(f"<span style='color:{Settings.GOOGLE_GREEN if hasattr(Settings, 'GOOGLE_GREEN') else '#34A853'};'>🟢 Modelo {model_type_str} <b>'{model_name_display}'</b> cargado y listo para clasificar.</span>")

            if active_classifier and active_classifier.is_trained:
                model_info = active_classifier.get_model_info() if hasattr(active_classifier, 'get_model_info') else {}
                
                info_html = f"<b>Nombre:</b> {model_name_display}<br>"
                info_html += f"<b>Tipo:</b> {model_info.get('model_type', model_type_str)}<br>"
                professions = model_info.get('professions', [])
                prof_display_count = 4
                prof_text = ', '.join(professions[:prof_display_count])
                if len(professions) > prof_display_count:
                    prof_text += f", ... (+{len(professions)-prof_display_count} más)"
                info_html += f"<b>Profesiones ({len(professions)}):</b> {prof_text if professions else 'No definidas'}<br>"
                
                if self.current_model_is_dl:
                     info_html += f"<b>Max. Longitud (Tokens):</b> {model_info.get('max_length', 'N/A')}<br>"
                     accuracy_dl_info = model_info.get('accuracy')
                     accuracy_dl_info_str = f"{accuracy_dl_info:.2%}" if isinstance(accuracy_dl_info, float) else "N/A"
                     info_html += f"<b>Precisión (Entrenamiento):</b> {accuracy_dl_info_str}"

                else: # ML Clásico
                    info_html += f"<b>Características Usadas:</b> {model_info.get('num_features', 'N/A')}"


        else:
            self.model_status_label.setText(f"<span style='color:{Settings.GOOGLE_RED if hasattr(Settings, 'GOOGLE_RED') else '#EA4335'};'>🔴 Ningún modelo cargado.</span> Por favor, selecciona y carga un modelo de la lista superior o desde la pestaña 'Mis Modelos'.")
        
        self.model_info_text.setHtml(info_html if info_html else "Información del modelo no disponible.")
        self.update_classification_ui()


    def load_model_if_exists(self): 
        # Intenta cargar el primer modelo de la lista si no hay ninguno cargado.
        # Opcional: podrías guardar el último modelo usado en settings y cargarlo.
        if not self.current_loaded_model and self.model_selector_combo.count() > 1: # Más que el placeholder
            first_model_data = self.model_selector_combo.itemData(1) # El primer modelo real
            if isinstance(first_model_data, dict):
                print(f"Intentando cargar automáticamente el primer modelo: {first_model_data.get('display_name')}")
                self._load_model_by_data(first_model_data)
        
        self.update_model_status_ui() # Siempre actualizar UI
        self.update_classification_ui()


    def is_any_model_loaded_and_ready(self):
        if self.current_loaded_model:
            if self.current_model_is_dl:
                return self.dl_classifier and self.dl_classifier.is_trained
            else:
                return self.classifier and self.classifier.is_trained
        return False

    def update_classification_ui(self):
        ready_to_classify = self.is_any_model_loaded_and_ready() and hasattr(self, 'selected_cv_file') and self.selected_cv_file is not None
        self.btn_classify.setEnabled(ready_to_classify)


    def select_cv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de CV para clasificar", "",
            "Archivos de CV (*.pdf *.docx *.doc *.txt *.png *.jpg *.jpeg);;Documentos de Texto (*.txt);;Documentos PDF (*.pdf);;Documentos Word (*.docx *.doc);;Imágenes (*.png *.jpg *.jpeg);;Todos los Archivos (*)"
        )
        if file_path:
            if self.processor.is_supported_file(file_path):
                self.selected_cv_file = file_path
                self.selected_file_label.setText(f"<b>{os.path.basename(file_path)}</b><br><small>{file_path}</small>")
                self.selected_file_label.setStyleSheet(f"color: {Settings.GOOGLE_BLUE if hasattr(Settings, 'GOOGLE_BLUE') else '#4285F4'}; font-weight: normal; border: 1px solid {Settings.GOOGLE_BLUE if hasattr(Settings, 'GOOGLE_BLUE') else '#4285F4'}; background-color: #e8f0fe; padding: 5px; border-radius: 4px;") 
            else:
                QMessageBox.warning(self, "Formato de Archivo No Soportado", 
                                  "El archivo seleccionado no tiene un formato de CV que la aplicación pueda procesar (se admiten: pdf, docx, doc, txt, png, jpg, jpeg).")
                self.selected_file_label.setText("Formato de archivo no soportado. Intenta con otro.")
                self.selected_file_label.setStyleSheet(f"color: {Settings.GOOGLE_RED if hasattr(Settings, 'GOOGLE_RED') else '#EA4335'}; font-weight: bold; border: 1px solid {Settings.GOOGLE_RED if hasattr(Settings, 'GOOGLE_RED') else '#EA4335'}; background-color: #fce8e6; padding: 5px; border-radius: 4px;")
                self.selected_cv_file = None # Resetear
            self.update_classification_ui()
        else: # Si el usuario cancela el diálogo
            # self.selected_file_label.setText("Ningún archivo de CV ha sido seleccionado.")
            # self.selected_file_label.setStyleSheet(f"color: {Settings.GREY_700 if hasattr(Settings, 'GREY_700') else '#5f6368'}; border: 1px dashed {Settings.GREY_400 if hasattr(Settings, 'GREY_400') else '#bdc1c6'}; background-color: {Settings.GREY_50 if hasattr(Settings, 'GREY_50') else '#f8f9fa'}; padding: 5px; border-radius: 4px;")
            # self.selected_cv_file = None
            self.update_classification_ui()


    def classify_cv(self):
        if not self.is_any_model_loaded_and_ready():
            QMessageBox.warning(self, "Modelo No Cargado o No Listo", "Asegúrate de que un modelo esté cargado y listo para usar antes de intentar clasificar un CV.")
            return
        if not hasattr(self, 'selected_cv_file') or not self.selected_cv_file:
            QMessageBox.warning(self, "Archivo CV No Seleccionado", "Por favor, selecciona un archivo de CV para proceder con la clasificación.")
            return

        active_classifier = self.dl_classifier if self.current_model_is_dl else self.classifier
        model_type_str = "Deep Learning" if self.current_model_is_dl else "ML Clásico"
        model_name_display = self.current_loaded_model # Usar el nombre interno para el log

        try:
            self.main_result.setHtml(f"<p>🔄 Procesando archivo CV: <b>{os.path.basename(self.selected_cv_file)}</b>...</p>")
            QApplication.processEvents() # Forzar actualización de UI

            raw_text = self.processor.extract_text_from_file(self.selected_cv_file)
            if raw_text is None or not raw_text.strip(): # Verificar si la extracción falló o resultó en texto vacío
                 QMessageBox.critical(self, "Error de Extracción de Texto", f"No se pudo extraer contenido textual del archivo '{os.path.basename(self.selected_cv_file)}'. El archivo podría estar dañado, protegido, ser una imagen sin OCR o no ser un formato soportado para extracción de texto.")
                 self.main_result.append("<p style='color:red;'>❌ Error: No se pudo extraer texto del CV.</p>")
                 return

            clean_text = self.processor.clean_text(raw_text)

            if not clean_text.strip(): 
                QMessageBox.warning(self, "Contenido Vacío o No Útil", "Después del preprocesamiento, no se encontró texto útil en el CV. El CV podría estar vacío o contener solo elementos no textuales.")
                self.main_result.append("<p style='color:orange;'>⚠️ Advertencia: No se encontró texto útil en el CV después del preprocesamiento.</p>")
                return

            self.main_result.append(f"<p>🤖 Clasificando usando el modelo {model_type_str} (<b>{model_name_display}</b>)...</p>")
            QApplication.processEvents()
            
            prediction_result = active_classifier.predict_cv(clean_text)

            if prediction_result.get('error', False):
                error_msg = prediction_result.get('message', 'Ocurrió un error desconocido durante la clasificación.')
                QMessageBox.critical(self, "Error de Clasificación", error_msg)
                self.main_result.append(f"<p style='color:red;'>❌ Error en clasificación: {error_msg}</p>")
                return

            predicted_profession = prediction_result.get('predicted_profession', 'Indeterminada')
            confidence = prediction_result.get('confidence', 0.0)
            confidence_percentage = f"{confidence:.1%}" if isinstance(confidence, (float, int)) else "N/A"
            confidence_level = prediction_result.get('confidence_level', 'Desconocida')
            interpretation = prediction_result.get('interpretation', 'No hay una interpretación detallada disponible.')

            # Determinar color basado en confianza (ejemplo)
            conf_color_style = "color: #202124;" # Default (negro/gris oscuro)
            if confidence_level == "Alta": conf_color_style = f"color: {Settings.GOOGLE_GREEN if hasattr(Settings, 'GOOGLE_GREEN') else '#34A853'}; font-weight: bold;"
            elif confidence_level == "Media": conf_color_style = f"color: {Settings.GOOGLE_YELLOW_DARK if hasattr(Settings, 'GOOGLE_YELLOW_DARK') else '#F9AB00'}; font-weight: bold;" # Amarillo oscuro para texto
            elif confidence_level == "Baja": conf_color_style = f"color: {Settings.GOOGLE_RED if hasattr(Settings, 'GOOGLE_RED') else '#EA4335'}; font-weight: bold;"


            main_html = f"""
            <h3 style="color:{Settings.GOOGLE_BLUE if hasattr(Settings, 'GOOGLE_BLUE') else '#4285F4'}; margin-bottom: 10px;">Resultado de Clasificación del CV</h3>
            <p><b>Archivo Analizado:</b> {os.path.basename(self.selected_cv_file)}</p>
            <hr style="border:none; border-top: 1px solid #dadce0; margin: 10px 0;">
            <p style="font-size: 13pt;"><b>Profesión Predicha: <span style="color:{Settings.GOOGLE_BLUE if hasattr(Settings, 'GOOGLE_BLUE') else '#4285F4'};">{predicted_profession}</span></b></p>
            <p><b>Confianza del Modelo:</b> <span style='{conf_color_style}'>{confidence_percentage} ({confidence_level})</span></p>
            <p style="margin-top: 8px;"><b>Interpretación Sugerida:</b><br>{interpretation}</p>
            """
            self.main_result.setHtml(main_html)

            self.ranking_table.setRowCount(0) 
            profession_ranking = prediction_result.get('profession_ranking', [])
            for i, rank_data in enumerate(profession_ranking):
                self.ranking_table.insertRow(i)
                item_prof = QTableWidgetItem(rank_data['profession'])
                item_perc_val = rank_data.get('probability', 0.0) # Asumir que el backend devuelve 'probability'
                item_perc_str = f"{item_perc_val:.1%}" if isinstance(item_perc_val, float) else rank_data.get('percentage', 'N/A')
                
                item_perc = QTableWidgetItem(item_perc_str)
                item_perc.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.ranking_table.setItem(i, 0, item_prof)
                self.ranking_table.setItem(i, 1, item_perc)
                
                if rank_data['profession'] == predicted_profession:
                    font = item_prof.font(); font.setBold(True); item_prof.setFont(font)
                    fontp = item_perc.font(); fontp.setBold(True); item_perc.setFont(fontp)
                    
                    # Color de fondo sutil para la fila principal
                    # Determinar el color de fondo basado en la confianza, pero más claro
                    bg_color_qcolor = QColor(Settings.GOOGLE_GREEN if hasattr(Settings, 'GOOGLE_GREEN') else '#34A853')
                    if confidence_level == "Media": bg_color_qcolor = QColor(Settings.GOOGLE_YELLOW if hasattr(Settings, 'GOOGLE_YELLOW') else '#FBBC05')
                    elif confidence_level == "Baja": bg_color_qcolor = QColor(Settings.GOOGLE_RED if hasattr(Settings, 'GOOGLE_RED') else '#EA4335')
                    
                    # Hacer el color de fondo mucho más claro para la tabla
                    highlight_bg = bg_color_qcolor.lighter(180) if confidence_level != "Media" else QColor("#fff8e1") # Amarillo muy claro

                    item_prof.setBackground(highlight_bg)
                    item_perc.setBackground(highlight_bg)


        except Exception as e:
            detailed_error = f"Ocurrió un error crítico durante el proceso de clasificación:\n{str(e)}"
            QMessageBox.critical(self, "Error Crítico en Clasificación", detailed_error)
            self.main_result.setHtml(f"<p style='color:red;'>❌ Error crítico: {detailed_error}</p>")
            import traceback
            print(f"Error en classify_cv: {e}\n{traceback.format_exc()}")


def main():
    app = QApplication(sys.argv)
    # app.setApplicationName("Clasificador de CVs por Profesiones v2.1") # El título se pone en CustomTitleBar

    # Cargar fuentes de Google (Roboto) si están disponibles, o usar Segoe UI como fallback
    # Esto es conceptual, PyQt no carga fuentes web directamente. Deben estar instaladas.
    font_id = QFontDatabase.addApplicationFont(":/fonts/Roboto-Regular.ttf") # Asumiendo que tienes Roboto en recursos Qt
    if font_id != -1:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            default_font = QFont(font_families[0], 10)
            app.setFont(default_font)
    else: # Fallback
        default_font = QFont("Segoe UI", 10) 
        app.setFont(default_font)


    window = CVClassifierGUI()
    window.show()

    # No mostrar mensaje de bienvenida intrusivo, la UI debe ser autoexplicativa
    # QTimer.singleShot(200, lambda: show_welcome_message(window))

    sys.exit(app.exec())

# La función show_welcome_message puede eliminarse o rediseñarse si es necesaria
# def show_welcome_message(parent_window):
# ... (contenido anterior)


if __name__ == "__main__":
    # --- Stubs para ejecución independiente (sin cambios) ---
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
    def extract_text_from_file(self, file_path):
        if not os.path.exists(file_path): return None
        # Simular que algunos archivos no tienen texto extraíble
        if "empty" in os.path.basename(file_path): return ""
        if "image_only" in os.path.basename(file_path): return " " # Texto no útil
        return f'Contenido extraído de {os.path.basename(file_path)} para pruebas. Esto debería ser el texto real del CV.'
    def clean_text(self, text): return text.lower().strip().replace('\\n', ' ')
""")

    if not os.path.exists("src/config/settings.py"):
        with open("src/config/settings.py", "w", encoding="utf-8") as f:
            f.write("""
class Settings:
    MODEL_DIR = "cv_models_storage_" 
    # Colores inspirados en Driver Booster
    GOOGLE_BLUE = "#D1001F"
    GOOGLE_GREEN = "#4CAF50"
    GOOGLE_YELLOW = "#FFCA28"
    GOOGLE_YELLOW_DARK = "#FFA000"
    GOOGLE_RED = "#EF5350"
    GREY_900 = "#FFFFFF"
    GREY_700 = "#BDBDBD"
    GREY_400 = "#616161"
    GREY_100 = "#212121"
    GREY_50 = "#121212"
""")
    # Crear directorio de modelos si no existe
    # Esto debe hacerse después de que Settings se haya importado y MODEL_DIR esté definido
    # Lo muevo a después de la importación de Settings en el script principal de la GUI si es necesario
    # o asegurarse de que Settings.MODEL_DIR se evalúe correctamente aquí.
    # Para el stub, lo creo directamente.
    if not os.path.exists("cv_models_storage_"):
        os.makedirs("cv_models_storage_", exist_ok=True)


    if not os.path.exists("src/models/cv_classifier.py"):
        with open("src/models/cv_classifier.py", "w", encoding="utf-8") as f:
            f.write("""
import os, json, datetime
from src.config.settings import Settings
class CVClassifier:
    def __init__(self): self.is_trained = False; self.model = None; self.professions = []; self.model_type = "N/A"; self.num_features = 0
    def train_model(self, data, model_type):
        self.is_trained = True; self.professions = sorted(list(set(d['profession'] for d in data))); self.model_type = model_type
        self.num_features = 120 # Placeholder
        return {'accuracy': 0.88, 'train_samples': len(data), 'test_samples': 0, 'features': self.num_features, 'classes': self.professions}
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
            if metadata.get('is_deep_learning', False): return False 
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
                if metadata.get('is_deep_learning', False) == is_deep_learning: 
                    os.remove(path); return True
            except: pass 
        return False
    def predict_cv(self, text):
        if not self.is_trained or not self.professions: return {'error': True, 'message': 'Modelo no entrenado o sin profesiones definidas.'}
        # Simular una predicción más variada
        idx = len(text) % len(self.professions) if self.professions else 0
        pred_prof = self.professions[idx] if self.professions else "Desconocido"
        confidence = ( (len(text) % 50) + 50) / 100.0 # Entre 0.5 y 0.99
        confidence_level = "Alta" if confidence > 0.85 else ("Media" if confidence > 0.65 else "Baja")
        interpretation = f"El análisis sugiere que el CV podría corresponder a la profesión de {pred_prof} con una confianza {confidence_level.lower()}."
        ranking = []
        for i, p in enumerate(self.professions):
            prob = confidence / (i + 1) if p == pred_prof else (1.0 - confidence) / (len(self.professions) or 1)
            ranking.append({'profession': p, 'probability': max(0.01, min(0.99, prob + ( (i*len(text))%10 - 5)/100.0 )) }) # Añadir algo de ruido
        
        # Asegurar que la suma no exceda 1 (muy simplificado)
        # total_prob = sum(r['probability'] for r in ranking)
        # if total_prob > 1.0:
        #    ranking = [{'profession': r['profession'], 'probability': r['probability']/total_prob} for r in ranking]

        return {'error': False, 'predicted_profession': pred_prof, 'confidence': confidence, 
                'confidence_level': confidence_level, 
                'interpretation': interpretation,
                'profession_ranking': sorted(ranking, key=lambda x: x['probability'], reverse=True)}
    def get_model_info(self):
        if not self.is_trained: return {}
        return {'model_type': self.model_type, 'professions': self.professions, 
                'num_professions': len(self.professions), 'num_features': self.num_features,
                'is_deep_learning': False}
""")

    if DEEP_LEARNING_AVAILABLE and not os.path.exists("src/models/deep_learning_classifier.py"):
       with open("src/models/deep_learning_classifier.py", "w", encoding="utf-8") as f:
            f.write("""
from src.models.cv_classifier import CVClassifier 
import os, json, datetime
from src.config.settings import Settings

class DeepLearningClassifier(CVClassifier): 
    def __init__(self):
        super().__init__() 
        self.model_type_dl = "BERT" 
        self.max_length = 512
        self.epochs_trained = 0
        self.batch_size_trained = 0
        self.accuracy = 0.0

    def train_model(self, data, model_type='bert', epochs=3, batch_size=8): # Default a BERT y menos épocas/batch
        self.is_trained = True
        self.professions = sorted(list(set(d['profession'] for d in data)))
        self.model_type_dl = model_type.upper()
        self.epochs_trained = epochs
        self.batch_size_trained = batch_size
        self.accuracy = 0.85 # Placeholder para DL
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
            if not metadata.get('is_deep_learning'): return False 
            self.professions = metadata.get('professions', [])
            self.model_type_dl = metadata.get('model_type', 'BERT')
            self.max_length = metadata.get('max_length', 512)
            self.epochs_trained = metadata.get('epochs_trained', 0)
            self.batch_size_trained = metadata.get('batch_size_trained', 0)
            self.accuracy = metadata.get('accuracy', 0.0)
            self.is_trained = True
            return True
        return False

    def predict_cv(self, text):
        if not self.is_trained or not self.professions: return {'error': True, 'message': 'Modelo Deep Learning no entrenado o sin profesiones.'}
        idx = len(text) % len(self.professions) if self.professions else 0
        pred_prof = self.professions[idx] if self.professions else "Desconocido (DL)"
        confidence = ( (len(text) % 40) + 60) / 100.0 # Entre 0.6 y 0.99 para DL
        confidence_level = "Alta" if confidence > 0.88 else ("Media" if confidence > 0.70 else "Baja")
        interpretation = f"El análisis profundo del CV sugiere una correspondencia con {pred_prof} (confianza {confidence_level.lower()})."
        
        ranking = []
        for i, p in enumerate(self.professions):
            prob = confidence / (i*0.5 + 1) if p == pred_prof else (1.0 - confidence) / (len(self.professions) or 1)
            ranking.append({'profession': p, 'probability': max(0.01, min(0.99, prob + ( (i*len(text))%10 - 5)/150.0 )) })
        
        return {'error': False, 'predicted_profession': pred_prof, 'confidence': confidence, 
                'confidence_level': confidence_level, 
                'interpretation': interpretation,
                'profession_ranking': sorted(ranking, key=lambda x: x['probability'], reverse=True)}

    def get_model_info(self): 
        if not self.is_trained: return {}
        return {'model_type': self.model_type_dl, 'professions': self.professions, 
                'num_professions': len(self.professions), 'num_features': 'N/A (Embeddings)',
                'max_length': self.max_length, 'is_deep_learning': True,
                'epochs_trained': self.epochs_trained, 'batch_size_trained': self.batch_size_trained,
                'accuracy': self.accuracy}
""")
    from PyQt6.QtGui import QFontDatabase # Para cargar fuentes
    sys.exit(main())
