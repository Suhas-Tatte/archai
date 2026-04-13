import csv
from graph_layer import GraphService
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

DATA_PATH = "data/data/"

graph = GraphService(URI, USERNAME, PASSWORD)

def clean_row(row):
	"""Remove leading/trailing spaces from keys and values"""
	return {k.strip(): v.strip() if v else None for k, v in row.items()}

def load_sites():
	with open(DATA_PATH + "sites.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			row = clean_row(row)
			
			query = """
			MERGE (s:Site {id: $site_id})
			SET s.name = $name,
				s.address = $address,
				s.district = $district,
				s.state = $state,
				s.latitude = toFloat($latitude),
				s.longitude = toFloat($longitude),
				s.gis_accuracy = $gis_accuracy
			"""
			graph.run_query(query, row)

def load_structures():
	with open(DATA_PATH + "structures.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			row = clean_row(row)
			
			query = """
			MERGE (st:Structure {id: $structure_id})
			SET st.name = $name,
				st.type = $type,
				st.description = $description
			WITH st
			MATCH (s:Site {id: $site_id})
			MERGE (s)-[:HAS_STRUCTURE]->(st)
			"""
			graph.run_query(query, row)

def load_artifacts():
	with open(DATA_PATH + "artifacts.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			row = clean_row(row)
			
			query = """
			MERGE (a:Artifact {id: $artifact_id})
			SET a.name = $name,
				a.type = $type,
				a.description = $description
			WITH a
			MATCH (s:Site {id: $site_id}) 
			MERGE (s)-[:HAS_ARTIFACT]->(a)
			"""
			graph.run_query(query, row)

if __name__ == "__main__":
	print("Loading sites...")
	load_sites()
	
	
	print("Loading structures...")
	load_structures()
	
	print("Loading artifacts...")
	load_artifacts()
	
	graph.close()
	print("Data successfully loaded into Neo4j!") 