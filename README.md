# 🚀 Project Name
![image](https://github.com/user-attachments/assets/1d6fb095-fb24-4fc9-a2b3-14e2d8a88dbe)

![image](https://github.com/user-attachments/assets/107735cd-b971-4b90-bade-67651ec67970)



## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
The AI Risk-Driven Entity Analysis project focuses on assessing the credit risk of companies by analyzing transaction data and identifying patterns among various entities involved. By leveraging advanced AI techniques and knowledge graph modeling, the system detects anomalies, evaluates complex ownership structures, and uncovers hidden connections between companies. This comprehensive analysis helps assess the financial stability and creditworthiness of organizations while providing valuable feedback to mitigate potential risks. The project's objective is to deliver accurate, data-driven insights to support effective decision-making in financial risk management.

![image](https://github.com/user-attachments/assets/3bdd3e68-d09c-47d7-9e32-bbc5349cbf6d)

## 🎥 Demo
📹 [https://drive.google.com/file/d/1EHSUP4vIRQ1e9wA5dbGH9OXcb_cTc5Pr/view?usp=drive_link](https://drive.google.com/file/d/1EHSUP4vIRQ1e9wA5dbGH9OXcb_cTc5Pr/view?usp=sharing)
🖼️ Screenshots: <img width="539" alt="image" src="https://github.com/user-attachments/assets/fd3f84c6-cd3d-41d4-8ed8-5260c417e7f5" />

## ⚙️ What It Does
# AI Risk-Driven Entity Analysis: Project Overview
This project aims to assess **credit risk** and detect potential **anomalies** through advanced AI and data analytics. The system analyzes transaction files, extracts key entities, and applies techniques like **fuzzy name matching** and **phonetic algorithms** to identify discrepancies or fraudulent entities.

---

## Data Extraction and Enrichment
Relevant information about the entities is gathered through **web scraping** and data extraction techniques to enrich the dataset. Various features analyzed include:


## 🎥 Demo
📹 [https://drive.google.com/file/d/1EHSUP4vIRQ1e9wA5dbGH9OXcb_cTc5Pr/view?usp=drive_link](https://drive.google.com/file/d/1EHSUP4vIRQ1e9wA5dbGH9OXcb_cTc5Pr/view?usp=sharing)
    https://drive.google.com/file/d/1Bp1g2_A6fMdewBjsjC502-yB7tvWTjzU/view?usp=sharing
🖼️ Screenshots: <img width="539" alt="image" src="https://github.com/user-attachments/assets/fd3f84c6-cd3d-41d4-8ed8-5260c417e7f5" />

## ⚙️ What It Does
# AI Risk-Driven Entity Analysis: Project Overview
This project aims to assess **credit risk** and detect potential **anomalies** through advanced AI and data analytics. The system analyzes transaction files, extracts key entities, and applies techniques like **fuzzy name matching** and **phonetic algorithms** to identify discrepancies or fraudulent entities.

---

## Data Extraction and Enrichment
Relevant information about the entities is gathered through **web scraping** and data extraction techniques to enrich the dataset. Various features analyzed include:


- **Entity-Level Features:**  
  Information specific to individual entities, such as:  
  - Ownership  
  - Legal status  
  - Operational scope  

- **Transaction-Level Features:**  
  Details about financial transactions like:  
  - Amounts  
  - Currencies  
  - Dates  
  - Transaction patterns  

- **External Data Features:**  
  Insights from external sources, such as:  
  - Market analysis  
  - Competitor insights  
  - Industry trends  

- **Network and Behavioral Features:**  
  Analysis of network connections and behavioral patterns, including:  
  - Frequent transactions between the same entities  
  - Patterns suggesting potential collusion  

- **Geographical and Regulatory Features:**  
  Information regarding:  
  - Geographic locations of entities  
  - Jurisdiction-based regulations  
  - Compliance data  

- **Anomaly Features:**  
  Detection of red flags and outliers, like:  
  - Unusual transaction amounts  
  - Atypical transaction frequency  
  - Suspicious behavior  

---

## Methods Used for Data Extraction
- **Fuzzy Name Matching:** Identifies variations of company names like "Ltd." and "Limited."  
- **Language Detection:** Handles multilingual entity names.  
- **Phonetic Algorithms:** Detects phonetic similarities to identify potential fraud.  
- **Web Scraping:** Retrieves insights from social media, reviews, and real-time news data.  
- **Risk Calculator:** Dynamically adjusts risk scores based on extracted features.  

---

## Data Dumping and Transparency
To enhance transparency and build trust, results from each phase of data extraction and analysis are **systematically dumped** for the user. This allows stakeholders to:
- View intermediate results and understand each step of the analysis.  
- Access the reasoning behind final risk scores and anomaly detection.  
- Validate the data used for risk assessments, supporting compliance and audit requirements.  

This approach ensures the system is not a "black box" but a transparent and accountable solution for financial risk management.

---

## Neo4j Knowledge Graph
After data extraction and analysis, structured data is modeled and stored in a **Neo4j knowledge graph**. The graph is optimized for:
- Detecting complex relationships and hidden connections.  
- Identifying patterns of potential fraud.  
- Enhancing the understanding of interconnected data.  

<img width="914" alt="image" src="https://github.com/user-attachments/assets/55b39d4f-794c-434a-a2ea-a720fe3432da" />

---

## Anomaly Detection Patterns
The system applies multiple anomaly detection patterns to identify risks, including:
- **High-Risk Bank Association**  
- **PEP (Politically Exposed Persons) Association**  
- **Multiple Directorships**  
- **High-Risk Transactions**  
- **Shell Companies**  
- **Circular Ownership**  

---

## Dynamic Rule Engine: The USP


![image](https://github.com/user-attachments/assets/72255768-7a7e-4baa-adf8-816d3100c2ed)


The **Dynamic Rule Engine** is the solution's core strength, combining:
- Structured relationships from the **Neo4j knowledge graph**  
- Enriched external data from **web scraping**  

Using advanced AI-driven logic, the engine can:
- Cross-reference transaction patterns and entity behaviors.  
- Detect hidden connections and fraudulent activities.  
- Evaluate real-time risk scores dynamically.  
- Provide data-driven feedback for informed decision-making.  

This combination of structured graph data and dynamic external intelligence makes the system highly adaptive, enhancing its reliability in identifying complex financial risks.

---

## 🛠️ How We Built It
We built this solution using a combination of advanced AI techniques, data extraction microservices, and a Neo4j knowledge graph for structured relationship analysis. The system integrates dynamic web scraping, anomaly detection algorithms, and a rule engine to assess credit risk accurately.

## 🚧 Challenges We Faced
Web Scraping Limitations: Navigating restricted or protected websites for data enrichment.

## 🏗️ Tech Stack
- 🔹 Frontend: css/html/ bootstrap
- 🔹 Backend: Flask, python/ LLM llama / 
- 🔹 Database: Neo4j

**Deployment** : https://quickstart-app-1050188241794.us-west2.run.app/

## Conclusion
This structured approach enables comprehensive **credit risk assessment**, effective **anomaly detection**, and robust **financial risk mitigation**. It provides transparency, accuracy, and insightful analysis for financial institutions and regulatory bodies.

## 👥 Team
- **Gulshan Kumar** 
- **Shivesh Dixit** 
- **Srivatsh Agarwal**
- **Nishan Murarka**


