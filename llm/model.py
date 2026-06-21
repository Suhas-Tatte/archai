from groq import Groq
import os
from dotenv import load_dotenv
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_cypher(user_query):

    prompt = f"""
Convert the following natural language question into a Neo4j Cypher query.

STRICT RULES:
- Output ONLY Cypher
- No explanation
- Always use DISTINCT

STRICT VARIABLE RULES:
- ALWAYS use EXACT variable names:
    (s:Site)
    (st:Structure)
    (a:Artifact)
    (m:Material)

SCHEMA:
(Site)-[:HAS_STRUCTURE]->(Structure)
(Site)-[:HAS_ARTIFACT]->(Artifact)
(Artifact)-[:MADE_OF]->(Material)
(Artifact)-[:HAS_IMAGE]->(Image)

IMPORTANT LOGIC:
- temple, mosque, stepwell → Structure
- inscription, memorial stone → Artifact
- If both are mentioned → Structure + Artifact query

LOCATION RULE:
Check location in:
- s.name
- s.district
- s.state
- s.address

SPECIAL RULE:
- memorial stone =>
  toLower(a.type) CONTAINS "memorial"

RETURN RULE:

For Structure queries:

RETURN DISTINCT
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy,
    st.name AS structure_name,
    st.type AS structure_type

For Artifact queries:

RETURN DISTINCT
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy,
    a.name AS artifact_name,
    a.type AS artifact_type

For Structure + Artifact queries:

RETURN DISTINCT
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy,
    st.name AS structure_name,
    st.type AS structure_type,
    a.name AS artifact_name,
    a.type AS artifact_type

EXAMPLES:

User: temples in Ahmedabad

MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)

WHERE (
    toLower(s.district) CONTAINS "ahmedabad"
    OR toLower(s.state) CONTAINS "ahmedabad"
    OR toLower(s.address) CONTAINS "ahmedabad"
)

AND toLower(st.type) CONTAINS "temple"

RETURN DISTINCT
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy,
    st.name AS structure_name,
    st.type AS structure_type


User: all memorial stones

MATCH (s:Site)-[:HAS_ARTIFACT]->(a:Artifact)

WHERE toLower(a.type) CONTAINS "memorial"

RETURN DISTINCT
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy,
    a.name AS artifact_name,
    a.type AS artifact_type


User: inscriptions in temples

MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)
MATCH (s)-[:HAS_ARTIFACT]->(a:Artifact)

WHERE toLower(st.type) CONTAINS "temple"
AND toLower(a.type) CONTAINS "inscription"

RETURN DISTINCT
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy,
    st.name AS structure_name,
    st.type AS structure_type,
    a.name AS artifact_name,
    a.type AS artifact_type

User Query:
{user_query}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    # Fix Structure variables
    result = re.sub(
        r"\(\s*\w+\s*:\s*Structure\s*\)",
        "(st:Structure)",
        result
    )

    # Fix Artifact variables
    result = re.sub(
        r"\(\s*\w+\s*:\s*Artifact\s*\)",
        "(a:Artifact)",
        result
    )

    # Fix wrong aliases
    result = re.sub(
        r"\b(sst|str|t)\b",
        "st",
        result
    )

    # Remove incorrect stone condition
    result = re.sub(
        r'AND\s+toLower\(a\.type\)\s+CONTAINS\s+"stone"',
        '',
        result
    )

    # Ensure Cypher starts from MATCH
    if "MATCH" in result:
        result = result[result.index("MATCH"):]

    return result.strip()


def extract_location_llm(query):

    prompt = f"""
Extract ONLY the location name.

Query:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()