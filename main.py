import os
import json
import copy
import traceback
import pandas as pd
import atexit
import threading
import pychrome
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementClickInterceptedException
from affranchigo_forfait_case import AffranchigoForfaitCase
from affranchigo_lib_case import AffranchigoLibCase
from destineo_case import destineoCase
from frequenceo_case import FrequenceoCase
from proxicompte_case import ProxicompteCase
from collecte_remise import CollecteRemise
from debug import log_error_and_capture_screenshot, setup_logger
from data_processing import extract_contrat_numbers_to_json


# Initialisation du logger
logger = setup_logger()
load_dotenv()


# Définition du verrou pour les opérations sur les fichiers
file_lock = threading.Lock()


class SeleniumManager:
    def __init__(self):
        self.drivers = []
        self.identifiant = os.getenv("IDENTIFIANT")
        self.mot_de_passe = os.getenv("MOT_DE_PASSE")


    def configure_selenium(self):
        logger.debug("Configuration de Selenium...")
        service = Service("data/msedgedriver.exe")
        options = Options()
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-features=EdgeEnterpriseModeSiteListManager')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')  # Optionnel, pour exécuter en mode headless
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Edge(service=service, options=options)
        self.drivers.append(driver)
        driver.get("https://exemple.intranet.fr")
        wait = WebDriverWait(driver, 10)
        return driver, wait
   
    def setup_devtools(self, url):
        self.browser = pychrome.Browser(url="http://127.0.0.1:9222")
        tab = self.browser.new_tab()
        tab.start()
        tab.Page.navigate(url=url)
        tab.wait(5)
        logger.info("DevTools configuré et prêt")


    def cleanup(self):
        for driver in self.drivers:
            driver.quit()
        logger.debug("Nettoyage effectué. Toutes les instances de driver ont été fermées.")


def handle_modal(driver, wait, name=""):
    try:
        modal_elements = driver.find_elements(By.NAME, name)
        if modal_elements:
            modal_elements[0].click()
            logger.debug(f"Modal '{name}' gérée.")
        else:
            logger.debug(f"La modal '{name}' n'est pas apparue.")
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la modal '{name}': {e}")


def login(driver, wait, identifiant, mot_de_passe):
    logger.debug("Tentative de connexion...")


    try:
        input_identifiant = wait.until(EC.presence_of_element_located((By.ID, "AUTHENTICATION.LOGIN")))
        input_identifiant.clear()
        input_identifiant.send_keys(identifiant)
        input_identifiant.send_keys(Keys.RETURN)


        input_mot_de_passe = wait.until(EC.presence_of_element_located((By.ID, "AUTHENTICATION.PASSWORD")))
        input_mot_de_passe.clear()
        input_mot_de_passe.send_keys(mot_de_passe)
        input_mot_de_passe.send_keys(Keys.RETURN)
    except TimeoutException:
        logger.debug("Dejà connecté ou le champ d'identifiant n'est pas présent.")
    except Exception as e:    
        log_error_and_capture_screenshot(driver, "Problème Login", e)


def process_json_files(file_path):
    logger.debug("Traitement du fichier JSON pour les contrats...")
    numeros_contrat = []


    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            numeros_contrat = list(data.values())


    return numeros_contrat


def submit_contract_number(driver, wait, numero):
    logger.debug(f"Soumission du numero de contrat {numero}...")
    try:
        input_element = wait.until(EC.presence_of_element_located((By.ID, "idContrat")))
        input_element.clear()
        input_element.send_keys(numero)
        input_element.send_keys(Keys.RETURN)


        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSubmitContrat_accesRDC")))
        submit_button.click()


        handle_modal(driver, wait, "OK")
    except TimeoutException:
        logger.debug("Pas de première modale à gérer.")
    except Exception as e:
        log_error_and_capture_screenshot(driver, "Submit_contrat", e)


def save_processed_contracts(contrats, file_path="numeros_contrat_traites.json"):
    try:
        with file_lock, open(file_path, "r+") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
            updated_data = existing_data + [c for c in contrats if c not in existing_data]
            file.seek(0)
            file.truncate()  # Clear the file before writing
            json.dump(updated_data, file)
    except FileNotFoundError:
        with file_lock, open(file_path, "w") as file:
            json.dump(contrats, file)




