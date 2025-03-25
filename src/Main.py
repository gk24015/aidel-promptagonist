from Cyphers.Nodes import *
from db.neo4j_connect import *
from Cyphers.Relationships import * 
from Cyphers.Anomalies import *
from Cyphers.View import *

# print("URI:", URI)
# print("Username:", USERNAME)
# print("Password:", PASSWORD)  # Just for testing, remove this later!

# Create a Company node example
# create_company(
#     company_id="C003",
#     name="Wells Fargo & Company",
#     country="USA",
#     industry="Banking",
#     status="Active",
#     incorporation_date="1929-01-24",
#     revenue=125000000000,
#     employees=217000,
#     is_listed=True,
#     risk_score=2.5,
#     ownership_type="Public"
# )

# create_person(
#     person_id="P004",
#     name="Charles W. Scharf",
#     dob="1965-04-24",
#     nationality="American",
#     role="Director",
#     passport_number=None,
#     risk_score=None
# )

# Create Directorship Relationship
# create_directorship(
#     person_id="P004",         # Charles W. Scharf's person_id
#     company_id="C003",        # Company ID
#     since="2021-01-01",       # Since when he is a director
#     active=True               # Active status
# )

# create_transaction (
#     transaction_id="T002",
#     company_id_1="C003",
#     company_id_2="C002",
#     amount=11000000,
#     currency="USD",
#     date="2025-03-25"
# )

print("\n🔎 Detecting High-Risk Transactions:")
high_risk_transactions = detect_high_risk_transactions()
for txn in high_risk_transactions:
    print(txn)

# updated_data = {
#     "country": "India",
# }

# response = update_company("C002", updated_data)
# print(response)

# view_relationships("Example Corp", "Subsidiary Corp")

# Close the Neo4j connection
close_connection()
