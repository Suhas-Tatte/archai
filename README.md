# Archai – Capstone Project

## Current Status

The Neo4j data layer and ingestion pipeline for the project have been implemented.

Implemented components:

• Neo4j graph database integration  
• Python GraphService for executing Cypher queries  
• CSV dataset schema (Sites, Structures, Artifacts, Materials, Images)  
• Automated ingestion pipeline to load datasets into Neo4j  
• Static dataset for testing

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
├── run.sh # Linux/Mac setup script
├── run.bat # Windows setup script
├── .env.example
├── requirements.txt
└── README.md
```
---

## Graph Model

Nodes:
- Site
- Structure
- Artifact
- Material
- Image

Relationships:

(Site)-[:HAS_STRUCTURE]->(Structure)  
(Structure)-[:HAS_ARTIFACT]->(Artifact)  
(Artifact)-[:MADE_OF]->(Material)  
(Artifact)-[:HAS_IMAGE]->(Image)

---

## Setup Instructions

### 1. Clone repository
```
git clone https://github.com/Suhas-Tatte/archai.git  
cd Archai
```
---

### 2. Install Neo4j
## Linux (Ubuntu)
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
```
username: neo4j
password: neo4j
```

(Change password when prompted)

## Windows

- Install Neo4j Desktop: https://neo4j.com/download/
- Create and start a local DBMS

Open Neo4j Browser: http://localhost:7474

Default credentials:
```
username: neo4j
password: neo4j
```

(Change password when prompted)

---

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
```

---

### Quick Start (Recommended)

## Linux / Mac

```chmod +x run.sh
./run.sh
```

## Windows

```run.bat ```

---

# Manual Setup (Alternative)

### 1.Create Virtual Environment

## Linux / Mac
```
python3 -m venv venv
source venv/bin/activate
```

## Windows

```
python -m venv venv
venv\Scripts\activate
```
---

---

### 2. Install Dependencies
```
pip install -r requirements.txt
```

---

### 3. Load Dataset into Neo4j

Run:
```
python -m graph_layer.ingestion_data
```
Expected output:

Loading sites...  
Loading materials...  
Loading structures...  
Loading artifacts...  
Loading images...  
Data successfully loaded into Neo4j!

---

### Verify Graph

In Neo4j browser run:

MATCH (n) RETURN n

You should see nodes and relationships for:

- Sites
- Artifacts
- Materials
- Periods
- Images

Example query: 
MATCH (s:Site)-[:HAS_STRUCTURE]->(st)-[:HAS_ARTIFACT]->(a) 
RETURN s.name, st.name, a.name LIMIT 10;

---

## Important Notes

- Ensure Neo4j is running before ingestion
- Ensure `.env` credentials match your local Neo4j setup
- To reset database before reloading:
```
MATCH (n) DETACH DELETE n;
```
-The backend graph infrastructure is ready.  
-Future modules (LLM queries, visualization, maps) should interact with the database through `GraphService`.

---

## Team Instructions

1. Clone repository
2. Install Neo4j and start database
3. Create .env file
4. Run ``` run.sh ``` (Linux) or ``` run.bat ``` (Windows)

The system will automatically:

- Set up environment
- Install dependencies
- Load dataset into Neo4j

---

## Temporary Map Feature Demo

To quickly verify map functionality, a temporary webpage is available at:

- `map_demo/index.html`
- `scripts/map_demo.py`

### Run the demo

From the repository root:

```bash
python scripts/map_demo.py
```

Open this URL in your browser:

`http://127.0.0.1:8090`

### What to verify

- Map loads successfully
- Site markers appear on the map
- Clicking a marker shows site details (name, district/state, latitude/longitude)

### Notes

- Data source is auto-selected from:
  1. `data/data/sites.csv`
  2. `data/dummy_data/sites.csv` (fallback)

---
