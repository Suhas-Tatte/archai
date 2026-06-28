import csv
import json
import logging
import math
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv

import llm.llm_main as llm_main

load_dotenv()


REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_HTML_PATH = REPO_ROOT / "map_demo" / "index.html"
DATA_CANDIDATES = [
    REPO_ROOT / "data" / "data" / "sites.csv",
    REPO_ROOT / "data" / "dummy_data" / "sites.csv",
]
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class MapDemoHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/nearby"):
            self._handle_nearby_api()
            return

        if self.path.startswith("/api/query"):
            self._handle_query_api()
            return

        if self.path == "/api/sites":
            self._handle_sites_api()
            return

        if self.path in ["/", "/index.html"]:
            self._serve_map_page()
            return

        self.send_error(404, "Not Found")

    def _serve_map_page(self):
        if not MAP_HTML_PATH.exists():
            self.send_error(500, "map_demo/index.html not found")
            return

        payload = MAP_HTML_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle_sites_api(self):
        csv_path = _find_sites_csv()
        if csv_path is None:
            self.send_error(500, "No sites.csv found in expected locations")
            return

        try:
            sites = _load_sites(csv_path)
            payload = json.dumps(sites, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except Exception as exc:
            logger.exception("Failed loading site data")
            self.send_error(500, "Failed to load site data from CSV")

    def _handle_query_api(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        q = params.get("q", [""])[0].strip()

        if not q:
            self.send_error(400, "Missing query parameter 'q'")
            return
        
        try:
            results = llm_main.ask_question(q)
            
            if not isinstance(results, list):
                results = [] 
            
            sites = []
            for r in results:
                lat = r.get("latitude")
                lon = r.get("longitude")
                try:
                    lat = None if lat is None else float(lat)
                    lon = None if lon is None else float(lon)
                except (ValueError, TypeError):
                    continue 
                if lat is None or lon is None:
                    continue 

                sites.append({
                    "site_name": r.get("site_name"),
                    "structure_name": r.get("structure_name"),
                    "artifact_name": r.get("artifact_name"),
                    "district": r.get("district"),
                    "state": r.get("state"),
                    "latitude": lat,
                    "longitude": lon,
                })

            payload = json.dumps(sites, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        
        except Exception:
            logger.exception("LLM/Neo4j query failed")
            self.send_error(500, "LLM/Neo4j query failed")

    def _handle_nearby_api(self):
        """Return sites within a radius of a given lat/lng, sorted by distance."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        try:
            lat = float(params.get("lat", [None])[0])
            lng = float(params.get("lng", [None])[0])
        except (TypeError, ValueError):
            self.send_error(400, "Missing or invalid 'lat' / 'lng' parameters")
            return

        try:
            radius_km = float(params.get("radius_km", ["5"])[0])
        except (TypeError, ValueError):
            radius_km = 5.0

        csv_path = _find_sites_csv()
        if csv_path is None:
            self.send_error(500, "No sites.csv found")
            return

        try:
            all_sites = _load_sites(csv_path)
            nearby = []
            for site in all_sites:
                dist = _haversine(lat, lng, site["latitude"], site["longitude"])
                if dist <= radius_km:
                    site_copy = dict(site)
                    site_copy["distance_km"] = round(dist, 2)
                    nearby.append(site_copy)

            nearby.sort(key=lambda s: s["distance_km"])

            # Enrich with structures and artifacts from Neo4j
            nearby = _enrich_with_neo4j(nearby)

            payload = json.dumps(nearby, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        except Exception:
            logger.exception("Nearby query failed")
            self.send_error(500, "Nearby query failed")


# --------------------------------------------------
# HAVERSINE DISTANCE
# --------------------------------------------------

_EARTH_RADIUS_KM = 6371.0


def _haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two lat/lon points."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return _EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


# --------------------------------------------------
# NEO4J ENRICHMENT (optional — degrades gracefully)
# --------------------------------------------------

def _enrich_with_neo4j(sites):
    """For each site, fetch its structures and artifacts from Neo4j.
    Falls back silently if Neo4j is unavailable."""
    if not sites:
        return sites

    try:
        from graph_layer import GraphService

        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, username, password]):
            logger.info("Neo4j credentials not configured — skipping enrichment")
            return sites

        graph = GraphService(uri, username, password)

        try:
            site_ids = [s["site_id"] for s in sites if s.get("site_id")]
            if not site_ids:
                return sites

            # Fetch structures
            struct_query = """
            MATCH (s:Site)-[:HAS_STRUCTURE]->(st:Structure)
            WHERE s.id IN $site_ids
            RETURN s.id AS site_id, st.name AS name, st.type AS type, st.description AS description
            """
            struct_rows = graph.run_query(struct_query, {"site_ids": site_ids})

            # Fetch artifacts
            art_query = """
            MATCH (s:Site)-[:HAS_ARTIFACT]->(a:Artifact)
            WHERE s.id IN $site_ids
            RETURN s.id AS site_id, a.name AS name, a.type AS type, a.description AS description
            """
            art_rows = graph.run_query(art_query, {"site_ids": site_ids})

            # Group by site_id
            structs_by_site = {}
            for row in struct_rows:
                sid = row.get("site_id")
                if sid not in structs_by_site:
                    structs_by_site[sid] = []
                structs_by_site[sid].append({
                    "name": row.get("name"),
                    "type": row.get("type"),
                    "description": row.get("description"),
                })

            arts_by_site = {}
            for row in art_rows:
                sid = row.get("site_id")
                if sid not in arts_by_site:
                    arts_by_site[sid] = []
                arts_by_site[sid].append({
                    "name": row.get("name"),
                    "type": row.get("type"),
                    "description": row.get("description"),
                })

            # Merge into site dicts
            for site in sites:
                sid = site.get("site_id")
                site["structures"] = structs_by_site.get(sid, [])
                site["artifacts"] = arts_by_site.get(sid, [])

        finally:
            graph.close()

    except Exception:
        logger.info("Neo4j enrichment unavailable — returning CSV-only results")

    return sites


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def _find_sites_csv():
    for candidate in DATA_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _parse_float_or_none(value):
    if value is None:
        return None

    raw = str(value).strip()
    if raw == "":
        return None

    try:
        parsed = float(raw)
        if math.isnan(parsed):
            return None
        return parsed
    except ValueError:
        return None


def _load_sites(csv_path):
    rows = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            latitude = _parse_float_or_none(row.get("latitude"))
            longitude = _parse_float_or_none(row.get("longitude"))
            if latitude is None or longitude is None:
                continue

            rows.append(
                {
                    "site_id": row.get("site_id"),
                    "name": row.get("name"),
                    "district": row.get("district"),
                    "state": row.get("state"),
                    "address": row.get("address"),
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )
    return rows


def main():
    host = "127.0.0.1"
    port = 8090
    server = ThreadingHTTPServer((host, port), MapDemoHandler)
    print(f"Map demo running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
