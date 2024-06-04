import os
import json
import copy
import traceback
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from affranchigo_forfait_case import AffranchigoForfaitCase

from affranchigo_lib_case import AffranchigoLibCase

from destineo_case import destineoCase

from frequenceo_case import FrequenceoCase

from proxicompte_case import ProxicompteCase

from collecte_remise import CollecteRemise

from debug import log_error_and_capture_screenshot, setup_logger

from data_processing import extract_contrat_numbers_to_json

# Initatilisation du debug 
logger = setup_logger()
# Charge les variables d'env si necessaire
load_dotenv()

# Acceder aux variables
identifiant = os.getenv("IDENTIFIANT")
mot_de_passe = os.getenv("MOT_DE_PASSE")


def configure_selenium():
    logger.info("Configuration de Selenium...")
    service = Service("data/msedgedriver.exe")
    driver = webdriver.Edge(service=service)
    driver.get(
        "https://www.exemple.intranet.fr"
    )
    wait = WebDriverWait(driver, 3)
    return driver, wait

def handle_first_modal(driver):
    modal_elements = driver.find_elements(By.NAME, "OK")
    if modal_elements:
        modal_elements[0].click()
        logger.info("Premiere Modale Geree")
    else:
        logger.info("La premiere modale n'est pas apparue.")

def handle_second_modal(driver):
    modal_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "div.bootbox.modal.fade.bootbox-alert.in div.modal-footer button",
    )
    if modal_elements:
        modal_elements[0].click()
        logger.info("Deuxieme Modale Geree")
    else:
        logger.info("La deuxieme modale n'est pas apparue.")

def handle_permission_modal(driver, wait ):
    modal_elements = driver.find_elements(
        By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"
    )
    if modal_elements:
        modal_elements[0].click()
        logger.info("Modale Permission geree.")
        driver.get(
        "https://www.exemple.intranet.fr"
    )
        process_contract(driver, wait)

def handle_api_modal(driver, wait):
    modal_elements = driver.find_elements(
        By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"
    )
    if modal_elements:
        modal_elements[0].click()
        logger.info("Modale API geree.")
        driver.get(
        "https://www.exemple.intranet.fr"
    )
        process_contract(driver, wait)

def handle_modification_modal(driver, wait):
    try:
        # XPath pour trouver le bouton "Valider"
        valider_button_xpath = "swal2-confirm.swal2-styled.swal2-default-outline"
        
        # Attendre que le bouton soit cliquable
        valider_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, valider_button_xpath))
        )

        # Cliquer sur le bouton "Valider"
        valider_button.click()
        logger.info("Le bouton 'Valider' de la modale de modification a ete clique.")
    except TimeoutException:
        logger.info("La modale de modification n'est pas apparue.")
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la modale de modification: {e}")

def login(driver, wait):
    logger.debug("Tentative de connexion...")

    try:
        input_identifiant = wait.until(
            EC.presence_of_element_located((By.ID, "AUTHENTICATION.LOGIN"))
        )
        input_identifiant.clear()
        input_identifiant.send_keys(identifiant)
        input_identifiant.send_keys(Keys.RETURN)

        input_mot_de_passe = wait.until(
            EC.presence_of_element_located((By.ID, "AUTHENTICATION.PASSWORD"))
        )
        input_mot_de_passe.clear()
        input_mot_de_passe.send_keys(mot_de_passe)
        input_mot_de_passe.send_keys(Keys.RETURN)
    except TimeoutException:
        logger.info("Dejà connecte ou le champ d'identifiant n'est pas present.")
    except Exception as e:    
        log_error_and_capture_screenshot(driver, "Probleme Login", e)

def process_json_files(file_path):
    logger.info("Traitement du fichier JSON pour les contrats...")
    numeros_contrat = []

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            numeros_contrat = list(data.values())

    return numeros_contrat

