import logging
import json
from entity_enricher import EntityDataEnricher

# Setup logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console logging
        logging.FileHandler("history.txt", mode="a", encoding="utf-8")  # Log to file
    ]
)

def main():
    logging.info("🚀 Starting the Entity Enrichment process...")

    sanctions_pdf_path = "sdnlist.pdf"  # Update with the correct path
    enricher = EntityDataEnricher(sanctions_pdf_path)

    #entities = ["Tesla Inc."]  # Entities to enrich
    entities = ["23andMe Holding Co"]
    

    results = []
    all_failed_apis = {}

    for entity in entities:
        enriched_data, failed_apis = enricher.enrich_entity(entity)
        results.append(enriched_data)
        all_failed_apis[entity] = failed_apis

        logging.info(f"✅ Enrichment completed for {entity}. Failed APIs: {failed_apis}")

    # Print and log enriched data for each entity
    logging.info("\n📌 Final Enriched Data:")
    print("\n🔹 Final Enriched Data:\n")

    for entity, data in zip(entities, results):
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        logging.info(f"📍 {entity}:\n{formatted_data}\n")

     # Summary of failures
    failed_summary = {k: v for k, v in all_failed_apis.items() if v}
    if failed_summary:
        logging.warning("\n❌ Summary of failed API calls:")
        for entity, failures in failed_summary.items():
            logging.warning(f"   🔹 {entity}: {', '.join(failures)}")
    else:
        logging.info("\n🎉 All API calls succeeded!")


if __name__ == "__main__":
    main()
