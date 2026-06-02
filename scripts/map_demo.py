import csv
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_HTML_PATH = REPO_ROOT / "map_demo" / "index.html"
DATA_CANDIDATES = [
    REPO_ROOT / "data" / "data" / "sites.csv",
    REPO_ROOT / "data" / "dummy_data" / "sites.csv",
]


class MapDemoHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
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
            self.send_error(500, f"Failed loading data: {exc}")


def _find_sites_csv():
    for candidate in DATA_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _safe_float(value):
    if value in [None, "", "null", "Null"]:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _load_sites(csv_path):
    rows = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            latitude = _safe_float(row.get("latitude"))
            longitude = _safe_float(row.get("longitude"))

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
