import os
import sys
from wsgiref.types import StartResponse
from typing import Any
from collections.abc import Callable

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ViewFunc = Callable[..., str|bytes]

# A dict of appropriate HTTP status codes
HTTP_STATUS_MAPPINGS: dict[int, str] = {
    200: '200 OK',
    404: '404 NOT FOUND',
}

class NotFound(Exception):
    status = 404

def not_found(start_response: StartResponse) -> list[bytes]:
    start_response(HTTP_STATUS_MAPPINGS[404], [('Content-Type', 'text/plain')])
    return [b"Page Not Found"]

class Jamanthi:
    def __init__(self, name: str) -> None:
        self.name = name
        # Records the handlers for a method and path combination
        self.routes: dict[str, dict[str, ViewFunc]] = {
            'GET': {},
        }
        module = sys.modules.get(self.name)
        module_file = getattr(module, '__file__', None)
        if module_file:
            self.root_path = os.path.dirname(os.path.abspath(module_file))
        else:
            self.root_path = os.getcwd()

        self.html_path = os.path.join(self.root_path, "html")
        
        logger.info(f"[Jamanthi] App initialized with name {name}")

    # Callable which web servers will call invoke when a request arrives
    def __call__(self, environ: dict[str, Any], start_response: StartResponse) -> list[bytes]:

        status = 200
        content_type = 'text/html'

        try:
            handler = self.find_handler(environ)
        except NotFound:
            logger.error(f"[Jamanthi] Handler not registered")
            return not_found(start_response)

        body = handler()
        if isinstance(body, str):
            body = body.encode()
        headers = [('Content-type', content_type)]
        status_text = HTTP_STATUS_MAPPINGS[status]
            
        start_response(status_text, headers)
        return [body]
        
    def get(self, path: str) -> Callable[[ViewFunc], ViewFunc]:
        logger.info(f"[Jamanthi] Handler registered for 'GET' and  '{path}'")
        def wrapper(handler: ViewFunc) -> ViewFunc:
            self.routes['GET'][path] = handler
            return handler
        return wrapper

    def find_handler(self, environ: dict[str, Any]) -> ViewFunc:
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/')
        handler = self.routes[method].get(path, None)
        if handler is None:
            logger.error(f"[Jamanthi] Path '{path}' not found for '{method}'")
            raise NotFound(f"[Jamanthi] Path '{path}' not found for '{method}'")
        logger.info(f"[Jamanthi] Handler successfully retrieved for '{method}' and  '{path}'")
        return handler
    
    def run(self, host: str = "0.0.0.0", port: int = 8000)->None:
        from wsgiref.simple_server import make_server

        print(f"* Starting Jamanthi at http://{host}:{port}/")
        print(f"* Press Ctrl+C to force shutdown.")
        srv = make_server(host, port, self)
        
        try:
            srv.serve_forever()
        except KeyboardInterrupt: # Gracefully shutdown using Ctrl+C
            print(f"[Jamanthi] Shuttinf Down!!")
            srv.shutdown()
