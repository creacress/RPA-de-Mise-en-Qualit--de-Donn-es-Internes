from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import pandas as pd
from debug import log_error_and_capture_screenshot, setup_logger

# Initatilisation du debug
logger = setup_logger()

class FrequenceoCase:
    def __init__(self, driver):
        self.driver = driver
    def is_select_value_present(self, select_selector):
        """Verifie si un element select a une valeur selectionnee."""
        try:
            select_element = Select(
                self.driver.find_element(By.CSS_SELECTOR, select_selector)
            )
            return select_element.first_selected_option.text.strip() != ""
        except NoSuchElementException:
            return False

    def is_specific_option_selected(self, select_selector, option_text):
        """Verifie si une option specifique est selectionnee dans un element select."""
        try:
            select_element = Select(
                self.driver.find_element(By.CSS_SELECTOR, select_selector)
            )
            selected_option_text = select_element.first_selected_option.text.strip()
            return selected_option_text == option_text
        except NoSuchElementException:
            logger.debug(f"Selecteur '{select_selector}' non trouve.")
            return False
        
    def submit_frequenceo(driver):
        # Trouver et cliquer sur le bouton de soumission
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "#odcFormCPV > button")
                    )
                )
                submit_button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_changes(
                        "https://www.exemple.intranet.fr"
                    )
                )
                logger.info("Formulaire soumis avec succes.")
            
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
                driver.save_screenshot("debug_screenshot_erreur_soumission_proxicompte.png")
    
    def initialize_selectors(self, driver):
        selectors = {}
        try:
            wait = WebDriverWait(driver, 10)
            # Initialiser les sélecteurs communs
            selectors["coordonees_interlocuteur_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cptLeft > div:nth-child(2) select")))
            selectors["adresse_facturation_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cptLeft > div:nth-child(3) select")))
            selectors["adresse_prestation_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cptLeft > div:nth-child(3) select")))
            selectors["input_first_regate_frequenceo"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p10083|0_r16735_c16736")))
            selectors["select_first_etablissement_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p10083\\|0_r16735\\[0\\] critere-form:nth-child(3) select")))
            selectors["select_first_role_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#g0_p10083\\|0_r16735\\[0\\] critere-form:nth-child(5) select")))

            if selectors["button_delete_depot"].is_displayed():
                # Sélecteurs supplémentaires si le bouton delete est présent
                selectors["input_second_regate_frequenceo"] = wait.until(EC.presence_of_element_located((By.ID, "g0_p10083|0_r16735_c16736[0]")))
                selectors["select_second_etablissement_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#\\[g0_p10083\\|0_r16735\\[0\\]\\] critere-form:nth-child(3) select")))
                selectors["select_second_role_frequenceo"] = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#\\[g0_p10083\\|0_r16735\\[0\\]\\] critere-form:nth-child(5) select")))

        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des sélecteurs: {e}")
        
        return selectors
    
    def compare_input_values(self, driver, selectors, current_value, expected_value, numero_contrat):
        if str(current_value) != str(expected_value):
            # Creation locale des objets Select
            select_first_etablissement = Select(selectors["select_first_etablissement_frequenceo"])
            select_adresse_facturation = Select(selectors["adresse_facturation_frequenceo"])

            # Verifie que les objets crees sont des instances de Select
            if not isinstance(select_first_etablissement, Select) or not isinstance(select_adresse_facturation, Select) :
                logger.error("Les elements fournis ne sont pas des elements de selection valides.")
                return False

            # Recuperation des valeurs à partir des elements Select
            etablissement_value_first = select_first_etablissement.first_selected_option.get_attribute('title') if select_first_etablissement else "Non trouve"
            select_adresse_facturation = select_adresse_facturation.first_selected_option.get_attribute('title') if select_adresse_facturation else "Non trouve"

            # Creation du message d'erreur sous forme de dictionnaire
            error_info = {
                "message": "Erreur de validation pour le contrat",
                "numero_contrat": numero_contrat,
                "adresse_facturation": select_adresse_facturation,
                "valeur_attendue": expected_value,
                "valeur_trouvee": current_value,
                "premier_etablissement": etablissement_value_first
            }
            logger.error(error_info)

            return False

        return True
    
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
    
    def check_and_select_first_option(select_element, element_name):
        """
        Vérifie si une option est sélectionnée dans un élément select et sélectionne la première option si aucune n'est sélectionnée.
        
        :param select_element: L'élément select à vérifier.
        :param element_name: Nom de l'élément pour le logging.
        """
        if select_element:
            select_obj = Select(select_element)
            selected_option = select_obj.first_selected_option
            if selected_option and selected_option.get_attribute('value'):
                logger.debug(f"Option sélectionnée pour {element_name}: {selected_option.text}")
            else:
                # Aucune option sélectionnée, on sélectionne la première option disponible
                logger.debug(f"Aucune option sélectionnée pour {element_name}, sélection de la première option disponible.")
                if select_obj.options:
                    select_obj.select_by_index(0)
                    logger.debug(f"Première option sélectionnée pour {element_name}: {select_obj.first_selected_option.text}")
                else:
                    logger.debug(f"Aucune option disponible dans le sélecteur pour {element_name}.")
        else:
            logger.debug(f"Élément select pour {element_name} non trouvé.")

    def traitement_frequenceo(self, driver, wait, numero_contrat, dictionnaire):
        logger.debug('Debut du traitement pour le contrat numéro: {}'.format(numero_contrat))
        selectors = self.initialize_selectors(driver)

        if not selectors:
            logger.debug('Aucun selecteur initialise pour le contrat numero: {}'.format(numero_contrat))
            return

        input_element = selectors.get("input_first_regate_frequenceo")
        if not input_element:
            logger.debug('Element input non trouve, contrat numero: {}'.format(numero_contrat))
            return
        select_element = selectors.get("select_first_etablissement_frequenceo")
        coordonees_interlocuteur_frequenceo = selectors.get("coordonees_interlocuteur_frequenceo")
        adresse_facturation_frequenceo = selectors.get("adresse_facturation_frequenceo")
        adresse_prestation_frequenceo = selectors.get("adresse_prestation_frequenceo")
        
        # Vérification et sélection d'option
        self.check_and_select_first_option(adresse_facturation_frequenceo, "adresse de facturation")
        self.check_and_select_first_option(coordonees_interlocuteur_frequenceo, "coordonnées interlocuteur")
        self.check_and_select_first_option(adresse_prestation_frequenceo, "adresse de prestation")

        # Lecture du fichier Excel pour vérifier les valeurs "Dépôt" et "Traitement"
        excel_path = 'MEQ - Fichier test pour le robot.xlsx'
        df = pd.read_excel(excel_path)

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
        
        
        contrat_data = dictionnaire.get(numero_contrat, {})
        new_value_traitement = contrat_data.get('Nouveau Régate Traitement', '')
        # Mise à jour des entrées et sélection pour Dépôt
        self.update_input(input_element, new_value_traitement)
        self.update_select_element(self.driver, select_element)
        logger.info("Traitement complet pour le contrat numero: {}".format(numero_contrat))
        # Envoi du formulaire
        # self.submit_frequenceo(driver)
        logger.debug("Contrat traité")

    
    def handle_case_frequenceo(self, driver, wait, numero_contrat, dictionnaire):
        logger.debug("Debut du cas Fequenceo")
        try:
            h1_text = driver.find_element(By.TAG_NAME, "h1").text
            logger.debug(f"Texte de l en tete H1 : {h1_text}")
            if "Frequenceo" in h1_text:
                logger.debug("Cas Frequenceo")
                self.traitement_frequenceo(driver, wait, numero_contrat, dictionnaire)

            elif "Destineo kdo" in h1_text:
                logger.debug("Cas Destineo KDO")
                self.traitement_frequenceo(driver, wait, numero_contrat, dictionnaire)
            
            elif "Destineo monde primo" in h1_text:
                logger.debug("Cas Destineo monde primo")
            
            elif "Destineo monde volume" in h1_text:
                logger.debug("Cas Destineo monde volume")
        except Exception as e:
            logger.exception(f"Service non reconnu : {e}")
            log_error_and_capture_screenshot(driver, "Erreur_service_non_reconnu", e)
