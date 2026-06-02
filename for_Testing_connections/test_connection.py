from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "archaicapstone")
)

with driver.session() as session:
    print(session.run("RETURN 1").single())

driver.close()