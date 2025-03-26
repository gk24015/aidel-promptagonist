from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
app = Flask(__name__)
import re
from openai import OpenAI
from flask_cors import CORS
import os
from dotenv import load_dotenv
import pandas as pd
import PyPDF2

from Cyphers.Nodes import *
from db.neo4j_connect import *
from Cyphers.Relationships import * 
from Cyphers.Anomalies import *
from Cyphers.View import *

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OpenAI_api_key"),
)

def query_model(user_query, content):

    
   
   
    messages = [
        {"role": "system", "content": """You are an AI designed to extract financial data from structured or unstructured text.

Your Task:
Extract transaction details from the file.

Identify the payer and receiver companies from the transaction data.

Extract relevant information for the companies using their names.

Extract any directorship information available.
On fileds like company_id, or personId just give a unique id maybe counter to each
Return the data as a list of Python objects in the following format:

         
Output Format (One Object Per Transaction)

[
    {
        "transaction_id": "<transaction_id>",
        "receiver": {
            "company_id": "company_id",
            "name": "<receiver_company_name>",
            "country": "determine the country using company name",
            "industry": "determine the industry using company name",
            "incorporation_date": "determine the incorporation date using company name",
            "revenue": "determine the revenue using company name",
            "employees": "determine no of total employees using company name",
            
        },
        "payer": {
            "company_id": "company_id",
            "name": "<receiver_company_name>",
            "country": "determine the country using company name",
            "industry": "determine the industry using company name",
            "incorporation_date": "determine the incorporation date using company name",
            "revenue": "determine the revenue using company name",
            "employees": "determine no of total employees using company name",
        },
        "Owner": 
            {
                "person_id": "person_id",
                "name": "determine owner name using company name",
                "dob": "<person_dob>",
                "nationality": "owner country given company name",
                "role": "detrmine role in company", 
                "since": "when they joined the company as owner?",

            }
 
        "amount": <amount>,
        "currency": "<currency>",
        "date": "<transaction_date>"
    },
    # Repeat for other transactions
]
Extraction Guidelines:
Identify Payer and Receiver:

Extract the payer and receiver company names from each transaction.

Search and extract relevant company details using their names.

Company Information:

For each company, using the company name find details like company_id, country, industry, status, incorporation_date, revenue, employees, is_listed, and ownership_type.

If any detail is missing or not available, return "None".

Directorship Information:

Using company name find out the owner details
Extract details like person_id, name, dob, nationality, role, and since date.

If no relevant directorship information is available, return an empty list.

Transaction Details:

Ensure the transaction_id, amount, currency, and date fields are correctly extracted.

Validate the data for consistency.

Error Handling:

If data is incomplete, ambiguous, or not found, mark missing fields as "None" instead of guessing.

"""},
        {"role": "user", "content": f"User Query: {user_query}\n\nContent:\n{content}"}
    ]
    completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=messages
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def test_query_model():
    structured_data = """
    Transaction ID: T001
    Payer: Microsoft Corporation
    Receiver: Amazon.com Inc.
    Amount: 5,000,000 USD
    Date: 2025-03-20
    """

    unstructured_data = """
    On March 20, 2025, Microsoft Corporation completed a payment of 5 million USD to Amazon.com Inc. The transaction ID for this payment was T001.

    Tesla Inc. transferred 11 million USD to Apple Inc. The transfer took place on March 25, 2025, with the transaction ID T002.

    Additionally, Satya Nadella is listed as a director at Microsoft Corporation since 2014.
    Tim Cook serves as a director at Apple Inc. since 2011.
    """

    print("Testing with Structured Data:")
    structured_response = query_model("Extract transaction details, Only respond with the requested data and nothing more", structured_data)
    
   
    create_company_objects(structured_response)

import json

def create_company_objects(response_data):
    try:
        if isinstance(response_data, str):
            response_data = response_data.strip().strip("```json").strip("```")
            transactions = json.loads(response_data)
        else:
            transactions = response_data
        
        for transaction in transactions:
            for company_role in ['payer', 'receiver']:
                company = transaction.get(company_role, {})
                if company:
                    
                    create_company(
                        company_id="ab12",
                        name=company.get('name', None),
                        country=company.get('country', None),
                        industry=company.get('industry', None),
                        status=company.get('status', None),
                        incorporation_date=company.get('incorporation_date', None),
                        revenue=company.get('revenue', None),
                        employees=company.get('employees', None),
                        is_listed=company.get('is_listed', None),
                        risk_score=None,
                        ownership_type=company.get('ownership_type', None),
                    )
    except Exception as e:
        print(f"Error while creating company objects: {e}")


# Run the function
test_query_model()


test_query_model()

    

