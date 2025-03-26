from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
# from IPython.display import Image, display
# from langgraph.graph import Graph

# Load environment variables
load_dotenv()

class FinancialDataExtractor:
    def __init__(self, entity):
        self.entity = entity
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        # self.workflow = Graph()
        # self.setup_workflow()

    def query_model(self, user_query, content):
        messages = [
            {"role": "system", "content": "You are an expert in financial data extraction. Do not include Disclaimers at end of your response"},
            {"role": "user", "content": f"User Query: {user_query}\n\nContent:\n{content}"}
        ]
        completion = self.client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=messages
        )
        return completion.choices[0].message.content

    def extract_entity_info(self, content):
        user_query = '''Given the transaction details, return the data in this format:
            "Extracted Entity": The name of the payer and receiver,
            "Entity Type": Industry type,
            "Entity Owner": Owner name,
            "Industry": the industry the entities are associated with,
            "Industry Risk": is the industry risky and have more chances of frauds
            "Market Cap": the market capital of entities
            "Revenue": the revenue of entities
            '''
            
        return self.query_model(user_query, content)

    def extract_owner_info(self, content):
        user_query = '''Given the transaction details, return the data in this format:
            "Owner's Profile": Owner's fraud associations,
            "Risk Score of Owner": Risk level, is the owner connected to any political criminal entity?
            "Supporting Evidence": Supporting evidence'''
        
        return self.query_model(user_query, content)

    def extract_shareholder_info(self, content):
        user_query = '''Given the transaction details, return the data in this format:
            "Shareholder Profile": Shareholders if any,
            "Risk": Risk level of shareholders,
            "Supporting Evidence": Supporting evidence.
            If no shareholders, mention single entity ownership and risk.'''
        return self.query_model(user_query, content)

    def extract_shell_company_info(self, content):
        user_query = '''Given the transaction details, return the data in this format:
            "Shell Company": Associated shell companies,
            "Risk": Associated risks,
            "Sentiments in News": Recent sentiment changes,
            "Supporting Evidence": Supporting evidence.'''
        return self.query_model(user_query, content)

    def subsidiary_company_info(self, content):
        user_query = '''Given the transaction details, return the data in this format:
            "Subsidiary": Subsidiary companies,
            "Risk": Associated risks with any subsidiaries,
            "Sentiments in News": Recent sentiment changes for subsidiaries,
            "Supporting Evidence": Supporting evidence.'''
        return self.query_model(user_query, content)
    
    def lawsuitInfo(self,content):
        user_query= '''Given the transaction details, return the data in this format: 
            "Lawsuit": any lawsuit informations available,
            "Criminal Activities": criminal activities associated with the entities,
            "Fraudulant Informations": Recent fraud news related to entities,
            "Supporting Evidence": Supporting evidence.'''
    
    
        return self.query_model(user_query, content)

    def determineRisk(self,custom_rules, entity_info, owner_info, shareholder_info, shell_company_info, subsidiary_info, lawsuit_info):
        user_query = f'''You are an expert in financial risk assessment. Based on the following information, provide a risk evaluation for the entity:

        Entity Information:
        {entity_info}

        Owner Information:
        {owner_info}

        Shareholder Information:
        {shareholder_info}

        Shell Company Information:
        {shell_company_info}

        Subsidiary Information:
        {subsidiary_info}

        Lawsuit Information:
        {lawsuit_info}

        Perform a comprehensive risk assessment. Consider the following factors:
        - If the owner has criminal connections, political exposure, or is linked to fraudulent activities, assign a high-risk score.
        - If multiple shell companies or subsidiaries are identified with negative sentiments, increase the risk level.
        - Lawsuits, fraud reports, or negative news should significantly contribute to the risk score.
        - Evaluate shareholder profiles and their risk associations.
        - Consider industry risks as well.

        Provide the output in the following format without any additional comments:
        {{
            "Transaction ID": "{self.entity['TransactionId']}",
            "Payer Entity": "{self.entity['Payer Name']} 
            "Receiver Entity":" {self.entity['Receiver Name']}",
            "Entity Type": "{entity_info}",
            "Fradulant Activity":"{lawsuit_info}",
            "Risk Score": "Percentage between 0 to 100, low risk meaning 0-30 medium risk score can range 30-65 and above that would be high risk",
            "Confidence Score": "High",
            "Reason": ["List key factors contributing to the risk in support of score"]
        }}
        '''
        if custom_rules:
         user_query += "\nAdditional Custom Rules:\n" + "\n".join(custom_rules)
         print("Custom Rules appended",user_query)
        return self.query_model(user_query, "")

