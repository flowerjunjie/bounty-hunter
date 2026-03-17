import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class BountyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # 读取最新报告
            report_file = Path("/root/.bounty-hunter/auto_report.json")
            if report_file.exists():
                data = report_file.read_text()
                self.wfile.write(data.encode())
            else:
                self.wfile.write(b'{"status": "initializing"}')
        else:
            super().do_GET()

if __name__ == "__main__":
    server = HTTPServer(("", 8080), BountyHandler)
    print("API running on port 8080")
    server.serve_forever()
