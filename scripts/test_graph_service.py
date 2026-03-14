from graph_layer import GraphService

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "neo4jadmin"

graph = GraphService(URI, USERNAME, PASSWORD)

result = graph.run_query("MATCH (n) RETURN n;")

print(result)

graph.close()
