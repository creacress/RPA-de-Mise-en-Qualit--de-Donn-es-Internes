import time
import copy
import json
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from debug import setup_logger

# Initatilisation du debug
logger = setup_logger()


class AffranchigoForfaitCase:
    def __init__(self, driver):
        self.driver = driver

    def initialize_selectors(self, driver):
        selectors = {}
        try:
            wait = WebDriverWait(driver, 10)
            selectors["radio_non"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0")))
            selectors["radio_oui"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1")))

            if selectors["radio_oui"].is_selected():
                # Stocker uniquement les elements du DOM
                selectors["select_first_role"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(9) select")))
                selectors["input_first_regate"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487")))
                selectors["select_first_etablissement"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(3) select")))
            else:
                selectors["select_first_role"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(9) select")))
                selectors["input_first_regate"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487")))
                selectors["select_first_etablissement"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(3) select")))
                selectors["select_second_role"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#\\[g0_p159\\|0_r486\\[0\\]\\] critere-form:nth-child(9) select")))
                selectors["input_second_regate"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487[0]")))
                selectors["select_second_etablissement"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#\\[g0_p159\\|0_r486\\[0\\]\\] critere-form:nth-child(3) select")))
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des selecteurs: {e}")
        return selectors
    
    def initialize_selectors_radio_oui(self):
        selectors = {}
        try:
            logger.debug("Initialisation des sélecteurs pour radio_oui.")
            wait = WebDriverWait(self.driver, 20)  # Augmentation du délai d'attente

            selectors["radio_oui"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1")))
            logger.debug("Sélecteur radio_oui initialisé.")

            selectors["radio_non"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0")))
            logger.debug("Sélecteur radio_non initialisé.")

            selectors["input_first_regate"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487")))
            logger.debug("Sélecteur input_first_regate initialisé.")
            
            selectors["select_first_etablissement"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(3) select")))
            logger.debug("Sélecteur select_first_etablissement initialisé.")
            
            selectors["select_first_role"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(9) select")))
            logger.debug("Sélecteur select_first_role initialisé.")

        except TimeoutException as e:
            logger.error(f"Timeout lors de l'initialisation des sélecteurs radio_oui: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des sélecteurs radio_oui: {e}")

        return selectors
    
    def initialize_selectors_radio_non(self):
        selectors = {}
        try:
            logger.debug("Initialisation des sélecteurs pour radio_non.")
            wait = WebDriverWait(self.driver, 10)
            
            selectors["radio_non"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0")))

            selectors["select_first_role"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(9) select")))

            selectors["select_second_role"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#\\[g0_p159\\|0_r486\\[0\\]\\] critere-form:nth-child(9) select")))

            selectors["input_first_regate"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487")))

            selectors["input_second_regate"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487[0]")))

            selectors["select_first_etablissement"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] critere-form:nth-child(3) select")))

            selectors["select_second_etablissement"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#\\[g0_p159\\|0_r486\\[0\\]\\] critere-form:nth-child(3) select")))

        except TimeoutException as e:
            logger.error(f"Timeout lors de l'initialisation des sélecteurs radio_non: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des sélecteurs radio_non: {e}")

        return selectors

    # Fonction pour selectionner l'Heure dans le cas
    def select_time_in_selectors(self):
        select_time_selectors = [
            "#g0_p159\\|0_r486_c490\\[0\\]",
            "#g0_p159\\|0_r486\\[0\\] input-component select"
        ]

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ", ".join(select_time_selectors))
                )
            )
        
            for select_time_selector in select_time_selectors:
                for element in self.driver.find_elements(By.CSS_SELECTOR, select_time_selector):
                    try:
                        select_element = Select(element)
                        current_value = select_element.first_selected_option.get_attribute('value')
                        logger.debug(f"Valeur actuelle selectionnee: '{current_value}'")

                        if current_value in ['', 'null']:
                            logger.debug("Aucune heure selectionnee ou valeur 'null'. Selection de l'heure par defaut.")
                            select_element.select_by_index(16)
                        else:
                            logger.debug(f"L'heure est dejà selectionnee: '{current_value}'.")
                    except Exception as e:
                        logger.critical(f"Erreur lors de la selection de l'heure: {e}")
        except TimeoutException:
            logger.exception("Aucun selecteur de temps trouve.")
    
    def submit_forfait(driver):
        # Trouver et cliquer sur le bouton de soumission
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "#odcFormCPR > button")
                    )
                )
                submit_button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_changes(
                        "https://www.exemple.intranet.fr"
                    )
                )
                logger.info("Formulaire soumis avec succes.")
                time.sleep(1)
                try:
                    # Retour à l'URL de depart
                    url_de_depart = "https://www.exemple.intranet.fr"
                    driver.get(url_de_depart)
                    logger.info("Retour à l'URL de depart reussi.")
                except Exception as e:
                    logger.critical(f"Erreur lors de la navigation vers l'URL de depart : {e}")
                    driver.save_screenshot("debug_screenshot_erreur_retour.png")
            except TimeoutException:
                logger.error("Le bouton de soumission n'as pas ete trouve dans les temps")
                driver.save_screenshot("debug_screenshot_erreur_clic.png")
            except Exception as e:
                logger.critical(f"Erreur lors de la soumission formulaire : {e}")
                driver.save_screenshot("debug_screenshot_erreur_soumission_forfait.png")

    def save_non_modifiable_contract(self, numero_contrat):
        """Enregistre le numéro de contrat dans un fichier JSON en évitant les doublons."""
        file_path = "re_traitement_lib.json"
        data = set()  # Utiliser un ensemble pour éviter les doublons

        try:
            logger.debug(f"Lecture du fichier existant : {file_path}")
            with open(file_path, "r") as file:
                existing_data = json.load(file)
                data.update(existing_data)  # Mise à jour de l'ensemble avec les données existantes
        except FileNotFoundError:
            logger.info("Le fichier n'existe pas, il sera créé.")
        except json.JSONDecodeError:
            logger.error("Erreur de décodage JSON, le fichier est peut-être corrompu.")

        if numero_contrat not in data:
            data.add(numero_contrat)
            with open(file_path, "w") as file:
                json.dump(list(data), file)  # Convertir l'ensemble en liste pour la sérialisation
            logger.info(f"Contrat numéro {numero_contrat} ajouté.")
        else:
            logger.info(f"Contrat numéro {numero_contrat} déjà présent, non ajouté.")
    
    def handle_case_forfait(self, driver, numero_contrat, dictionnaire):
        """Traitement principal pour chaque cas."""
        logger.debug(f"Début de traitement du cas Forfait pour le contrat {numero_contrat}")

        # Charger le fichier Excel
        df = pd.read_excel('MEQ - Fichier test pour le robot.xlsx')
        logger.debug("Fichier Excel chargé.")

        # Sélectionner les éléments radio
        radio_non = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0")))
        radio_oui = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1")))

        # Trouver la ligne correspondant au numéro de contrat
        row = df[df['N°Contrat'] == numero_contrat]
        if row.empty:
            logger.error(f'Contrat {numero_contrat} introuvable dans le fichier Excel')
            return

        # Extraire les valeurs de dépôt et de traitement
        depot_value = row['Nouveau Régate Dépôt'].values[0] if pd.notna(row['Nouveau Régate Dépôt'].values[0]) else None
        traitement_value = row['Nouveau Régate Traitement'].values[0] if pd.notna(row['Nouveau Régate Traitement'].values[0]) else None

        depot_value = str(int(depot_value)) if isinstance(depot_value, float) else str(depot_value) if depot_value else None
        traitement_value = str(int(traitement_value)) if isinstance(traitement_value, float) else str(traitement_value) if traitement_value else None

        # Initialiser les sélecteurs en fonction de la sélection des boutons radio
        if radio_non.is_selected():
            elements = self.initialize_selectors_radio_non()
            if not elements:
                logger.error(f"Impossible d'initialiser les sélecteurs pour le contrat {numero_contrat}")
                return
        elif radio_oui.is_selected():
            elements = self.initialize_selectors_radio_oui()
            if not elements:
                logger.error(f"Impossible d'initialiser les sélecteurs pour le contrat {numero_contrat}")
                return

        # Initialiser les boutons radio dans le dictionnaire des éléments
        elements["radio_non"] = radio_non
        elements["radio_oui"] = radio_oui

        current_value_first = None
        current_value_second = None

        if elements["radio_non"].is_selected():
            logger.debug("Le bouton non est sélectionné")
            select_first_role = Select(elements['select_first_role'])
            current_value_first = select_first_role.first_selected_option.text
            select_second_role = Select(elements['select_second_role'])
            current_value_second = select_second_role.first_selected_option.text
            logger.debug(f"Valeurs actuelles - Premier Rôle: {current_value_first}, Second Rôle: {current_value_second}")
        elif elements["radio_oui"].is_selected():
            logger.debug("Le bouton oui est sélectionné")
            select_first_role = Select(elements['select_first_role'])
            current_value_first = select_first_role.first_selected_option.text
            logger.debug(f"Valeurs actuelles - Premier Rôle: {current_value_first}")

        logger.debug(f"Valeurs actuelles - Premier Rôle: {current_value_first}, Second Rôle: {current_value_second}")

        # Logique de traitement en fonction des valeurs de dépôt et de traitement
        if depot_value and traitement_value:
            if depot_value == traitement_value:
                if current_value_first == "Dépôt et Traitement":
                    self.dépôt_et_traitement_égaux(numero_contrat, dictionnaire)
                elif (current_value_first == "Dépôt" or current_value_first == "Traitement") and (current_value_second == "Traitement" or current_value_second == "Dépôt"):
                    self.dépôt_traitement_diff_egaux(numero_contrat, dictionnaire)
                elif (current_value_first == "Dépôt" or current_value_second == "Dépôt") and (current_value_second == "" or current_value_first == ""):
                    self.dépôt_only_value_egaux(numero_contrat, dictionnaire)
                elif (current_value_first == "Traitement" or current_value_second == "Traitement") and (current_value_second == "" or current_value_first == ""):
                    self.traitement_only_value_egaux(numero_contrat, dictionnaire)
            else:
                if current_value_first == "Dépôt et Traitement":
                    self.dépôt_et_traitement_non_égaux(numero_contrat, dictionnaire)
                elif (current_value_first == "Dépôt" or current_value_first == "Traitement") and (current_value_second == "Traitement" or current_value_second == "Dépôt"):
                    self.dépôt_traitement_diff_non_égaux(numero_contrat, dictionnaire)
                elif (current_value_first == "Dépôt" or current_value_second == "Dépôt") and (current_value_second == "" or current_value_first == ""):
                    self.dépôt_only_value_diff(numero_contrat, dictionnaire)
                elif (current_value_first == "Traitement" or current_value_second == "Traitement") and (current_value_second == "" or current_value_first == ""):
                    self.traitement_only_value_diff(numero_contrat, dictionnaire)
        elif depot_value:
            if current_value_first == "Dépôt et Traitement":
                self.dépôt_et_traitement_dépôt_modification(numero_contrat, dictionnaire)
            elif (current_value_first == "Dépôt" or current_value_first == "Traitement") and (current_value_second == "Traitement" or current_value_second == "Dépôt"):
                self.dépôt_diff_non_égaux(numero_contrat, dictionnaire)
            elif (current_value_first == "Dépôt" or current_value_second == "Dépôt") and (current_value_second == "" or current_value_first == ""):
                self.dépôt_only_depôt_only(numero_contrat, dictionnaire)
            elif (current_value_first == "Traitement" or current_value_second == "Traitement") and (current_value_second == "" or current_value_first == ""):
                self.traitement_only_depôt_only(numero_contrat, dictionnaire)
        elif traitement_value:
            if current_value_first == "Dépôt et Traitement":
                self.dépôt_et_traitement_traitement_modification(numero_contrat, dictionnaire)
            elif (current_value_first == "Dépôt" or current_value_first == "Traitement") and (current_value_second == "Traitement" or current_value_second == "Dépôt"):
                self.traitement_diff_non_égaux(numero_contrat, dictionnaire)
            elif (current_value_first == "Dépôt" or current_value_second == "Dépôt") and (current_value_second == "" or current_value_first == ""):
                self.dépôt_only_traitement_only(numero_contrat, dictionnaire)
            elif (current_value_first == "Traitement" or current_value_second == "Traitement") and (current_value_second == "" or current_value_first == ""):
                self.traitement_only_traitement_only(numero_contrat, dictionnaire)
        else:
            logger.error(f'Aucune valeur à traiter pour le contrat {numero_contrat}')

    def update_input(self, element, new_value):
        logger.debug(f"Tentative de mise à jour de l'input avec la nouvelle valeur: {new_value}")
        if element is None:
            logger.error("L'élément fourni à update_input est None.")
            return
        if new_value is None:
            logger.error("La nouvelle valeur pour l'input est None.")
            return
        element.clear()
        element.send_keys(new_value)
        element.send_keys(Keys.TAB)
        logger.info("Nouveau code régate attribué")

    def update_select_element(self, driver, select_element):
        logger.debug(f"Mise à jour de l'élément select: {select_element}")

        try:
            if isinstance(select_element, str):
                wait = WebDriverWait(driver, 10)
                select_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, select_element)))
            elif not isinstance(select_element, WebElement):
                raise ValueError("select_element must be a string or WebElement")

            # Wait until the select element is interactable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(select_element))

            # Ensure all options are loaded
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "option")))

            select_obj = Select(select_element)

            try:
                current_selected = select_obj.first_selected_option.text
            except NoSuchElementException:
                current_selected = "None"

            logger.debug(f"Selection actuelle dans le select: {current_selected}")

            select_obj.select_by_index(1)

            try:
                new_selected = select_obj.first_selected_option.text
            except NoSuchElementException:
                new_selected = "None"

            logger.debug(f"Index {1} sélectionné dans le select, nouvelle selection: {new_selected}")
            logger.info("Nouvel établissement attribué.")
        except TimeoutException:
            logger.error("Le sélecteur n'a pas pu être localisé ou n'était pas interactif dans le temps imparti.")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'élément select: {e}")
    
    def select_role(self, select_element, role):
        try:
            select_obj = Select(select_element)
            for option in select_obj.options:
                if option.text.strip() == role:
                    select_obj.select_by_visible_text(role)
                    logger.debug(f"Rôle '{role}' sélectionné dans le sélecteur.")
                    return
            logger.error(f"Rôle '{role}' non trouvé dans le sélecteur.")
        except Exception as e:
            logger.error(f"Erreur lors de la sélection du rôle '{role}' : {e}")

    
    # Ajout des méthodes spécifiques appelées dans handle_case_lib
    def dépôt_et_traitement_égaux(self, numero_contrat, dictionnaire):
        selectors = self.initialize_selectors_radio_oui()
        if not selectors:
            logger.error(f"Impossible d'initialiser les sélecteurs pour le contrat {numero_contrat}")
            return
        input_element = selectors.get("input_first_regate")
        select_element = selectors.get("select_first_etablissement")
        new_value = dictionnaire.get(numero_contrat, {}).get('Nouveau Régate Traitement', '')
        self.update_input(input_element, new_value)
        self.update_select_element(self.driver, select_element)
        self.select_time_in_selectors()
        logger.debug("Mise à jour du code régate. Enregistrement. Sortie.")

    def dépôt_et_traitement_non_égaux(self, numero_contrat, dictionnaire):
        logger.debug("Début dépôt_et_traitement_non_égaux")
        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_non = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_traitement or not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_non.is_displayed() or not radio_non.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass

            # Utilisation de JavaScript pour cliquer sur le bouton radio_non
            self.driver.execute_script("arguments[0].click();", radio_non)
            logger.debug("Clic sur radio_non effectué avec JavaScript.")
            time.sleep(3)
            try:
                input_second_regate = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487[0]"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")
            input_second_regate.click()
            input_second_regate.send_keys(Keys.TAB)
            
            selectors = self.initialize_selectors_radio_non()
            if not selectors:
                logger.error(f"Impossible d'initialiser les sélecteurs après le clic pour le contrat {numero_contrat}")
                return
            
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_first)
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def dépôt_et_traitement_dépôt_modification(self, numero_contrat, dictionnaire):
        logger.debug("1er bloc à dépôt avec code régate fichier de dépôt. 2ème bloc à traitement avec code régate sauvegardé. Les 2 heures sont mises à 16h30.")
        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_non = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_non.is_displayed() or not radio_non.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass

            # Utilisation de JavaScript pour cliquer sur le bouton radio_non
            self.driver.execute_script("arguments[0].click();", radio_non)
            logger.debug("Clic sur radio_non effectué avec JavaScript.")
            time.sleep(3)
            try:
                input_second_regate = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487[0]"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")
            input_second_regate.click()
            input_second_regate.send_keys(Keys.TAB)
            
            selectors = self.initialize_selectors_radio_non()
            if not selectors:
                logger.error(f"Impossible d'initialiser les sélecteurs après le clic pour le contrat {numero_contrat}")
                return
            
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_second, new_value_depot)
            
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_second, "Dépôt")
            self.select_role(select_role_first, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def dépôt_et_traitement_traitement_modification(self, numero_contrat, dictionnaire):
        logger.debug("1er bloc à dépôt avec code régate sauvegardé. 2ème bloc à traitement avec code régate traitement du fichier. Les 2 heures sont mises à 16h30.")
        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_non = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v0"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')

            if not new_value_traitement:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_non.is_displayed() or not radio_non.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass

            # Utilisation de JavaScript pour cliquer sur le bouton radio_non
            self.driver.execute_script("arguments[0].click();", radio_non)
            logger.debug("Clic sur radio_non effectué avec JavaScript.")
            time.sleep(3)
            try:
                input_second_regate = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_r486_c487[0]"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")
            input_second_regate.click()
            input_second_regate.send_keys(Keys.TAB)
            
            selectors = self.initialize_selectors_radio_non()
            if not selectors:
                logger.error(f"Impossible d'initialiser les sélecteurs après le clic pour le contrat {numero_contrat}")
                return
            
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def dépôt_traitement_diff_egaux(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour de l'input radio à Oui. Code REGATE avec le code REGATE de dépôt du fichier.")

        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_oui = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1"))
                )
            except TimeoutException:
                logger.error("Radio_oui non trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_oui.is_displayed() or not radio_oui.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass

            # Utilisation de JavaScript pour cliquer sur le bouton radio_non
            self.driver.execute_script("arguments[0].click();", radio_oui)
            logger.debug("Clic sur radio_oui effectué avec JavaScript.")
            time.sleep(3)
            
            selectors = self.initialize_selectors_radio_oui()
            if not selectors:
                logger.error(f"Impossible d'initialiser les sélecteurs après le clic pour le contrat {numero_contrat}")
                return
            
            input_regate_first = selectors.get("input_first_regate")
            
            select_element_first = selectors.get("select_first_etablissement")
            
            select_role_first = selectors.get("select_first_role")
            
            if not all([input_regate_first, select_element_first, select_role_first]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
            
            self.update_select_element(self.driver, select_element_first)

            self.select_time_in_selectors()

            # Sélection des rôles
            """ Dans ce cas le rôle se met automatiquement en "Dépôt et Traitement" """
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def dépôt_traitement_diff_non_égaux(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour des Codes REGATE avec identification des blocs.")
        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_traitement or not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return
            
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_first)
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_element_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")


    def dépôt_only_value_egaux(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour du code REGATE avec le code REGATE dépôt du fichier.")
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_oui = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1"))
                )
            except TimeoutException:
                logger.error("Radio_non no trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_oui.is_displayed() or not radio_oui.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass

            # Utilisation de JavaScript pour cliquer sur le bouton radio_non
            self.driver.execute_script("arguments[0].click();", radio_oui)
            logger.debug("Clic sur radio_non effectué avec JavaScript.")
            time.sleep(3)
            
            input_regate_first = selectors.get("input_first_regate")
            
            select_element_first = selectors.get("select_first_etablissement")

            select_role_first = selectors.get("select_first_role")


            if not all([input_regate_first, select_element_first, select_role_first]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
            
            self.update_select_element(self.driver, select_element_first)

            
            self.select_time_in_selectors()
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def dépôt_only_value_diff(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour du code REGATE dépôt avec celui du fichier. Si plantage, passer l'input radio à Oui.")
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            
            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_traitement or not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_first)
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")
    
    def dépôt_diff_non_égaux(self, numero_contrat, dictionnaire): 
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_oui = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1"))
                )
            except TimeoutException:
                logger.error("Radio_oui non trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_oui.is_displayed() or not radio_oui.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
        
            self.update_select_element(self.driver, select_element_first)
        
            self.select_time_in_selectors()
            
            try:
                div_alert = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(3) > error-component > div.alert.alert-danger"))
                )
            except TimeoutException:
                logger.error("Div Alert non trouvé.")
            pass
            
            if div_alert :
                # Utilisation de JavaScript pour cliquer sur le bouton radio_non
                self.driver.execute_script("arguments[0].click();", radio_oui)
                logger.debug("Un doublon à été détecter, passage du flag sur oui")
                time.sleep(3)
            else:
                # Sélection des rôles
                self.select_role(select_role_first, "Dépôt")
                self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")
    
    def traitement_diff_non_égaux(self, numero_contrat, dictionnaire):
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_oui = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1"))
                )
            except TimeoutException:
                logger.error("Radio_oui non trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')

            if not new_value_traitement :
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_oui.is_displayed() or not radio_oui.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass
            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()
            
            try:
                div_alert = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(3) > error-component > div.alert.alert-danger"))
                )
            except TimeoutException:
                logger.error("Div Alert non trouvé.")
            
            if div_alert :
                # Utilisation de JavaScript pour cliquer sur le bouton radio_non
                self.driver.execute_script("arguments[0].click();", radio_oui)
                logger.debug("Un doublon à été détecter, passage du flag sur oui")
                time.sleep(3)
            else:
                # Sélection des rôles
                self.select_role(select_role_first, "Dépôt")
                self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")
        
    def dépôt_only_depôt_only(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour du code REGATE avec le code REGATE dépôt du fichier. Signalement pas de rôle traitement.")
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
        
            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass
            # Vérifier si input_regate_second a une valeur
            if not input_regate_second.get_attribute("value") :
                logger.error(f"L'input traitement {input_regate_second}, le selecteur : {select_element_second} et le rôle : {select_role_second}.")
                return

            self.update_input(input_regate_first, new_value_depot)
            
            self.update_select_element(self.driver, select_element_first)
            
            self.select_time_in_selectors()

            if not select_role_second.get_attribute("value"): 
                # Sélection des rôles
                self.select_role(select_role_second, "Traitement")
                
            self.select_role(select_role_first, "Dépôt")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def dépôt_only_traitement_only(self, numero_contrat, dictionnaire):
        logger.debug("Création du bloc de traitement avec code régate traitement du fichier.")
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            
            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            
            if not new_value_traitement :
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def traitement_only_value_egaux(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour du code REGATE avec le code REGATE traitement du fichier.")
        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            try:
                radio_oui = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "g0_p159|0_c25258_v1"))
                )
            except TimeoutException:
                logger.error("Radio_oui non trouvé.")

            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_traitement or not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            if not radio_oui.is_displayed() or not radio_oui.is_enabled():
                logger.error(f"L'élément radio_non n'est pas visible ou activé pour le contrat {numero_contrat}")
                time.sleep(2)
                pass

            # Utilisation de JavaScript pour cliquer sur le bouton radio_non
            self.driver.execute_script("arguments[0].click();", radio_oui)
            logger.debug("Clic sur radio_non effectué avec JavaScript.")
            time.sleep(3)
            
            input_regate_first = selectors.get("input_first_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_role_first = selectors.get("select_first_role")

            if not all([input_regate_first, select_element_first, select_role_first]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_traitement)

            self.update_select_element(self.driver, select_element_first)

            self.select_time_in_selectors()

            # Sélection des rôles

            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def traitement_only_value_diff(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour du code REGATE traitement avec celui du fichier. Si plantage, passer l'input radio à Oui.")
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            
            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_traitement or not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_first, new_value_depot)
            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_first)
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def traitement_only_depôt_only(self, numero_contrat, dictionnaire):
        logger.debug("Mise à jour du code REGATE avec le code REGATE traitement du fichier. Signalement pas de rôle dépôt.")
        selectors = self.initialize_selectors_radio_oui()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
            
            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_depot = contrat_data.get('Nouveau Régate Dépôt', '')

            if not new_value_depot:
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_second, new_value_depot)
            
            self.update_select_element(self.driver, select_element_first)

            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Traitement")
            self.select_role(select_role_second, "Dépôt")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")

    def traitement_only_traitement_only(self, numero_contrat, dictionnaire):
        logger.debug("Création du bloc de dépôt avec code régate dépôt du fichier.")
        selectors = self.initialize_selectors()
        try:
            if not isinstance(numero_contrat, str):
                logger.error(f"Le numero_contrat doit être une chaîne de caractères, reçu: {type(numero_contrat)}")
                return
        
            contrat_data = dictionnaire.get(numero_contrat, {})
            new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
            

            if not new_value_traitement :
                logger.error(f"Valeurs manquantes pour le contrat {numero_contrat}")
                return

            input_regate_first = selectors.get("input_first_regate")
            input_regate_second = selectors.get("input_second_regate")
            select_element_first = selectors.get("select_first_etablissement")
            select_element_second = selectors.get("select_second_etablissement")
            select_role_first = selectors.get("select_first_role")
            select_role_second = selectors.get("select_second_role")

            if not all([input_regate_first, input_regate_second, select_element_first, select_element_second, select_role_first, select_role_second]):
                logger.error(f"Un ou plusieurs sélecteurs sont manquants après le clic sur radio_non pour le contrat {numero_contrat}")
                time.sleep(3)
                pass

            self.update_input(input_regate_second, new_value_traitement)
            
            self.update_select_element(self.driver, select_element_second)
            
            self.select_time_in_selectors()

            # Sélection des rôles
            self.select_role(select_role_first, "Dépôt")
            self.select_role(select_role_second, "Traitement")
            
            logger.debug("Mise à jour des inputs et sélecteurs effectuée.")
        except TimeoutException:
            logger.error("Timeout lors de la tentative de clic sur radio_non.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du contrat {numero_contrat} : {e}")
