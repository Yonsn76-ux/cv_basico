import os
import argparse
from src.utils.cv_processor import CVProcessor
from src.models.cv_classifier import CVClassifier


def load_cvs(data_dir):
    """Carga y procesa CVs desde subcarpetas por profesión."""
    processor = CVProcessor(skill_keywords=[])  # sin keywords de habilidades
    all_data = []
    for profession in os.listdir(data_dir):
        prof_path = os.path.join(data_dir, profession)
        if os.path.isdir(prof_path):
            results = processor.process_cv_folder(prof_path, profession)
            all_data.extend(results)
    return all_data


def main():
    parser = argparse.ArgumentParser(description="Entrena un clasificador de CVs")
    parser.add_argument("data_dir", help="Directorio con subcarpetas de CVs por profesion")
    parser.add_argument("--model-name", default="cv_classifier", help="Nombre del modelo a guardar")
    parser.add_argument("--model-type", default="random_forest",
                        choices=["random_forest", "logistic_regression", "svm", "naive_bayes"],
                        help="Algoritmo de clasificacion")
    args = parser.parse_args()

    cv_data = load_cvs(args.data_dir)
    if not cv_data:
        print("No se encontraron CVs para entrenar")
        return

    classifier = CVClassifier()
    classifier.train_model(cv_data, model_type=args.model_type)
    classifier.save_model(args.model_name)
    print("Modelo guardado correctamente")


if __name__ == "__main__":
    main()