def save_non_modifiable_contract(contrat_number, file_path="annexe_multisites.json"):
    data = set()
    try:
        with file_lock, open(file_path, "r") as file:
            existing_data = json.load(file)
            data.update(existing_data)
    except FileNotFoundError:
        logger.debug("Le fichier n'existe pas, il sera créé.")
    except json.JSONDecodeError:
        logger.error("Erreur de décodage JSON, le fichier est peut-être corrompu.")


    if contrat_number not in data:
        data.add(contrat_number)
        with file_lock, open(file_path, "w") as file:
            json.dump(list(data), file)
        logger.debug(f"Contrat numéro {contrat_number} ajouté.")
    else:
        logger.debug(f"Contrat numéro {contrat_number} déjà présent, non ajouté.")


def create_dictionnaire(excel_path):
    df = pd.read_excel(excel_path)
    dictionnaire = {}
    for index, row in df.iterrows():
        numero_contrat = row['N°Contrat']
        regate_depot_ancien = str(int(row['Ancien Régate Dépôt'])) if not pd.isna(row['Ancien Régate Dépôt']) else None
        regate_depot_nouveau = str(int(row['Nouveau Régate Dépôt'])) if not pd.isna(row['Nouveau Régate Dépôt']) else None
        regate_traitement_ancien = str(int(row['Ancien Régate Traitement'])) if not pd.isna(row['Ancien Régate Traitement']) else None
        regate_traitement_nouveau = str(int(row['Nouveau Régate Traitement'])) if not pd.isna(row['Nouveau Régate Traitement']) else None


        dictionnaire[numero_contrat] = {
            'Ancien Régate Dépôt': regate_depot_ancien,
            'Nouveau Régate Dépôt': regate_depot_nouveau,
            'Ancien Régate Traitement': regate_traitement_ancien,
            'Nouveau Régate Traitement': regate_traitement_nouveau
        }
    return dictionnaire


def handle_non_clickable_element(driver, numero_contrat):
    try:
        span_element = driver.find_element(By.ID, "detailsCategorieV")
        if span_element.text == "Annexe Multisites":
            save_non_modifiable_contract(numero_contrat)
            logger.debug(f"Contrat {numero_contrat} enregistré comme non modifiable en raison de 'Annexe Multisites'.")
    except NoSuchElementException:
        logger.debug(f"L'élément span.detailsCategorieV n'a pas été trouvé pour le contrat {numero_contrat}.")
    except Exception as e:
        logger.exception(f"Erreur inattendue lors de la vérification de l'élément span.detailsCategorieV pour le contrat {numero_contrat}.")


def switch_to_iframe_and_click_modification(driver, wait, contrat_number):
    logger.debug("Changement vers iframe et clic sur 'Modification'...")
    try:
        iframe_selector = "#modalRefContrat > div > div > div.modal-body > iframe"
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
        driver.switch_to.frame(iframe)
        logger.debug("Passé à l'iframe avec succès.")
       
        modification_button_selector = "//permission/a[@href='#amendment']//div[@id='detailsModificationButton']"
       
        max_attempts = 1
        for attempt in range(max_attempts):
            try:
                bouton_modification = wait.until(EC.element_to_be_clickable((By.XPATH, modification_button_selector)))
                bouton_modification.click()
                logger.debug(f"Clique sur le bouton de modification pour le contrat {contrat_number} effectué avec succès.")
                break
            except TimeoutException as te:
                if attempt < max_attempts - 1:
                    logger.warning(f"{contrat_number} * Tentative {attempt + 1} échouée, nouvelle tentative...")
                else:
                    logger.info(f"{contrat_number} * Le bouton 'Modification'n'est pas trouvé après {max_attempts} tentatives. Contrat Annexes Multisites")
                    handle_non_clickable_element(driver, contrat_number)
                    raise
            except NoSuchElementException as nse:
                logger.critical(f"L'élément bouton 'Modification' pour le contrat {contrat_number} n'a pas été trouvé.")
                handle_non_clickable_element(driver, contrat_number)
                raise


    except Exception as e:
        logger.debug(f"Erreur inattendue lors du clic sur le bouton 'Modification' pour le contrat {contrat_number}.")
        raise
    finally:
        driver.switch_to.default_content()
        logger.debug("Retour au contenu principal après traitement de l'iframe.")




