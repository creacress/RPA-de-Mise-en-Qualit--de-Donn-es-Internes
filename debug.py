import logging
from logging.handlers import RotatingFileHandler
import datetime
from selenium import webdriver
import os

# Configuration du Logger
def setup_logger():
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        # Reglage du niveau de logging pour capturer tous les messages
        logger.setLevel(logging.DEBUG)

        # Empêche la propagation au logger parent
        logger.propagate = False

        # Créer un gestionnaire de fichier log avec rotation
        file_handler = RotatingFileHandler('activity_1.log', maxBytes=5000000, backupCount=5, encoding='utf-8')

        # Format du message log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # Ajout du format au gestionnaire de log
        file_handler.setFormatter(formatter)

        # Ajout du gestionnaire de log au logger
        logger.addHandler(file_handler)
    return logger

# Initialisation du logger
logger = setup_logger()

# Fonction pour enregistrer les erreurs et capturer les screenshots
def log_error_and_capture_screenshot(driver: webdriver, contrat_numero, error):
    # Timestamp pour le nom de fichier unique
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f"screenshots/error_{contrat_numero}_{timestamp}.png"
    
    # Créer le dossier pour les captures d'ecran si nécessaire
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Sauvegarder la capture d'ecran
    driver.save_screenshot(screenshot_file)

    # Enregistrement de l'erreur dans le fichier log
    logger.error(f"Erreur dans le contrat numero {contrat_numero}: {error}, Screenshot: {screenshot_file}")
