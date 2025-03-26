from db.neo4j_connect import execute_query # type: ignore

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
def create_person(person_id, name, dob, nationality, role, passport_number=None, risk_score=None):
    query = """
    CREATE (p:Person {
        person_id: $person_id,
        name: $name,
        dob: $dob,
        nationality: $nationality,
        role: $role,
        passport_number: $passport_number,
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
        "passport_number": passport_number,
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