def append_to_file(entity_name, entity_info, owner_info, shareholder_info, shell_company_info, subsidiary_info, lawsuit_info, risk_response):
    filename = f"F:\\Development\\TechnologyHackathon\\aidel-promptagonist\\code\\src\\Chatbot\\{entity_name}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("Financial Data Extraction Report\n")
        file.write(f"Entity Name: {entity_name}\n\n")
        
        file.write("Entity Information:\n")
        file.write(entity_info + "\n\n")
        
        file.write("Owner Information:\n")
        file.write(owner_info + "\n\n")
        
        file.write("Shareholder Information:\n")
        file.write(shareholder_info + "\n\n")
        
        file.write("Shell Company Information:\n")
        file.write(shell_company_info + "\n\n")
        
        file.write("Subsidiary Information:\n")
        file.write(subsidiary_info + "\n\n")
        
        file.write("Lawsuit Information:\n")
        file.write(lawsuit_info + "\n\n")
        
        file.write("Risk Assessment:\n")
        file.write(risk_response + "\n\n")
        
        file.write("=" * 50 + "\n\n")
    
    print(f"Data appended to {filename}")

if __name__ == "__main__":
    entity = {
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
    }

    extractor = FinancialDataExtractor(entity)

    # Call the method with entity or any content
    entity_info = extractor.extract_entity_info(entity)
    print("Entity_info done")
    owner_info = extractor.extract_owner_info(entity)
    print("Owner_info done")
    shareholder_info = extractor.extract_shareholder_info(entity)
    print("Shareholder_info done")
    shell_company_info = extractor.extract_shell_company_info(entity)
    print("Shell_company_info done")
    subsidiary_info = extractor.subsidiary_company_info(entity)
    print("Subsidiary_info done")
    lawsuit_info = extractor.lawsuitInfo(entity)
    print("Lawsuit_info done")

    risk_response = extractor.determineRisk(
        entity_info,
        owner_info,
        shareholder_info,
        shell_company_info,
        subsidiary_info,
        lawsuit_info
    )
    print("Risk assessment done")

    # Print the response
    print({
        "entity_info": entity_info,
        "owner_info": owner_info,
        "shareholder_info": shareholder_info,
        "shell_company_info": shell_company_info,
        "subsidiary_info": subsidiary_info,
        "lawsuit_info": lawsuit_info,
        "risk_response": risk_response
    })

    # Append to file
    append_to_file(
        entity["Payer Name"],
        entity_info,
        owner_info,
        shareholder_info,
        shell_company_info,
        subsidiary_info,
        lawsuit_info,
        risk_response
    )

    # entity_info = '''{
    #     "Extracted Entity": "TechCorp Ltd",
    #     "Entity Type": "Technology",
    #     "Entity Owner": "John Doe",
    #     "Industry": "Software",
    #     "Industry Risk": "Moderate",
    #     "Market Cap": "1.2B USD",
    #     "Revenue": "500M USD"
    # }'''

    # owner_info = '''{
    #     "Owner's Profile": "Experienced Entrepreneur",
    #     "Risk Score of Owner": "Low",
    #     "Supporting Evidence": "No issues"
    # }'''

    # shareholder_info = '''{
    #     "Shareholder Profile": [
    #         {"Name": "Investor A", "Stake": "30%", "Risk Level": "Low"},
    #         {"Name": "Investor B", "Stake": "20%", "Risk Level": "Medium"}
    #     ],
    #     "Risk": "Medium",
    #     "Supporting Evidence": "Minor violation"
    # }'''

    # shell_company_info = '''{
    #     "Shell Company": [
    #         {"Name": "Global Ventures", "Location": "Cayman Islands"},
    #         {"Name": "Offshore Holdings", "Location": "BVI"}
    #     ],
    #     "Risk": "High",
    #     "Sentiments in News": "Negative",
    #     "Supporting Evidence": "Tax evasion"
    # }'''

    # subsidiary_info = '''{
    #     "Subsidiary": [
    #         {"Name": "Tech Solutions", "Risk Level": "Low"},
    #         {"Name": "InnovateX AI", "Risk Level": "Medium"}
    #     ],
    #     "Risk": "Low",
    #     "Sentiments in News": "Positive",
    #     "Supporting Evidence": "Product awards"
    # }'''

    # lawsuit_info = '''{
    #     "Lawsuit": [
    #         {"Case": "Patent Infringement", "Status": "Ongoing"},
    #         {"Case": "Misconduct", "Status": "Settled"}
    #     ],
    #     "Criminal Activities": "None",
    #     "Fraudulant Informations": "No fraud",
    #     "Supporting Evidence": "Legal documents"
    # }'''

    # print("Entity_info done")
    # print("determining risk")

    # risk_response = extractor.determineRisk(entity_info, owner_info, shareholder_info, shell_company_info, subsidiary_info, lawsuit_info)
    # print(risk_response)
    # # Print the response
    # append_to_file(
    #     extractor.entity_name,
    #     entity_info,
    #     owner_info,
    #     shareholder_info,
    #     shell_company_info,
    #     subsidiary_info,
    #     lawsuit_info
    # )

