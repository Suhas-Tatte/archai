from .model import generate_cypher, extract_location_llm
from .graph import run_query
from .rules import (
    detect_location,
    detect_structure_type,
    is_structure_query,
    extract_entity_phrase
)

import json


# --------------------------------------------------
# COMMON SITE FIELDS
# --------------------------------------------------

SITE_FIELDS = """
    s.name AS site_name,
    s.state AS state,
    s.district AS district,
    s.address AS address,
    s.latitude AS latitude,
    s.longitude AS longitude,
    s.gis_accuracy AS gis_accuracy
"""


# --------------------------------------------------
# FETCH LOCATIONS DYNAMICALLY
# --------------------------------------------------

def get_all_locations():

    query = """
    MATCH (s:Site)

    RETURN DISTINCT
        s.district AS district,
        s.state AS state,
        s.address AS address
    """

    results = run_query(query)

    locations = set()

    for r in results:

        if r.get("district"):
            locations.add(r["district"])

        if r.get("state"):
            locations.add(r["state"])

        if r.get("address"):
            locations.add(r["address"])

    return list(locations)


# --------------------------------------------------
# MAIN QA FUNCTION
# --------------------------------------------------

def ask_question(question):

    print("\n==============================")
    print("Question:", question)

    # STEP 1
    locations = get_all_locations()

    # STEP 2
    location = detect_location(question, locations)
    structure_type = detect_structure_type(question)
    entity = extract_entity_phrase(question)

    # STEP 3
    llm_location = None

    if not location:
        llm_location = extract_location_llm(question)

    # --------------------------------------------------
    # CASE 1
    # Location + Structure Type
    # --------------------------------------------------

    if location and structure_type and is_structure_query(question):

        cypher = f"""
        MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)

        WHERE (
            toLower(s.district) CONTAINS "{location.lower()}"
            OR toLower(s.state) CONTAINS "{location.lower()}"
            OR toLower(s.address) CONTAINS "{location.lower()}"
        )

        AND (
            toLower(st.type) CONTAINS "{structure_type.lower()}"
            OR toLower(s.name) CONTAINS "{structure_type.lower()}"
        )

        RETURN DISTINCT
            {SITE_FIELDS},
            st.name AS structure_name,
            st.type AS structure_type
        """

    # --------------------------------------------------
    # CASE 2
    # Location Only
    # --------------------------------------------------

    elif location and is_structure_query(question):

        cypher = f"""
        MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)

        WHERE (
            toLower(s.district) CONTAINS "{location.lower()}"
            OR toLower(s.state) CONTAINS "{location.lower()}"
            OR toLower(s.address) CONTAINS "{location.lower()}"
        )

        RETURN DISTINCT
            {SITE_FIELDS},
            st.name AS structure_name,
            st.type AS structure_type
        """

    # --------------------------------------------------
    # CASE 3
    # Entity Search
    # --------------------------------------------------

    elif entity and is_structure_query(question):

        cypher = f"""
        MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)

        WHERE (
            toLower(s.name) CONTAINS "{entity.lower()}"
            OR toLower(s.address) CONTAINS "{entity.lower()}"
        )

        RETURN DISTINCT
            {SITE_FIELDS},
            st.name AS structure_name,
            st.type AS structure_type
        """

    # --------------------------------------------------
    # CASE 4
    # LLM Location Fallback
    # --------------------------------------------------

    elif llm_location and structure_type:

        cypher = f"""
        MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)

        WHERE (
            toLower(s.district) CONTAINS "{llm_location.lower()}"
            OR toLower(s.state) CONTAINS "{llm_location.lower()}"
            OR toLower(s.address) CONTAINS "{llm_location.lower()}"
        )

        AND (
            toLower(st.type) CONTAINS "{structure_type.lower()}"
            OR toLower(s.name) CONTAINS "{structure_type.lower()}"
        )

        RETURN DISTINCT
            {SITE_FIELDS},
            st.name AS structure_name,
            st.type AS structure_type
        """

    # --------------------------------------------------
    # CASE 5
    # FULL LLM FALLBACK
    # --------------------------------------------------

    else:

        cypher = generate_cypher(question)

    print("\nGenerated Cypher:\n")
    print(cypher)

    try:

        result = run_query(cypher)

        print("\nResult:\n")

        if result:

            print(
                json.dumps(
                    result,
                    indent=4,
                    ensure_ascii=False,
                    default=str
                )
            )

            return result

        else:

            print(
                f"⚠️ No data found for '{question}' in the database."
            )

            return []

    except Exception as e:

        print("\n❌ Query Failed:")
        print(e)

        return []


# --------------------------------------------------
# TESTING
# --------------------------------------------------

if __name__ == "__main__":

    ask_question("stone inscription at masjid")

    # ask_question("all memorial stones")
    # ask_question("stepwells in Ahmedabad")
    # ask_question("structures in Ahmedabad")
    # ask_question("stepwells in Gujarat")
    # ask_question("structures in Adalaj Stepwell")
    # ask_question("mosques in Ahmedabad")
    # ask_question("temple in hampi")
    # ask_question("temples in unknown place")
    # ask_question("temples in Junagadh")
    # ask_question("Find stepwells in Banaskantha")