def wait_for_complete_redirection(driver, wait, timeout=10):
    handle_modal(driver, wait, "swal2-confirm.swal2-styled")
   
    logger.debug("Attente de la redirection...")


    try:
        h1_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1_text = h1_element.text
        logger.debug(f"Texte de l'en-tête H1: {h1_text}")


        if "Collecte Remise Plus" in h1_text or "Collecte et remise" in h1_text:
            target_selector = "#content_offre > ul > li:nth-child(3) > a"
        else:
            target_selector = "#content_offre > ul > li:nth-child(2) > a"
       
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, target_selector)))
        element.click()
        logger.debug("L'élément cible est cliquable et a été cliqué.")
    except TimeoutException as e:
        logger.exception("La redirection ou le chargement de la page n'a pas été complet dans le temps imparti, ou l'élément cible n'a pas été trouvé.")
        raise
    except NoSuchElementException as e:
        logger.exception("L'élément h1 ou l'élément cible n'a pas été trouvé sur la page.")
        raise
    except Exception as e:
        logger.debug("Erreur inattendue lors de l'attente de la redirection ou du chargement de la page.")
        raise


def modifications_conditions_ventes(driver, wait, numero_contrat, dictionnaire, dictionnaire_original):
    affranchigo_forfait_case = AffranchigoForfaitCase(driver)
    affranchigo_liberte_case = AffranchigoLibCase(driver)
    destineo_case = destineoCase(driver)
    frequenceo_case = FrequenceoCase(driver)
    proxicompte_case = ProxicompteCase(driver)
    collecte_remise_case = CollecteRemise(driver)
   
    try:
        h1_text = driver.find_element(By.TAG_NAME, "h1").text
        logger.debug(f"Texte de l'en-tête H1: {h1_text}")
        if "Affranchigo forfait" in h1_text:
            logger.debug(" Contrat Affranchigo forfait")
            if not isinstance(dictionnaire, dict):
                logger.error(f"Type incorrect de 'dictionnaire' détecté: {type(dictionnaire)}; restauration en cours.")
                dictionnaire = copy.deepcopy(dictionnaire_original)
                logger.debug(f"Dictionnaire type: {type(dictionnaire)}")
            else:
                affranchigo_forfait_case.handle_case_forfait(driver, numero_contrat, dictionnaire)
        elif "Affranchigo liberté" in h1_text:
            logger.debug("Contat Affranchigo liberté")
            affranchigo_liberte_case.handle_case_lib(numero_contrat, dictionnaire)
        elif "Destineo esprit libre" in h1_text:
            logger.debug("Contrat Destineo")
            destineo_case.handle_case_destineo(driver, wait, numero_contrat, dictionnaire)
        elif "Frequenceo" in h1_text:
            logger.debug("Contrat Frequenceo")
            frequenceo_case.handle_case_frequenceo(driver, wait, numero_contrat, dictionnaire)
        elif "Proxicompte" in h1_text:
            proxicompte_case.handle_case_proxicompte(driver, numero_contrat, dictionnaire)
            logger.debug("Contrat Proxicompte")
        elif "Collecte Remise Plus" in h1_text:
            collecte_remise_case.handle_case_collecte_remise(driver, wait, numero_contrat, dictionnaire)
            logger.debug("Contrat Collecte Remise Plus")
        elif "Collecte et remise" in h1_text:
            collecte_remise_case.handle_case_collecte_remise(driver, wait, numero_contrat, dictionnaire)
            logger.debug("Contrat Collecte et Remise")
    except Exception as e:
        logger.exception(f"Service non reconnu : {e}")
        log_error_and_capture_screenshot(driver, "Erreur_service_non_reconnu", e)


