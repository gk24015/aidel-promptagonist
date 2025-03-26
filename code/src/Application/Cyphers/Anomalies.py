
import networkx as nx
import matplotlib.pyplot as plt
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
from neo4j import GraphDatabase
import os
# Load environment variables from .env file
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
# ✅ Detect Circular Ownership
def detect_circular_ownership():
    query = """
    MATCH path=(c1:Company)-[:OWNS*1..5]->(c2:Company)
    WHERE c1 = c2
    RETURN path
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])

# ✅ Detect Shell Companies
def detect_shell_companies():
    query = """
    MATCH (c:Company)
    WHERE c.revenue < 10000 
      OR c.employees < 5
      AND EXISTS {
        MATCH (c)-[:TRANSACTED_WITH]->(other:Company)
        WHERE other.revenue > 1000000
      }
    RETURN c
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])

# ✅ Detect Hidden Beneficiaries
def detect_hidden_beneficiaries():
    query = """
    MATCH path=(c1:Company)-[:OWNS*2..6]->(c2:Company)
    WHERE c1 <> c2
    RETURN path
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])

# ✅ Detect High-Risk Transactions
def detect_high_risk_transactions():
    query = """
    MATCH (c1:Company)-[t:TRANSACTED_WITH]->(c2:Company)
    WHERE t.amount > 1000000 AND c1.country <> c2.country
    RETURN c1.name AS Sender, c2.name AS Receiver, t.amount AS Amount, t.currency AS Currency
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])

# ✅ Detect Multiple Directorships
def detect_multiple_directorships():
    query = """
    MATCH (p:Person)-[:DIRECTOR_OF]->(c1:Company), (p)-[:DIRECTOR_OF]->(c2:Company)
    WHERE c1 <> c2
    RETURN p.name AS Person, COUNT(DISTINCT c1) AS num_companies
    HAVING num_companies > 5
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])

# ✅ Detect PEP Association
def detect_pep_association():
    query = """
    MATCH (p:Person)-[:DIRECTOR_OF|SHAREHOLDER_OF]->(c:Company)
    WHERE p.role = "PEP"
    RETURN p.name AS PEP_Name, c.name AS Company_Name
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])

# ✅ Detect High-Risk Bank Association
def detect_high_risk_bank_association():
    query = """
    MATCH (c:Company)-[:USES_BANK]->(b:Bank)
    WHERE b.risk_score > 8
    RETURN c.name AS Company_Name, b.name AS Bank_Name, b.risk_score AS Risk_Score
    """
    result = execute_query(query)
    return (True, result) if result else (False, [])



