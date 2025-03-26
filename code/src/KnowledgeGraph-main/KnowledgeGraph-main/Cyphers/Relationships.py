from db.neo4j_connect import execute_query # type: ignore

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
def create_directorship(person_id, company_id, since, active):
    query = """
    MATCH (p:Person {person_id: $person_id})
    MATCH (c:Company {company_id: $company_id})
    CREATE (p)-[:DIRECTOR_OF {
        since: $since,
        active: $active
    }]->(c)
    RETURN p, c
    """
    params = {
        "person_id": person_id,
        "company_id": company_id,
        "since": since,
        "active": active
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
