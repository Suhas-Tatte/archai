from groq import Groq
import os
from dotenv import load_dotenv
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_cypher(user_query):

    prompt = f"""
You are an expert Neo4j Cypher generator.

Generate a valid Cypher query from the user's natural language question.

Generate only the filters explicitly requested by the user.

Do not assume missing information.

Output ONLY Cypher.

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

QUERY GENERATION RULES:

- Only generate filters that are explicitly implied by the user's question.

- Never invent filters.

- Never assume a location exists.

- If the query asks for every entity of a type (for example all structures, all artifacts, all sites, all temples), do not generate a location filter.

- Only generate a WHERE clause when a filter is actually required.

- If multiple filters are present (location + structure type + artifact type), combine them appropriately.

LOCATION RULE:

1. A location is optional.

2. If the user explicitly mentions a location (city, district, state, site name, or address), generate a WHERE clause using:

    s.name
    s.district
    s.state
    s.address

3. If no location is mentioned, DO NOT generate any location-based WHERE clause.

4. Never generate comparisons against empty strings such as:

    toLower(s.name) = ""
    toLower(s.state) = ""
    toLower(s.district) = ""
    toLower(s.address) = ""

5. If no location exists, search the entire knowledge graph.

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

FINAL VALIDATION BEFORE OUTPUT:

- Is every WHERE condition supported by the user's question?

- If the answer is NO, remove that WHERE condition.

- Do not generate empty string comparisons.

- Do not generate impossible conditions.

- Return only valid Cypher.

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

# Remove markdown code fences if the model returns them
    result = result.replace("```cypher", "")
    result = result.replace("```", "")
    result = result.strip()

    return result


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