def submit_contract_number(driver, wait, numero):
    logger.info(f"Soumission du numero de contrat {numero}...")
    input_element = wait.until(EC.presence_of_element_located((By.ID, "idContrat")))
    input_element.clear()
    input_element.send_keys(numero)
    input_element.send_keys(Keys.RETURN)

    submit_button = wait.until(
        EC.element_to_be_clickable((By.ID, "btnSubmitContrat_accesRDC"))
    )
    submit_button.click()

    try:
        # Essaie de gerer la premiere modale avec le bouton nomme "OK"
        modal_button_ok = wait.until(EC.element_to_be_clickable((By.NAME, "OK")))
        modal_button_ok.click()
        logger.info("Premiere modale geree.")
    except TimeoutException:
        logger.info("Pas de premiere modale à gerer.")
    except Exception as e:
        log_error_and_capture_screenshot(driver, "Submit_contrat", e)

    try:
        # Essaie de gerer la deuxieme modale avec le selecteur CSS specifique
        modal_button_selector = "body > div.bootbox.modal.fade.bootbox-alert.in > div > div > div.modal-footer > button"
        modal_button_css = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, modal_button_selector))
        )
        modal_button_css.click()
        logger.info("Deuxieme modale geree.")
    except TimeoutException:
        logger.info("Pas de deuxieme modale à gerer.")

        # Attendre la visibilite de l'element avec l'ID 'modalRefContrat'
        wait.until(EC.visibility_of_element_located((By.ID, "modalRefContrat")))

def save_processed_contracts(contrats):
    """Enregistre les numeros de contrats traites dans un fichier JSON."""
    file_path = "numeros_contrat_traites_cas_4.json"
    try:
        # Lecture du fichier existant et ajout des nouveaux contrats
        with open(file_path, "r+") as file:
            existing_data = json.load(file)
            updated_data = existing_data + [
                c for c in contrats if c not in existing_data
            ]
            file.seek(0)
            json.dump(updated_data, file)
    except FileNotFoundError:
        # Creation d'un nouveau fichier si celui-ci n'existe pas
        with open(file_path, "w") as file:
            json.dump(contrats, file)

def save_non_modifiable_contract(contrat_number):
    """Enregistre le numéro de contrat dans un fichier JSON en évitant les doublons."""
    file_path = "non_modifiable_cas_4.json"
    data = set()  # Utiliser un ensemble pour éviter les doublons

    try:
        # Essaye de lire le fichier existant pour récupérer les numéros de contrats
        with open(file_path, "r") as file:
            existing_data = json.load(file)
            data.update(existing_data)  # Mise à jour de l'ensemble avec les données existantes
    except FileNotFoundError:
        logger.info("Le fichier n'existe pas, il sera créé.")
    except json.JSONDecodeError:
        logger.error("Erreur de décodage JSON, le fichier est peut-être corrompu.")

    # Ajout du nouveau numéro de contrat si nécessaire
    if contrat_number not in data:
        data.add(contrat_number)
        with open(file_path, "w") as file:
            json.dump(list(data), file)  # Convertir l'ensemble en liste pour la sérialisation
        logger.info(f"Contrat numéro {contrat_number} ajouté.")
    else:
        logger.info(f"Contrat numéro {contrat_number} déjà présent, non ajouté.")

def create_dictionnaire(excel_path):
    # Lecture du fichier Excel
    df = pd.read_excel(excel_path)
    # Creation du dictionnaire
    dictionnaire = {}
    for index, row in df.iterrows():
        numero_contrat = row['N°Contrat']
        regate_depot_ancien = str(int(row['Ancien Régate Dépôt'])) if not pd.isna(row['Ancien Régate Dépôt']) else None
        regate_depot_nouveau = str(int(row['Nouveau Régate Dépôt'])) if not pd.isna(row['Nouveau Régate Dépôt']) else None
        regate_traitement_ancien = str(int(row['Ancien Régate Traitement'])) if not pd.isna(row['Ancien Régate Traitement']) else None
        regate_traitement_nouveau = str(int(row['Nouveau Régate Traitement'])) if not pd.isna(row['Nouveau Régate Traitement']) else None
        # Ajout dans le dictionnaire
        dictionnaire[numero_contrat] = {
            'Ancien Régate Dépôt': regate_depot_ancien,
            'Nouveau Régate Dépôt': regate_depot_nouveau,
            'Ancien Régate Traitement': regate_traitement_ancien,
            'Nouveau Régate Traitement': regate_traitement_nouveau
        }
    return dictionnaire

