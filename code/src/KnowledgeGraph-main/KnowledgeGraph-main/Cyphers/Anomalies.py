from db.neo4j_connect import execute_query

# ✅ Detect Circular Ownership
def detect_circular_ownership():
    query = """
    MATCH path=(c1:Company)-[:OWNS*1..5]->(c2:Company)
    WHERE c1 = c2
    RETURN path
    """
    return execute_query(query)

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
    return execute_query(query)

# ✅ Detect Hidden Beneficiaries
def detect_hidden_beneficiaries():
    query = """
    MATCH path=(c1:Company)-[:OWNS*2..6]->(c2:Company)
    WHERE c1 <> c2
    RETURN path
    """
    return execute_query(query)

# ✅ Detect High-Risk Transactions
def detect_high_risk_transactions():
    query = """
    MATCH (c1:Company)-[t:TRANSACTED_WITH]->(c2:Company)
    WHERE t.amount > 1000000 AND c1.country <> c2.country
    RETURN c1.name AS Sender, c2.name AS Receiver, t.amount AS Amount, t.currency AS Currency
    """
    return execute_query(query)

# ✅ Detect Multiple Directorships
def detect_multiple_directorships():
    query = """
    MATCH (p:Person)-[:DIRECTOR_OF]->(c1:Company), (p)-[:DIRECTOR_OF]->(c2:Company)
    WHERE c1 <> c2
    RETURN p.name AS Person, COUNT(DISTINCT c1) AS num_companies
    HAVING num_companies > 5
    """
    return execute_query(query)

# ✅ Detect PEP Association
def detect_pep_association():
    query = """
    MATCH (p:Person)-[:DIRECTOR_OF|SHAREHOLDER_OF]->(c:Company)
    WHERE p.role = "PEP"
    RETURN p.name AS PEP_Name, c.name AS Company_Name
    """
    return execute_query(query)

# ✅ Detect High-Risk Bank Association
def detect_high_risk_bank_association():
    query = """
    MATCH (c:Company)-[:USES_BANK]->(b:Bank)
    WHERE b.risk_score > 8
    RETURN c.name AS Company_Name, b.name AS Bank_Name, b.risk_score AS Risk_Score
    """
    return execute_query(query)
