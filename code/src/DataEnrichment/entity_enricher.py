import logging
import requests
import PyPDF2
from fuzzywuzzy import fuzz
import yfinance as yf

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
            "SEC Enforcement Actions": "https://api.sec-api.io/sec-enforcement-actions",
            "SEC Litigation Releases": "https://api.sec-api.io/sec-litigation-releases",
            "SEC Form 8-K": "https://api.sec-api.io/form-8k"
        }
        self.api_keys = [
            "0ef05ff990c13ce4d2ede57adc51c0eede0c77be53cad777e17d3cb74da7d7d7",
            "another_api_key_here",
            "yet_another_api_key_here"
        ]
        self.cik = None
        self.ticker = None
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
        enriched_data = {
            "name": entity_name,
            "Sanctioned": "",  # Move "Sanctioned" to the top
            "SEC Enforcement Actions": "", 
            "SEC Litigation Releases": "",  # Add new field for SEC Litigation Releases
            "SEC Form 8-K": "",  # Add new field for SEC Form 8-K
            "Wikidata": "",
            "SEC EDGAR": "",  
            "SEC Facts": "",
            "World Bank": "",
        }
        failed_apis = []

        self.cik = self._get_cik(entity_name)
        self.ticker = self._get_ticker(entity_name)
        if not self.cik:
            logging.warning(f"No CIK found for {entity_name}")
            failed_apis.append("CIK")

        if not self.ticker:
            logging.warning(f"No ticker symbol found for {entity_name}")
            failed_apis.append("Ticker")

        if not self.fetch_wikidata(entity_name, enriched_data):
            failed_apis.append("Wikidata")

        if not self.fetch_sec_edgar(entity_name, enriched_data):
            failed_apis.append("SEC EDGAR")

        if not self.fetch_world_bank_data(entity_name, enriched_data):
            failed_apis.append("World Bank")

        if not self.fetch_sec_enforcement_actions(entity_name, enriched_data):
            failed_apis.append("SEC Enforcement Actions")

        if not self.fetch_sec_litigation_releases(entity_name, enriched_data):
            failed_apis.append("SEC Litigation Releases")

        if not self.fetch_sec_form_8k(entity_name, enriched_data):
            failed_apis.append("SEC Form 8-K")

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

        if not self.cik:
            return False

        try:
            sec_data_url = f"{self.data_sources['SEC Data']}/submissions/CIK{self.cik}.json"
            sec_facts_url = f"{self.data_sources['SEC Data']}/api/xbrl/companyfacts/CIK{self.cik}.json"

            sec_data_response = requests.get(sec_data_url, headers={"User-Agent": "EntityDataEnricher/1.0"})
            sec_facts_response = requests.get(sec_facts_url, headers={"User-Agent": "EntityDataEnricher/1.0"})
            
            if sec_data_response.status_code == 200:
                sec_data_data = sec_data_response.json()
                sec_data_data.pop("filings", None)  # Remove "filings" key if it exists
                enriched_data["SEC EDGAR"] = sec_data_data  # Assign to the correct key
            else:
                logging.error(f"Failed to retrieve SEC EDGAR data for CIK {self.cik}.")
            
            if sec_facts_response.status_code == 200:
                sec_facts_data = sec_facts_response.json()
                enriched_data["SEC Facts"] = sec_facts_data
            else:
                logging.warning(f"Failed to retrieve SEC Facts data for CIK {self.cik}.")
                
            return True
        except requests.RequestException as e:
            logging.warning(f"Failed to retrieve SEC EDGAR filings for {entity_name}: {e}")
            return False

    def _get_cik(self, entity_name):
        """ Extracts CIK from SEC Tickers using fuzzy matching. """
        try:
            response = requests.get(self.data_sources["SEC Tickers"], headers={"User-Agent": "EntityDataEnricher@gmail.com"})
            response.raise_for_status()
            company_data = response.json()
            cik = None
            max_score = 0
            
            for company in company_data.values():
                score = fuzz.token_sort_ratio(entity_name.lower(), company["title"].lower())
                if score > max_score and score > 80:
                    max_score = score
                    cik = str(company["cik_str"]).zfill(10)

            return cik
        except requests.RequestException as e:
            logging.warning(f"Failed to retrieve CIK for {entity_name}: {e}")
            return None

    def _get_ticker(self, company_name):
        """ Retrieves the stock ticker symbol using yfinance. """
        try:
            ticker = yf.Ticker(company_name)
            ticker_info = ticker.info
            ticker_symbol = ticker_info.get('symbol', None)
            if ticker_symbol:
                return ticker_symbol
            else:
                logging.warning(f"Ticker symbol for '{company_name}' not found.")
                return None
        except Exception as e:
            logging.warning(f"Error retrieving ticker symbol for '{company_name}': {e}")
            return None

    def fetch_sec_enforcement_actions(self, entity_name, enriched_data):
        """ Fetches data from SEC Enforcement Actions API. """
        logging.info(f"Fetching SEC Enforcement Actions for entity: {entity_name}")
        query = {
            "query": f"entities.cik:{self.cik}",
            "from": 0,
            "size": 50,
            "sort": [{"releasedAt": {"order": "desc"}}]
        }

        for api_key in self.api_keys:
            try:
                response = requests.post(f"{self.data_sources['SEC Enforcement Actions']}?token={api_key}", json=query)
                response.raise_for_status()
                enriched_data["SEC Enforcement Actions"] = response.json()
                logging.info(f"Data retrieved successfully from SEC Enforcement Actions for {entity_name}")
                return True
            except requests.RequestException as e:
                logging.warning(f"Failed to retrieve SEC Enforcement Actions for {entity_name} with API key {api_key}: {e}")

        return False

    def fetch_sec_litigation_releases(self, entity_name, enriched_data):
        """ Fetches data from SEC Litigation Releases API. """
        logging.info(f"Fetching SEC Litigation Releases for entity: {entity_name}")
        query = {
            "query": f"entities.cik:{self.cik}",
            "from": 0,
            "size": 50,
            "sort": [{"releasedAt": {"order": "desc"}}]
        }

        for api_key in self.api_keys:
            try:
                response = requests.post(f"{self.data_sources['SEC Litigation Releases']}?token={api_key}", json=query)
                response.raise_for_status()
                enriched_data["SEC Litigation Releases"] = response.json()
                logging.info(f"Data retrieved successfully from SEC Litigation Releases for {entity_name}")
                return True
            except requests.RequestException as e:
                logging.warning(f"Failed to retrieve SEC Litigation Releases for {entity_name} with API key {api_key}: {e}")

        return False

    def fetch_sec_form_8k(self, entity_name, enriched_data):
        """ Fetches data from SEC Form 8-K API. """
        logging.info(f"Fetching SEC Form 8-K for entity: {entity_name}")

        if not self.ticker:
            return False

        query = {
            "query": f"item4_01:* AND ticker:{self.ticker}",
            "from": "0",
            "size": "50"
        }

        for api_key in self.api_keys:
            try:
                response = requests.post(f"{self.data_sources['SEC Form 8-K']}?token={api_key}", json=query)
                response.raise_for_status()
                enriched_data["SEC Form 8-K"] = response.json()
                logging.info(f"Data retrieved successfully from SEC Form 8-K for {entity_name}")
                return True
            except requests.RequestException as e:
                logging.warning(f"Failed to retrieve SEC Form 8-K for {entity_name} with API key {api_key}: {e}")

        return False

    def check_sanctions_list(self, entity_name, enriched_data):
        """ Checks if the entity is in the sanctions list using fuzzy matching. """
        logging.info(f"Checking OFAC Sanctions List for entity: {entity_name}")

        try:
            for sanctioned_entity in EntityDataEnricher.sanctions_list:
                match_score = fuzz.token_sort_ratio(entity_name.lower(), sanctioned_entity.lower())

                if match_score > 80:
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
            params = {"format": "json", "qterm": entity_name, "display_title": "water", "fl": "display_title", "rows": 20, "os": 100}
            response = requests.get(self.data_sources["World Bank"], params=params)
            response.raise_for_status()
            enriched_data["World Bank"] = response.json()
            return True
        except requests.RequestException as e:
            logging.warning(f"Failed to retrieve World Bank data for {entity_name}: {e}")
            return False