def query_model1(user_query, content):

    
   
   
    messages = [
        {"role": "system", "content": """You are an AI designed to extract financial data from structured or unstructured text.

Your Task:
Extract transaction details from the file.

Identify the payer and receiver companies from the transaction data.

Extract relevant information for the companies using their names.

Extract any directorship information available.
On fileds like company_id, or personId just give a unique alpha-numeric value
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
        "receiver Owner": 
            {
                "person_id": "person_id",
                "name": "determine owner name using company name",
                "dob": "<person_dob>",
                "nationality": "owner country given company name",
                "role": "detrmine role in company", 
                "since": "when they joined the company as owner?",

            },
         "payer Owner": 
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
                        company_id=company.get('company_id'),
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
                    ownerType = company_role + " Owner"
                    owner = transaction.get(ownerType, {})
                    if owner:
                        create_person(
                            person_id=owner.get('person_id'),
                            name=owner.get('name', None),
                            dob=owner.get('dob', None),
                            nationality=owner.get('nationality', None),
                            role=owner.get('role', None),
                            since=owner.get('since', None)
                        )
                        create_directorship(
                            company_id=company.get('company_id'),
                            person_id=owner.get('person_id'),
                            since=owner.get('since', None),
                            role=owner.get('role', None),
                        )

            create_transaction(
                company_id_1=transaction['payer'].get('company_id'),
                company_id_2=transaction['receiver'].get('company_id'),
                transaction_id=transaction.get('transaction_id'),
                amount=transaction.get('amount'),
                currency=transaction.get('currency'),
                date=transaction.get('date')
            ) 
    except Exception as e:
        print(f"Error while creating company objects: {e}")


def delete_all_nodes():
    query = "MATCH (n) DETACH DELETE n"
    try:
        execute_query(query)
        print("✅ All nodes and relationships deleted successfully!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

load_dotenv()
import os
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Create a driver instance
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def execute_query(query, parameters=None):
    try:
        with driver.session() as session:
            result = session.run(query, parameters)
            print("Query Successfull")
            return [record for record in result]
    except Exception as e:
        print(f"❌ Query failed: {e}")

# Close the driver
def close_connection():
    driver.close()


# Create a Company node
def create_company(company_id, name, country, industry, status, incorporation_date, revenue, employees, is_listed, risk_score, ownership_type, parent_company_id=None):
    query = """
    CREATE (c:Company {
        company_id: $company_id,
        name: $name,
        country: $country,
        industry: $industry,
        status: $status,
        incorporation_date: $incorporation_date,
        revenue: $revenue,
        employees: $employees,
        is_listed: $is_listed,
        risk_score: $risk_score,
        ownership_type: $ownership_type,
        parent_company_id: $parent_company_id
    })
    RETURN c
    """
    params = {
        "company_id": company_id,
        "name": name,
        "country": country,
        "industry": industry,
        "status": status,
        "incorporation_date": incorporation_date,
        "revenue": revenue,
        "employees": employees,
        "is_listed": is_listed,
        "risk_score": risk_score,
        "ownership_type": ownership_type,
        "parent_company_id": parent_company_id
    }
    return execute_query(query, params)

# Create a Person node
def create_person(person_id, name, dob, nationality, role, since, risk_score=None):
    query = """
    CREATE (p:Person {
        person_id: $person_id,
        name: $name,
        dob: $dob,
        nationality: $nationality,
        role: $role,
        since: $since,
        risk_score: $risk_score
    })
    RETURN p
    """
    params = {
        "person_id": person_id,
        "name": name,
        "dob": dob,
        "nationality": nationality,
        "role": role,
        "since": since,
        "risk_score": risk_score
    }
    return execute_query(query, params)

# Create an Address node
def create_address(address_id, street, city, state, country, zip_code, lat=None, lon=None):
    query = """
    CREATE (a:Address {
        address_id: $address_id,
        street: $street,
        city: $city,
        state: $state,
        country: $country,
        zip_code: $zip_code,
        lat: $lat,
        lon: $lon
    })
    RETURN a
    """
    params = {
        "address_id": address_id,
        "street": street,
        "city": city,
        "state": state,
        "country": country,
        "zip_code": zip_code,
        "lat": lat,
        "lon": lon
    }
    return execute_query(query, params)

# Create a Bank node
def create_bank(bank_id, name, country, swift_code, risk_score=None):
    query = """
    CREATE (b:Bank {
        bank_id: $bank_id,
        name: $name,
        country: $country,
        swift_code: $swift_code,
        risk_score: $risk_score
    })
    RETURN b
    """
    params = {
        "bank_id": bank_id,
        "name": name,
        "country": country,
        "swift_code": swift_code,
        "risk_score": risk_score
    }
    return execute_query(query, params)

# Create a Transaction node
def create_transaction(transaction_id, amount, currency, date, txn_type, status, origin_country, destination_country, risk_score=None):
    query = """
    CREATE (t:Transaction {
        transaction_id: $transaction_id,
        amount: $amount,
        currency: $currency,
        date: $date,
        type: $txn_type,
        status: $status,
        origin_country: $origin_country,
        destination_country: $destination_country,
        risk_score: $risk_score
    })
    RETURN t
    """
    params = {
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "date": date,
        "txn_type": txn_type,
        "status": status,
        "origin_country": origin_country,
        "destination_country": destination_country,
        "risk_score": risk_score
    }
    return execute_query(query, params)


def update_company(company_id, updated_values):
    set_clauses = ", ".join([f"c.{key} = '{value}'" if isinstance(value, str) else f"c.{key} = {value}"
                             for key, value in updated_values.items()])
    query = f"""
    MATCH (c:Company {{company_id: '{company_id}'}})
    SET {set_clauses}
    RETURN c
    """
    return execute_query(query)


# Ownership Relationship: Company OWNS Company
def create_ownership(company_id_1, company_id_2, ownership_percentage, is_direct):
    query = """
    MATCH (c1:Company {company_id: $company_id_1})
    MATCH (c2:Company {company_id: $company_id_2})
    CREATE (c1)-[:OWNS {
        ownership_percentage: $ownership_percentage,
        is_direct: $is_direct
    }]->(c2)
    RETURN c1, c2
    """
    params = {
        "company_id_1": company_id_1,
        "company_id_2": company_id_2,
        "ownership_percentage": ownership_percentage,
        "is_direct": is_direct
    }
    return execute_query(query, params)

# Directorship Relationship: Person DIRECTOR_OF Company
def create_directorship(person_id, company_id, since, role):
    query = """
    MATCH (p:Person {person_id: $person_id})
    MATCH (c:Company {company_id: $company_id})
    CREATE (p)-[:DIRECTOR_OF {
        since: $since,
        role: $role
    }]->(c)
    RETURN p, c
    """
    params = {
        "person_id": person_id,
        "company_id": company_id,
        "since": since,
        "role": role
    }
    return execute_query(query, params)

# Shareholding Relationship: Person SHAREHOLDER_OF Company
def create_shareholding(person_id, company_id, share_percentage, since):
    query = """
    MATCH (p:Person {person_id: $person_id})
    MATCH (c:Company {company_id: $company_id})
    CREATE (p)-[:SHAREHOLDER_OF {
        share_percentage: $share_percentage,
        since: $since
    }]->(c)
    RETURN p, c
    """
    params = {
        "person_id": person_id,
        "company_id": company_id,
        "share_percentage": share_percentage,
        "since": since
    }
    return execute_query(query, params)

# Employment Relationship: Person EMPLOYEE_AT Company
def create_employment(person_id, company_id, role, start_date, end_date=None):
    query = """
    MATCH (p:Person {person_id: $person_id})
    MATCH (c:Company {company_id: $company_id})
    CREATE (p)-[:EMPLOYEE_AT {
        role: $role,
        start_date: $start_date,
        end_date: $end_date
    }]->(c)
    RETURN p, c
    """
    params = {
        "person_id": person_id,
        "company_id": company_id,
        "role": role,
        "start_date": start_date,
        "end_date": end_date
    }
    return execute_query(query, params)

# Transaction Relationship: Company TRANSACTED_WITH Company
def create_transaction(company_id_1, company_id_2, transaction_id, amount, currency, date):
    query = """
    MATCH (c1:Company {company_id: $company_id_1})
    MATCH (c2:Company {company_id: $company_id_2})
    CREATE (c1)-[:TRANSACTED_WITH {
        transaction_id: $transaction_id,
        amount: $amount,
        currency: $currency,
        date: $date
    }]->(c2)
    RETURN c1, c2
    """
    params = {
        "company_id_1": company_id_1,
        "company_id_2": company_id_2,
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "date": date
    }
    return execute_query(query, params)

# Registered At Relationship: Company REGISTERED_AT Address
def create_registered_at(company_id, address_id):
    query = """
    MATCH (c:Company {company_id: $company_id})
    MATCH (a:Address {address_id: $address_id})
    CREATE (c)-[:REGISTERED_AT]->(a)
    RETURN c, a
    """
    params = {
        "company_id": company_id,
        "address_id": address_id
    }
    return execute_query(query, params)

# Uses Bank Relationship: Company USES_BANK Bank
def create_uses_bank(company_id, bank_id):
    query = """
    MATCH (c:Company {company_id: $company_id})
    MATCH (b:Bank {bank_id: $bank_id})
    CREATE (c)-[:USES_BANK]->(b)
    RETURN c, b
    """
    params = {
        "company_id": company_id,
        "bank_id": bank_id
    }
    return execute_query(query, params)

def view_relationships(node1, node2):
    query = """
    MATCH (n {name: $node1})-[r]-(m {name: $node2})
    RETURN n.name AS Node1, type(r) AS Relationship, m.name AS Node2
    """
    params = {"node1": node1, "node2": node2}
    results = execute_query(query, params)

    if results:
        print(f"Relationships between '{node1}' and '{node2}':")
        for result in results:
            print(f"{result['Node1']} -[{result['Relationship']}]-> {result['Node2']}")
    else:
        print(f"No relationships found between '{node1}' and '{node2}'.")
# Establish Neo4j connection
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def fetch_graph():
    query = """
    MATCH (n)-[r]->(m)
    RETURN n.name AS source, m.name AS target, type(r) AS relationship
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record['source'], record['target'], record['relationship']) for record in result]

def visualize_graph():
    G = nx.MultiDiGraph()  # MultiDiGraph for multiple relationships
    relationships = fetch_graph()

    for source, target, relationship in relationships:
        if source is None or target is None:
            print(f"Skipped node with missing data: {source}, {target}")
            continue
        G.add_edge(source, target, label=relationship)

    pos = nx.spring_layout(G, seed=42)  # Consistent layout
    plt.figure(figsize=(12, 8))

    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True, edge_color='gray')

    # Draw all edge labels for each edge (handles multiple labels)
    edge_labels = {(u, v): [G[u][v][k]['label'] for k in G[u][v]] for u, v in G.edges()}
    formatted_labels = {(u, v): ', '.join(labels) for (u, v), labels in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_labels, font_color='red')

    output_path = os.path.join(os.getcwd(),'static','graph_visualization.png')

    plt.savefig(output_path)
    plt.close()

driver.close()

