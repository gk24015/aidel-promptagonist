from flask import Flask, render_template, request, redirect, url_for, jsonify

import re
from openai import OpenAI
from flask_cors import CORS
from DataEnrichment.entity_enricher import EntityDataEnricher
from Chatbot.chatbot import extract_and_query
from Chatbot.analysisChat import FinancialDataExtractor, append_to_file
import json
from itsdangerous import URLSafeTimedSerializer

import os


from flask import Flask, jsonify

app = Flask(__name__)
custom_rules = []
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OpenAI_api_key"),
)

# # Initial main balance
# main_balance = 20000.00

content=""
def query_model(user_query, content):
   
    """Passes user query and email list to the model for classification."""
    messages = [
        {"role": "system", "content": """You are a trained financial entity risk scorer, Based on user's query
         and the content provided as context answer queries. Keep it brief.

"""},
        {"role": "user", "content": f"User Query: {user_query}\n\nEmails:\n{content}"}
    ]

    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it:free",
        messages=messages
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def login():
    print("Entered here")
    if request.method == "POST":
        return redirect(url_for("landing"))
    return render_template("login.html")

@app.route("/landing")
def landing():
    return render_template("landing.html",emails="")


@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get("message", "").lower()

    # Dummy response logic
    if "hello" in user_message:
        bot_response = "Hello! How can I assist you today?"
    
    
    else:
        response = query_model(user_message, content)
        return jsonify({"response": response})

    return jsonify({"response": bot_response})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    return jsonify({"response": f"You said: {user_message}. This is a dummy response."})

@app.route('/submit_rule', methods=['POST'])
def submit_rule():
    data = request.get_json()
    rule = data.get('rule', '')
    if rule:
        custom_rules.append(rule)
        determineRisk()
        return jsonify({"message": "Rule added successfully!"}), 200
    return jsonify({"message": "Invalid rule!"}), 400

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
        print("Entities are ", entity)
        for entity in extracted_entities:
            payer_name = entity.get("Payer Name")
            receiver_name = entity.get("Receiver Name")

            # Process the entire entity using FinancialDataExtractor
            extractor = FinancialDataExtractor(entity)

            entity_info = extractor.extract_entity_info(entity)
            print("Entity info done")
            owner_info = extractor.extract_owner_info(entity)
            print("Owner info done")
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

def determineRisk( ):
    user_query = f''' Hi
    '''

    if custom_rules:
        user_query += "\nAdditional Custom Rules:\n" + "\n".join(custom_rules)

    user_query += '''
    Provide the output in the following format without any additional comments:
    {
        "Entity Risk ": "Low/Medium/High",
        "Entity Risk Score": "Percentage between 0 to 100, low risk meaning 0-30 medium risk score can range 30-65 and above that would be high risk"
        "Reason ": ["List key factors contributing to the risk in support of score"]
    }
    '''

    print(user_query)

if __name__ == '__main__':
    app.run(debug=True)


