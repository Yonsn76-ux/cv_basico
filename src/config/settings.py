"""
Configuraciones del CV Classifier v2.0
"""

import os
from pathlib import Path

class Settings:
    """Configuraciones centralizadas del sistema"""
    
    # Directorios principales
    BASE_DIR = Path(__file__).parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    DEEP_MODELS_DIR = BASE_DIR / "deep_models"
    DOCS_DIR = BASE_DIR / "docs"
    TESTS_DIR = BASE_DIR / "tests"
    
    # Datos de ejemplo
    SAMPLE_CVS_DIR = DATA_DIR / "sample_cvs"
    
    # Configuración de modelos tradicionales
    ML_CONFIG = {
        'default_model_type': 'random_forest',
        'available_models': [
            'random_forest',
            'logistic_regression', 
            'svm',
            'naive_bayes'
        ],
        'model_descriptions': {
            'random_forest': 'Random Forest (Recomendado)',
            'logistic_regression': 'Logistic Regression',
            'svm': 'Support Vector Machine (SVM)',
            'naive_bayes': 'Naive Bayes'
        }
    }
    
    # Configuración de Deep Learning
    DL_CONFIG = {
        'default_model_type': 'lstm',
        'available_models': [
            'lstm',
            'cnn',
            'bert'
        ],
        'model_descriptions': {
            'lstm': 'LSTM (Long Short-Term Memory)',
            'cnn': 'CNN (Convolutional Neural Network)',
            'bert': 'BERT (Transformer)'
        },
        'default_epochs': 10,
        'default_batch_size': 32,
        'max_length': 512,
        'vocab_size': 10000,
        'embedding_dim': 128
    }
    
    # Configuración de procesamiento de CVs
    CV_PROCESSING = {
        'supported_formats': ['.pdf', '.docx', '.txt', '.doc'],
        'max_file_size_mb': 10,
        'encoding': 'utf-8'
    }
    
    # Configuración de la GUI
    GUI_CONFIG = {
        'window_title': '🎯 Clasificador de CVs por Profesiones v2.0',
        'window_size': (1200, 800),
        'min_window_size': (900, 600),
        'theme': 'default'
    }
    
    # Configuración de logging
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '[%(asctime)s] %(levelname)s: %(message)s',
        'date_format': '%H:%M:%S'
    }
    
    @classmethod
    def ensure_directories(cls):
        """Crea los directorios necesarios si no existen"""
        directories = [
            cls.DATA_DIR,
            cls.MODELS_DIR,
            cls.DEEP_MODELS_DIR,
            cls.DOCS_DIR,
            cls.TESTS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name, model_type='traditional'):
        """Obtiene la ruta para un modelo específico"""
        if model_type == 'deep_learning':
            return cls.DEEP_MODELS_DIR / model_name
        else:
            return cls.MODELS_DIR / f"{model_name}.pkl"
    
    @classmethod
    def get_sample_cvs_path(cls):
        """Obtiene la ruta de los CVs de ejemplo"""
        return cls.SAMPLE_CVS_DIR
    
    @classmethod
    def is_supported_file(cls, file_path):
        """Verifica si un archivo es soportado"""
        return Path(file_path).suffix.lower() in cls.CV_PROCESSING['supported_formats']
