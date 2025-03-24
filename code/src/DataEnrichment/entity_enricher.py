import logging
import requests
import PyPDF2
from fuzzywuzzy import fuzz

class EntityDataEnricher:
    sanctions_list = None  # Static variable to store the sanctions list

    def __init__(self, sanctions_pdf_path):
        """ Initializes the class and loads the sanctions list from a PDF if not already loaded. """
        self.data_sources = {
            "OpenCorporates": "https://api.opencorporates.com",
            "Wikidata": "https://www.wikidata.org/w/api.php",
            "SEC Tickers": "https://www.sec.gov/files/company_tickers.json",
            "SEC Data": "https://data.sec.gov",
            "World Bank": "https://api.worldbank.org/v2/country",
        }
        try:
            if EntityDataEnricher.sanctions_list is None:
                EntityDataEnricher.sanctions_list = self._load_sanctions_list(sanctions_pdf_path)
                logging.info(f"Sanctions list loaded with {len(EntityDataEnricher.sanctions_list)} entries.")
        except Exception as e:
            logging.error(f"Error loading sanctions PDF: {e}")

    def _load_sanctions_list(self, pdf_path):
        """ Reads the OFAC sanctions list from a PDF and extracts entity names. """
        logging.info("Loading OFAC Sanctions List from PDF...")
        sanctions_list = []
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        sanctions_list.extend(text.split("\n"))  # Extract each line as an entity
            logging.info(f"Successfully loaded {len(sanctions_list)} entities from the sanctions list.")
        except Exception as e:
            logging.error(f"Error loading sanctions PDF: {e}")
        return sanctions_list

    def enrich_entity(self, entity_name):
        """ Fetches data from various sources and checks against the sanctions list. """
        logging.info(f"Processing entity: {entity_name}")
        enriched_data = {"name": entity_name, "Wikidata": "", "SEC EDGAR": "", "Sanctioned": ""}  # Ensure empty defaults
        failed_apis = []

        if not self.fetch_wikidata(entity_name, enriched_data):
            failed_apis.append("Wikidata")

        if not self.fetch_sec_edgar(entity_name, enriched_data):
            failed_apis.append("SEC EDGAR")

        if not self.fetch_world_bank_data(entity_name, enriched_data):
            failed_apis.append("World Bank")

        try:
            self.check_sanctions_list(entity_name, enriched_data)
        except Exception as e:
            logging.error(f"Error checking sanctions list: {e}")
            failed_apis.append("OFAC Sanctions List")

        return enriched_data, failed_apis

    def fetch_wikidata(self, entity_name, enriched_data):
        """ Fetches data from Wikidata API. """
        logging.info(f"Fetching data from Wikidata for entity: {entity_name}")
        params = {"action": "wbsearchentities", "search": entity_name, "format": "json", "language": "en"}

        try:
            response = requests.get(self.data_sources["Wikidata"], params=params)
            response.raise_for_status()
            enriched_data["Wikidata"] = response.json().get("search", "")
            logging.info(f"Data retrieved successfully from Wikidata for {entity_name}")
            return True
        except requests.RequestException as e:
            logging.warning(f"Failed to retrieve Wikidata data for {entity_name}: {e}")
            return False

    def fetch_sec_edgar(self, entity_name, enriched_data):
        """ Fetches CIK from SEC API and retrieves related data using fuzzy matching. """
        logging.info(f"Checking SEC EDGAR filings for entity: {entity_name}")

        try:
            # Fetch the list of companies and their CIKs
            response = requests.get(self.data_sources["SEC Tickers"], headers={"User-Agent": "EntityDataEnricher@gmail.com"})
            response.raise_for_status()
            company_data = response.json()
            cik = None
            max_score = 0
            
            for company in company_data.values():
                score = fuzz.token_sort_ratio(entity_name.lower(), company["title"].lower())
                if score > max_score and score > 80:  # Adjust threshold as needed
                    max_score = score
                    cik = str(company["cik_str"]).zfill(10)  # Ensure 10-digit CIK

            if not cik:
                logging.warning(f"No CIK found for {entity_name}")
                return False

            # Fetch SEC data
            sec_data_url = f"{self.data_sources['SEC Data']}/submissions/CIK{cik}.json"
            sec_data_response = requests.get(sec_data_url, headers={"User-Agent": "EntityDataEnricher/1.0"})
            
            if sec_data_response.status_code != 200:
                logging.error(f"Failed to retrieve SEC EDGAR data for CIK {cik}. Response: {sec_data_response.status_code}, {sec_data_response.text}")
                return False
            
            enriched_data["SEC EDGAR"] = sec_data_response.json()
            #logging.info(f"SEC EDGAR data retrieved for CIK {cik}: {enriched_data['SEC EDGAR']}")
            return True
        except requests.RequestException as e:
            logging.warning(f"Failed to retrieve SEC EDGAR filings for {entity_name}: {e}")
            return False

    def check_sanctions_list(self, entity_name, enriched_data):
        """ Checks if the entity is in the sanctions list using fuzzy matching. """
        logging.info(f"Checking OFAC Sanctions List for entity: {entity_name}")

        try:
            for sanctioned_entity in EntityDataEnricher.sanctions_list:
                match_score = fuzz.token_sort_ratio(entity_name.lower(), sanctioned_entity.lower())

                if match_score > 80:  # Adjust threshold as needed
                    enriched_data["Sanctioned"] = "Yes"
                    logging.info(f"Match found! {entity_name} is in the sanctions list (Score: {match_score}).")
                    return True

            enriched_data["Sanctioned"] = "No"
            logging.info(f"{entity_name} is NOT in the sanctions list.")
            return False

        except Exception as e:
            logging.error(f"Error during sanctions check: {e}")
            raise
        

    def fetch_world_bank_data(self, entity_name, enriched_data):
        """ Fetches document metadata from the World Bank API. """
        logging.info(f"Fetching data from World Bank for entity: {entity_name}")
        try:
            params = {
                "format": "json",
                "qterm": entity_name,
                "display_title": "water",
                "fl": "display_title",
                "rows": 20,
                "os": 100
            }
            response = requests.get(self.data_sources["World Bank"], params=params)
            response.raise_for_status()
            enriched_data["World Bank"] = response.json()
            return True
        except requests.RequestException as e:
            logging.warning(f"Failed to retrieve World Bank data for {entity_name}: {e}")
            return False

