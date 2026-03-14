# Archai – Capstone Project

## Current Status

The Neo4j data layer and ingestion pipeline for the project have been implemented.

Implemented components:

• Neo4j graph database integration  
• Python GraphService for executing Cypher queries  
• CSV dataset schema (Sites, Artifacts, Materials, Periods, Images)  
• Automated ingestion pipeline to load datasets into Neo4j  
• Dummy dataset for testing

The system currently loads archaeological data from CSV files and builds a knowledge graph in Neo4j.

---

## Project Structure
```
archai
│
├── data/
│   ├── dummy_data/      # CSV dataset
│   └── images/
│       └── dummy/       # artifact images
│
├── graph_layer/
│   ├── graph_service.py
│   └── ingestion.py
│
├── scripts/
│   └── test_graph_service.py
│
├── requirements.txt
└── README.md
```
---

## Graph Model

Nodes:
- Site
- Artifact
- Material
- Period
- Image

Relationships:

(Site)-[:CONTAINS]->(Artifact)  
(Artifact)-[:MADE_OF]->(Material)  
(Artifact)-[:BELONGS_TO]->(Period)  
(Artifact)-[:HAS_IMAGE]->(Image)

---

## Running the Project

### 1. Clone repository

git clone https://github.com/Suhas-Tatte/archai.git  
cd Archai

---

### 2. Install Neo4j
Linux (Ubuntu)
```
sudo apt update
sudo apt install neo4j
sudo systemctl start neo4j
```

Check if running:

```sudo systemctl status neo4j```

Open Neo4j browser:

http://localhost:7474

Default login:

username: neo4j

password: neo4j

(Change password when prompted)

Windows

Download Neo4j Desktop:

https://neo4j.com/download/

Install and create a local DBMS.

Start the database and open:

http://localhost:7474

Login using:

username: neo4j

password: neo4j

---

### 3. Setup Python Environment

Linux
```
python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt
```
Windows
```
python -m venv venv  
venv\Scripts\activate  
pip install -r requirements.txt
```
---

### 4. Load Dataset into Neo4j

Run:
```
python -m graph_layer.ingestion
```
Expected output:

Loading sites...  
Loading materials...  
Loading periods...  
Loading artifacts...  
Loading images...  
Data successfully loaded into Neo4j!

---

### 5. Verify Graph

In Neo4j browser run:

MATCH (n) RETURN n

You should see nodes and relationships for:

- Sites
- Artifacts
- Materials
- Periods
- Images

---

## Notes for Team

The backend graph infrastructure is ready.  
Future modules (LLM queries, visualization, maps) should interact with the database through `GraphService`.
