from graph_layer import GraphService
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

graph = GraphService(URI, USERNAME, PASSWORD)

result = graph.run_query("MATCH (n) RETURN n;")

print(result)

graph.close()
