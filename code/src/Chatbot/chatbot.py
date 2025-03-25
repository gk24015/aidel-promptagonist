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
# Load environment variables from .env file
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OpenAI_api_key"),
)

def query_model(user_query, content):

    
   
    """Passes user query and email list to the model for classification."""
    messages = [
        {"role": "system", "content": """You are an expert in financial data extraction. I have transaction data that may be in structured (tabular with columns) or unstructured (text with fields and descriptions) format. Your task is to convert the data into a structured JSON format.

Instructions:

Analyze and identify Payer Name and Receiver Name (Entity Names).

Extract other relevant fields such as:

TransactionId

Date (if available)

Amount

Currency Exchange

Transaction Type

Address

Reference

Receiver Country (if applicable)

For structured data, convert each row into a JSON object.

For unstructured data, intelligently parse and normalize the fields into the JSON format.

If there are multiple transactions in the input, create a list of JSON objects.

Output Format:
[
  {
    "TransactionId": "123456",
    "Payer Name": "John Doe",
    "Receiver Name": "Alice Smith",
    "Date": "2025-03-20",
    "Amount": 500.0,
    "Currency Exchange": "USD to EUR",
    "Transaction Type": "Wire Transfer",
    "Address": "123 Main St, NY",
    "Reference": "Payment for Invoice #123",
    "Receiver Country": "Germany"
  },
  ...
]
Return "null" if any field is missing.

Ensure the output is clean, with no redundant or irrelevant information.

"""},
        {"role": "user", "content": f"User Query: {user_query}\n\nContent:\n{content}"}
    ]
    completion = client.chat.completions.create(
    model="google/gemma-3-27b-it:free",
    messages=messages
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content



def extract_and_query(file_path, user_query):
    try:
        # Determine file type
        if file_path.lower().endswith('.pdf'):
            content = extract_pdf(file_path)
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            content = extract_excel(file_path)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            raise ValueError("Unsupported file format. Please use PDF, Excel, or TXT.")
        
        # Pass to your model
        return query_model(user_query, content)

    except Exception as e:
        print(f"Error: {e}")
        return None

# Extract PDF content
def extract_pdf(file_path):
    content = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content.append(page.extract_text())
    return "\n".join(content)

# Extract Excel content
def extract_excel(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        content = []
        for sheet_name, data in df.items():
            content.append(f"Sheet: {sheet_name}\n{data.to_string(index=False)}")
        return "\n\n".join(content)
    except Exception as e:
        raise Exception(f"Error reading Excel file: {e}")

    

# Example Usage
file_path = 'data.xlsx'
user_query = "Extract structured JSON data from this transaction information."
result = extract_and_query(file_path, user_query)
print(result)