STOP_FLAG = False


def stop_process():
    global STOP_FLAG
    STOP_FLAG = True


def cleanup(driver=None):
    if driver:
        driver.quit()
    # Ajoutez ici d'autres opérations de nettoyage nécessaires
    logger.debug("Nettoyage effectué après l'arrêt d'urgence.")


def process_contract(numero_contrat, dictionnaire, dictionnaire_original, max_retries=1):
    global STOP_FLAG
    manager = SeleniumManager()
    retries = 0
    while retries <= max_retries and not STOP_FLAG:
        driver, wait = manager.configure_selenium()
        try:
            login(driver, wait, manager.identifiant, manager.mot_de_passe)
            submit_contract_number(driver, wait, numero_contrat)
            switch_to_iframe_and_click_modification(driver, wait, numero_contrat)
            wait_for_complete_redirection(driver, wait)
            modifications_conditions_ventes(driver, wait, numero_contrat, dictionnaire, dictionnaire_original)


            logger.info(f"{numero_contrat} * Traitement terminé.")
           
            # Sauvegarder le contrat traité
            save_processed_contracts([numero_contrat])


            return True
        except WebDriverException as e:
            logger.warning(f"Problème de connexion détecté pour le contrat {numero_contrat} : {e}")
            if retries < max_retries:
                retries += 1
                logger.info(f"Nouvelle tentative ({retries}/{max_retries}) pour le contrat {numero_contrat}")
                driver.quit()
                continue
            else:
                logger.error(f"Nombre maximal de tentatives atteint pour le contrat {numero_contrat}")
                cleanup(driver)
                return False
        except Exception as e:
            logger.critical(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")
            traceback.print_exc()
            log_error_and_capture_screenshot(driver, f"Erreur lors du traitement du contrat {numero_contrat}", e)
            cleanup(driver)
            return False
        finally:
            driver.quit()
    if STOP_FLAG:
        cleanup(driver)
    return False


def process_contract_parallel(args):
    numero_contrat, dictionnaire, dictionnaire_original = args
    return process_contract(numero_contrat, dictionnaire, dictionnaire_original)


def main(excel_path, mode, progress_callback=None):
    global STOP_FLAG
    logger.debug("Démarrage du RPA...")


    json_path = 'data/numeros_contrat_robot.json'
    extract_contrat_numbers_to_json(excel_path, json_path)


    dictionnaire_original = create_dictionnaire(excel_path)
    dictionnaire = copy.deepcopy(dictionnaire_original)


    numeros_contrat = process_json_files(json_path)
    processed_count = 0
    try:
        if mode == "multi":
            with ThreadPoolExecutor(max_workers=7) as executor:  # 6 max sur cette ordi et configuration
                futures = [executor.submit(process_contract_parallel, (numero_contrat, dictionnaire, dictionnaire_original))
                           for numero_contrat in numeros_contrat[:50]]


                total_futures = len(futures)
                for i, future in enumerate(as_completed(futures)):
                    if STOP_FLAG:
                        logger.debug("Arrêt d'urgence activé.")
                        break
                    try:
                        if future.result():
                            processed_count += 1
                            logger.info(f"Nombre de contrats traités : {processed_count}")
                            if progress_callback:
                                progress_callback((i + 1) / total_futures * 100)
                    except Exception as e:
                        logger.error(f"Erreur lors de l'exécution de la tâche : {e}")
        else:
            total_contracts = min(len(numeros_contrat), 50)  
            for i, numero_contrat in enumerate(numeros_contrat[:50]):
                if STOP_FLAG:
                    logger.debug("Arrêt d'urgence activé.")
                    break
                try:
                    result = process_contract(numero_contrat, dictionnaire, dictionnaire_original)
                    if result:
                        processed_count += 1
                        logger.info(f"Nombre de contrats traités : {processed_count}")
                        if progress_callback:
                            progress_callback((i + 1) / total_contracts * 100)
                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution de la tâche : {e}")
    finally:
        cleanup()
        logger.info("Traitement terminé.")



