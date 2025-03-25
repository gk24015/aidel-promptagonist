import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import requests

# alphavantage api
def get_ticker(company_name, api_key):
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={api_key}"
    try:
        response = requests.get(url).json()
        return response['bestMatches'][0]['1. symbol'] if response.get('bestMatches') else None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_news_sentiment(api_key, entity_name_symbol):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={entity_name_symbol}&apikey={api_key}"
    try:
        return requests.get(url).json()
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example Usage



def fetch_news_api(entity_name):
    api_key = os.getenv("News_API_api_key")
    url = f"https://newsdata.io/api/1/latest?apikey={api_key}&q={entity_name}&size=5&language=en"
    response = requests.get(url)
    if response.status_code == 200:
        response_data = response.json().get("results", [])

        articles_data = [
            {
                "article_id": item.get("article_id"),
                "description": item.get("description"),
                "source_id": item.get("source_id"),
                "title": item.get("title")
            }
            for item in response_data
        ]

        print(articles_data)
    else:
        return {"error": f"Failed to fetch from News API. Status code: {response.status_code}"}



def fetch_entity_info(entity_name,entity_owner_name):
    results = {
        "Company News": fetch_news_api(entity_name),
        "Owner News": fetch_entity_info(entity_owner_name)
    }
    return results




def main():
    vonyage_free_api_key="HIKPE2YH9BY0F9YK"
    entity_name = input("Enter the entity name: ")
    # result = fetch_entity_info(entity_name)
    entity_name_symbol=get_ticker(entity_name,vonyage_free_api_key)
    print(entity_name_symbol)
    print(get_news_sentiment(vonyage_free_api_key,entity_name_symbol))
    
    # print(result)



if __name__ == "__main__":
    main()
