from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

from src.utils.cv_processor import CVProcessor
from src.models.cv_classifier import CVClassifier

app = Flask(__name__)
app.secret_key = "cv-classifier-secret"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cargar modelo por defecto si existe
MODEL_NAME = 'cv_classifier'
classifier = CVClassifier()
model_loaded = classifier.load_model(MODEL_NAME)

@app.route('/')
def index():
    return render_template('index.html', model_loaded=model_loaded)

@app.route('/classify', methods=['POST'])
def classify():
    if 'cv_file' not in request.files:
        flash('No se ha seleccionado archivo')
        return redirect(url_for('index'))

    file = request.files['cv_file']
    if file.filename == '':
        flash('Nombre de archivo vacío')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    processor = CVProcessor()
    text = processor.extract_text_from_file(file_path)
    text = processor.clean_text(text)

    if not model_loaded:
        flash('No hay modelo cargado. Entrena uno y colócalo en la carpeta models.')
        return redirect(url_for('index'))

    result = classifier.predict_cv(text)
    profession = result.get('predicted_profession', 'N/A')
    confidence = result.get('confidence_percentage', '0%')
    ranking = result.get('profession_ranking', [])
    return render_template('result.html', profession=profession,
                           confidence=confidence, ranking=ranking)

if __name__ == '__main__':
    app.run(debug=True)