def switch_to_iframe_and_click_modification(driver, wait, contrat_number, timeout=10):
    logger.info("Changement vers iframe et clic sur 'Modification'...")
    try:
        # Sélection de l'iframe et passage à l'intérieur
        iframe_selector = "#modalRefContrat > div > div > div.modal-body > iframe"
        iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector))
        )
        driver.switch_to.frame(iframe)
        logger.debug("Passé à l'iframe avec succès.")

        # Sélection du bouton de modification
        modification_button_selector = (
            "//permission/a[@href='#amendment']//div[@id='detailsModificationButton']"
        )
        bouton_modification = wait.until(
            EC.element_to_be_clickable((By.XPATH, modification_button_selector))
        )
        bouton_modification.click()
        logger.info(f"Clique sur le bouton de modification pour le contrat {contrat_number} effectué avec succès.")
        
    except TimeoutException:
        logger.exception(
            f"Le bouton 'Modification' pour le contrat {contrat_number} n'est pas trouvé dans le temps imparti. Enregistrement dans le fichier non_modifiable_cas_4.json"
        )
        save_non_modifiable_contract(contrat_number)
        raise
    except NoSuchElementException:
        logger.exception(
            f"L'élément bouton 'Modification' pour le contrat {contrat_number} n'a pas été trouvé."
        )
        save_non_modifiable_contract(contrat_number)
        raise
    except Exception as e:
        logger.exception(
            f"Erreur inattendue lors du clic sur le bouton 'Modification' pour le contrat {contrat_number}."
        )
        raise
    finally:
        driver.switch_to.default_content()
        logger.debug("Retour au contenu principal après traitement de l'iframe.")

def wait_for_complete_redirection(driver, wait, timeout=10):
    handle_api_modal(driver, wait)
    handle_modification_modal(driver, wait)
    
    logger.info("Attente de la redirection...")

    try:
        # Attendre que l'élément <h1> soit présent sur la page
        h1_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        h1_text = h1_element.text
        logger.debug(f"Texte de l'en-tête H1: {h1_text}")

        # Définir le sélecteur cible en fonction du texte de l'en-tête
        if "Collecte Remise Plus" in h1_text:
            target_selector = "#content_offre > ul > li:nth-child(3) > a"
            logger.debug("Clique sur Condtions Particulières de Réalisations")
        elif "Collecte et remise" in h1_text:
            target_selector = "#content_offre > ul > li:nth-child(3) > a"
            logger.debug("Clique sur Condtions Particulières de Réalisations")
        else:
            target_selector = "#content_offre > ul > li:nth-child(2) > a"
            logger.debug("Clique sur Condtions Particulières de Ventes")
        
        # Attendre que l'élément cible soit cliquable
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, target_selector))
        )
        element.click()
        logger.info("L'élément cible est cliquable et a été cliqué.")
    except TimeoutException as e:
        logger.exception("La redirection ou le chargement de la page n'a pas été complet dans le temps imparti, ou l'élément cible n'a pas été trouvé.")
        raise
    except NoSuchElementException as e:
        logger.exception("L'élément h1 ou l'élément cible n'a pas été trouvé sur la page.")
        raise
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'attente de la redirection ou du chargement de la page.")
        raise


def modifications_conditions_ventes(driver, wait, numero_contrat, dictionnaire, dictionnaire_original):
    # Creation d'une instance de la classe AffranchigoForfaitCase
    affranchigo_forfait_case = AffranchigoForfaitCase(driver)
    # Creation de l'instance de la classe AffranchigoFLibCase
    affranchigo_liberte_case = AffranchigoLibCase(driver)
    # Creation de l'instance de la classe DestineoCase
    destineo_case = destineoCase(driver)
    # Creation de l'instance de la classe FrequenceoCase
    frequenceo_case = FrequenceoCase(driver)
    # Creation de l'instance de la classe Proxicompte
    proxicompte_case = ProxicompteCase(driver)
    # Creation de l'instance de la classe Proxicompte
    collecte_remise_case = CollecteRemise(driver)
    
    try:
        h1_text = driver.find_element(By.TAG_NAME, "h1").text
        logger.debug(f"Texte de l'en-tête H1: {h1_text}")
        if "Affranchigo forfait" in h1_text:
            logger.info(" Contrat Affranchigo forfait trouve")
            if not isinstance(dictionnaire, dict):
                logger.error(f"Type incorrect de 'dictionnaire' detecte: {type(dictionnaire)}; restauration en cours.")
                # Restaure le dictionnaire à partir d'une source fiable ou reinitialise-le
                dictionnaire = copy.deepcopy(dictionnaire_original)
                logger.debug(f"Dictionnaire type: {type(dictionnaire)}")
            else:
                # Continuation normale du traitement
                affranchigo_forfait_case.handle_case_forfait(driver, numero_contrat, dictionnaire)
        elif "Affranchigo liberté" in h1_text:
            logger.debug("Affranchigo liberté")
            affranchigo_liberte_case.handle_case_lib(numero_contrat, dictionnaire)
        elif "Destineo esprit libre" in h1_text:
            logger.debug("destineo")
            destineo_case.handle_case_destineo(driver, wait, numero_contrat, dictionnaire)
        elif "Frequenceo" in h1_text:
            logger.debug("Frequenceo")
            frequenceo_case.handle_case_frequenceo(driver, wait, numero_contrat, dictionnaire)
        elif "Proxicompte" in h1_text:
            proxicompte_case. handle_case_proxicompte(driver, numero_contrat, dictionnaire)
            logger.debug("Proxicompte")
        elif "Collecte Remise Plus" in h1_text:
            collecte_remise_case.handle_case_collecte_remise(driver, wait, numero_contrat, dictionnaire)
            logger.debug("Collecte Remise Plus")
        elif "Collecte et remise" in h1_text:
            collecte_remise_case.handle_case_collecte_remise(driver, wait, numero_contrat, dictionnaire)
            logger.debug("Collecte et Remise")
    except Exception as e:
        logger.exception(f"Service non reconnu : {e}")
        log_error_and_capture_screenshot(driver, "Erreur_service_non_reconnu", e)


