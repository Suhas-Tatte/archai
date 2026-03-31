import csv
from graph_layer import GraphService
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

DATA_PATH = "data/dummy_data/"

graph = GraphService(URI, USERNAME, PASSWORD)

def load_sites():
	with open(DATA_PATH + "sites.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (s:Site {id: $site_id})
			SET s.name = $name,
				s.address = $address,
				s.district = $district,
				s.state = $state,
				s.latitude = toFloat($latitude),
				s.longitude = toFloat($longitude)
			"""
			graph.run_query(query, row)

def load_materials():
	with open(DATA_PATH + "materials.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (m:Material {id: $material_id})
			SET m.name = $name
			"""
			graph.run_query(query, row)

def load_structures():
	with open(DATA_PATH + "structures.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
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
			query = """
			MERGE (a:Artifact {id: $artifact_id})
			SET a.name = $name,
				a.type = $type,
				a.description = $description
			WITH a
			MATCH (st:Structure {id: $structure_id})
			MERGE (st)-[:HAS_ARTIFACT]->(a)
			WITH a
			MATCH (s:Site {id: $site_id})
			MERGE (s)-[:HAS_ARTIFACT]->(a)
			WITH a
			MATCH (m:Material {id: $material_id})
			MERGE (a)-[:MADE_OF]->(m)
			"""
			graph.run_query(query, row)

def load_images():
	with open(DATA_PATH + "images.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (img:Image {id: $image_id})
			SET img.path = $file_path,
				img.description = $description
			WITH img
			MATCH (a:Artifact {id: $artifact_id})
			MERGE (a)-[:HAS_IMAGE]->(img)
			"""
			graph.run_query(query, row)


if __name__ == "__main__":
	print("Loading sites...")
	load_sites()
	
	print("Loading materials...")
	load_materials()
	
	print("Loading structures...")
	load_structures()
	
	print("Loading artifacts...")
	load_artifacts()
	
	print("Loading images...")
	load_images()

	graph.close()
	print("Data successfully loaded into Neo4j!")