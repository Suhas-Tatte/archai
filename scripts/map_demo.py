import csv
import json
import logging
import math
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs 
import llm.llm_main as llm_main


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
