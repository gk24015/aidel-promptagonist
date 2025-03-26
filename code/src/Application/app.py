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
 
from Cyphers.Anomalies import *

from flask import Flask, jsonify
merge_info=[]
app = Flask(__name__)
custom_rules = []
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# # Initial main balance
# main_balance = 20000.00

content=""
def query_model(user_query, content):
    content=merge_info
    print(content)
    messages = [
        {"role": "system", "content": """You are a trained financial research bot.Give concise answers with evidences

"""},
        {"role": "user", "content": f"User Query: {user_query}\n\Content:\n{content}"}
    ]

    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3-0324:free",
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
     
    anomalies = {
        "Circular Ownership": detect_circular_ownership(),
        "Shell Companies": detect_shell_companies(),
        "Hidden Beneficiaries": detect_hidden_beneficiaries(),
        "High-Risk Transactions": detect_high_risk_transactions(),
        "Multiple Directorships": detect_multiple_directorships(),
        "PEP Association": detect_pep_association(),
        "High-Risk Bank Association": detect_high_risk_bank_association()
     }
    return render_template("landing.html",anomalies=anomalies)
    
def test_query_model():
    structured_data = """
    Transaction ID: T001
    Payer: Samsung Electronics Co., Ltd.
    Receiver: Apple Inc.
    Amount: 5,000,000 USD
    Date: 2025-03-20
    """

    unstructured_data = """
    On March 20, 2025, Microsoft Corporation completed a payment of 5 million USD to Amazon.com Inc. The transaction ID for this payment was T001.

    Tesla Inc. transferred 11 million USD to Apple Inc. The transfer took place on March 25, 2025, with the transaction ID T002.

    Additionally, Satya Nadella is listed as a director at Microsoft Corporation since 2014.
    Tim Cook serves as a director at Apple Inc. since 2011.
    """
    delete_all_nodes()

    print("Testing with Structured Data:")
    structured_response = query_model1("Extract transaction details, Only respond with the requested data and nothing more", structured_data)
    
   
    create_company_objects(structured_response)



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


# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     user_message = data.get('message', '')
#     return jsonify({"response": f"You said: {user_message}. This is a dummy response."})

@app.route('/submit_rule', methods=['POST'])
def submit_rule():
    data = request.get_json()
    rule = data.get('rule', '')
    if rule:
        custom_rules.append(rule)
        
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
            print(type(entity_info))
            print("Entity info done")
            owner_info = extractor.extract_owner_info(entity)
            print("Owner info done")
            merge_info=entity_info+owner_info
            print(merge_info)
            shareholder_info = extractor.extract_shareholder_info(entity)
            shell_company_info = extractor.extract_shell_company_info(entity)
            subsidiary_info = extractor.subsidiary_company_info(entity)
            lawsuit_info = extractor.lawsuitInfo(entity)
            
            
            
            print("Updated merge info",merge_info)
            # Get risk score using determineRisk
            
            risk_response = extractor.determineRisk(custom_rules,
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



    print(user_query)

if __name__ == '__main__':
    # test_query_model() 
    
    # visualize_graph();
    app.run(debug=True)


