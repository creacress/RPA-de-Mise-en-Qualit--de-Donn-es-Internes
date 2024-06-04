import pandas as pd

def extract_contrat_numbers_to_json(excel_path, json_path):
    """
    Extrait les numéros de contrat d'un fichier Excel et les enregistre dans un fichier JSON.
    
    :param excel_path: Chemin vers le fichier Excel.
    :param json_path: Chemin vers le fichier JSON où les numéros de contrat seront enregistrés.
    """
    # Lecture du fichier Excel
    df = pd.read_excel(excel_path)

    # Extraction de la colonne 'N°Contrat'
    numeros_contrat = df['N°Contrat']

    # Conversion en JSON et enregistrement dans un fichier
    numeros_contrat.to_json(json_path, orient='index')
