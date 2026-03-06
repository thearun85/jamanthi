from wsgiref.types import StartResponse
from typing import Any
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# A dict of appropriate HTTP status codes
HTTP_STATUS_MAPPINGS: dict[int, str] = {
    200: '200 OK'
}
class Jamanthi:
    def __init__(self, name: str) -> None:
        self.name = name

    # Callable which web servers will call invoke when a request arrives
    def __call__(self, environ: dict[str, Any], start_response: StartResponse) -> list[bytes]:

        status = 200
        content_type = 'text/html'
        headers = [('Content-type', content_type)]
        status_text = HTTP_STATUS_MAPPINGS[status]
            
        start_response(status_text, headers)
        return [b"Welcome to Jamanthi Framework!!"]
        

    def run(self, host: str = "0.0.0.0", port: int = 8000)->None:
        from wsgiref.simple_server import make_server

        print(f"* Starting Jamanthi at http://{host}:{port}/")
        print(f"* Press Ctrl+C to force shutdown.")
        srv = make_server(host, port, self)
        
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print(f"[Jamanthi] Shuttinf Down!!")
            srv.shutdown()