def process_contract(driver, wait, numero_contrat, dictionnaire, dictionnaire_original, retry_count=0):
    try:
        submit_contract_number(driver, wait, numero_contrat)
        switch_to_iframe_and_click_modification(driver, wait, numero_contrat)
        wait_for_complete_redirection(driver, wait)
        modifications_conditions_ventes(driver, wait, numero_contrat, dictionnaire, dictionnaire_original)

        logger.info(f"Traitement du contrat numero {numero_contrat} termine.")
        return True  # Indique un succes
    except WebDriverException as e:
        logger.critical(f"Probleme de connexion detecte : {e}")
        if retry_count < 3:  # Limite de nouvelles tentatives
            driver.get("https://www.exemple.intranet.fr")
            return process_contract(driver, wait, numero_contrat, dictionnaire, dictionnaire_original, retry_count+1)  # Recursivite avec valeur de retour
        else:
            logger.error(f"Nombre maximal de tentatives atteint pour le contrat {numero_contrat}")
            return False  # echec apres tentatives

    except Exception as e:
        logger.critical(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")
        traceback.logger.debug_exc()
        log_error_and_capture_screenshot(driver, f"Erreur lors du traitement du contrat {numero_contrat}", e)
        return False  # Gestion des exceptions inattendues

def main():
    logger.info("Démarrage du script...")

    # Extraction des numéros de contrat du fichier Excel et enregistrement dans un fichier JSON
    excel_path = "MEQ - Fichier test pour le robot.xlsx"
    json_path = 'numeros_contrat_robot.json'
    extract_contrat_numbers_to_json(excel_path, json_path)
    
    driver, wait = configure_selenium()
    login(driver, wait)

    # Création du dictionnaire à partir du fichier Excel
    dictionnaire_original = create_dictionnaire(excel_path)
    dictionnaire = copy.deepcopy(dictionnaire_original)
    logger.debug(f"{dictionnaire}")
    logger.debug(f"Type de 'dictionnaire' juste après création: {type(dictionnaire_original)}")

    file_path = "numeros_contrat_robot.json"
    numeros_contrat = process_json_files(file_path)
    compteur = 0

    for numero_contrat in numeros_contrat:
        if compteur >= 100:
            logger.debug("Limite de 100 contrats atteinte.")
            break

        if numero_contrat:
            logger.info(f"Traitement du contrat numéro {numero_contrat}...")
            # Passer le dictionnaire en tant que paramètre
            
            logger.debug(f"Type de 'dictionnaire' avant process_contract pour {numero_contrat}: {type(dictionnaire)}")
            success = process_contract(driver, wait, numero_contrat, dictionnaire, dictionnaire_original)
            logger.debug(f"Type de 'dictionnaire' après process_contract pour {numero_contrat}: {type(dictionnaire)}")

            compteur += 1
            logger.info(f"Nombre de contrats traités : {compteur}")

            if success:
                save_processed_contracts([numero_contrat])
            else:
                save_non_modifiable_contract(numero_contrat)

    driver.quit()
    logger.info("Fin du traitement.")

if __name__ == "__main__":
    main()