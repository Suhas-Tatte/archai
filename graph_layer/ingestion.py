import csv
from graph_layer import GraphService

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neo4jadmin"

DATA_PATH = "data/dummy_data/"

graph = GraphService(URI, USERNAME, PASSWORD)

def load_sites():
	with open(DATA_PATH + "sites.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (s:Site {site_id: $site_id})
			SET s.name = $name,
				s.region = $region,
				s.latitude = toFloat($latitude),
				s.longitude = toFloat($longitude)
			"""
			graph.run_query(query, row)

def load_materials():
	with open(DATA_PATH + "materials.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (m:Material {material_id: $material_id})
			SET m.name = $name
			"""
			graph.run_query(query, row)

def load_periods():
	with open(DATA_PATH + "periods.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (p:Period {period_id: $period_id})
			SET p.name = $name
			"""
			graph.run_query(query, row)

def load_artifacts():
	with open(DATA_PATH + "artifacts.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (a:Artifact {artifact_id: $artifact_id})
			SET a.name = $name,
				a.type = $type,
				a.description = $description
			WITH a
			MATCH (s:Site {site_id: $site_id})
			MERGE (a)-[:FOUND_AT]->(s)
			WITH a
			MATCH (m:Material {material_id: $material_id})
			MERGE (a)-[:MADE_OF]->(m)
			WITH a
			MATCH (p:Period {period_id: $period_id})
			MERGE (a)-[:FROM_PERIOD]->(p)
			"""
			graph.run_query(query, row)

def load_images():
	with open(DATA_PATH + "images.csv") as f:
		reader = csv.DictReader(f)
		for row in reader:
			query = """
			MERGE (img:Image {image_id: $image_id})
			SET img.file_path = $file_path,
				img.description = $description
			WITH img
			MATCH (a:Artifact {artifact_id: $artifact_id})
			MERGE (a)-[:HAS_IMAGE]->(img)
			"""
			graph.run_query(query, row)

if __name__ == "__main__":
	print("Loading sites...")
	load_sites()
	
	print("Loading materials...")
	load_materials()
	
	print("Loading periods...")
	load_periods()
	
	print("Loading artifacts...")
	load_artifacts()
	
	print("Loading images...")
	load_images()

	graph.close()
	print("Data successfully loaded into Neo4j!")