import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    entity_name = input("Enter the entity name: ")
    result = fetch_entity_info(entity_name)
    print(result)

if __name__ == "__main__":
    main()
