from neo4j import GraphDatabase # type: ignore
from config import URI, USERNAME, PASSWORD

# Create a driver instance
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def execute_query(query, parameters=None):
    try:
        with driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]
    except Exception as e:
        print(f"❌ Query failed: {e}")


# Close the driver
def close_connection():
    driver.close()
