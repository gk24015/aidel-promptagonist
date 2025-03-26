from flask import Flask, request, jsonify, render_template
import os
from DataEnrichment.entity_enricher import EntityDataEnricher
from Chatbot.chatbot import extract_and_query
from Chatbot.analysisChat import FinancialDataExtractor, append_to_file
import json
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Path to the sanctions PDF
SANCTIONS_PDF_PATH = os.path.join(os.path.dirname(__file__), 'sdnlist.pdf')

# Initialize the EntityDataEnricher with the sanctions list when the app starts
initial_enricher = EntityDataEnricher(SANCTIONS_PDF_PATH)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.txt'):
        # Use the current working directory
        file_path = os.path.join(os.getcwd(), file.filename)
        file.save(file_path)

        # Extract entities using chatbot.py
        user_query = "Extract structured JSON data from this transaction information."
        extracted_entities = extract_and_query(file_path, user_query)
        # Print the extracted entities
        print("Extracted Entities:", extracted_entities)
        if not extracted_entities:
            return jsonify({"error": "Failed to extract entities from the file."}), 400

        try:
            # Clean the extracted_entities string
            extracted_entities = extracted_entities.strip().strip('```json').strip()
            # Print the raw extracted_entities before parsing
            print("Raw Extracted Entities:", extracted_entities)
            extracted_entities = json.loads(extracted_entities)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Invalid JSON data extracted from the file."}), 400

        # Replace "null" with None or an empty string
        for entity in extracted_entities:
            for key, value in entity.items():
                if value == "null":
                    entity[key] = None

        risk_scores = []

        for entity in extracted_entities:
            payer_name = entity.get("Payer Name")
            receiver_name = entity.get("Receiver Name")

            # Process the entire entity using FinancialDataExtractor
            extractor = FinancialDataExtractor(entity)
            entity_info = extractor.extract_entity_info(entity)
            owner_info = extractor.extract_owner_info(entity)
            shareholder_info = extractor.extract_shareholder_info(entity)
            shell_company_info = extractor.extract_shell_company_info(entity)
            subsidiary_info = extractor.subsidiary_company_info(entity)
            lawsuit_info = extractor.lawsuitInfo(entity)
            
            # Get risk score using determineRisk
            risk_response = extractor.determineRisk(
                entity_info,
                owner_info,
                shareholder_info,
                shell_company_info,
                subsidiary_info,
                lawsuit_info
            )

            # Clean the risk_response string
            risk_response = risk_response.strip().strip('```json').strip()
            try:
                risk_response = json.loads(risk_response)
            except json.JSONDecodeError as e:
                return jsonify({"error": "Invalid JSON data in risk response."}), 400

            risk_scores.append(risk_response)
            print("risk_response: ", risk_response)

        return jsonify(risk_scores)

    return jsonify({"error": "Unsupported file format. Please use .txt files."}), 400

if __name__ == '__main__':
    app.run(debug=True)

