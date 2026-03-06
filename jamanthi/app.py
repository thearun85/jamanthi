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

class Request:
    def __init__(self, environ: dict[str, Any]) -> None:
        self._environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.path = environ.get('PATH_INFO', '/')

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
        self.static_path = os.path.join(self.root_path, "static")
        
        logger.info(f"[Jamanthi] App initialized with name {name}")

    # Callable which web servers will call invoke when a request arrives
    def __call__(self, environ: dict[str, Any], start_response: StartResponse) -> list[bytes]:

        self.request = Request(environ)
        status = 200
        content_type = 'text/html'

        # Handle css files
        if self.request.path.startswith('/static/'):
            return self.static_handler(self.request, start_response)
        else:
            # Handle custom handlers
            try:
                handler = self.find_handler(self.request)
            except NotFound:
                logger.error(f"[Jamanthi] Handler not registered")
                return not_found(start_response)

            body = handler(self.request)
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

    def find_handler(self, request: Request) -> ViewFunc:
        method = request.method
        path = request.path
        handler = self.routes[method].get(path, None)
        if handler is None:
            logger.error(f"[Jamanthi] Path '{path}' not found for '{method}'")
            raise NotFound(f"[Jamanthi] Path '{path}' not found for '{method}'")
        logger.info(f"[Jamanthi] Handler successfully retrieved for '{method}' and  '{path}'")
        return handler

    def static_handler(self, request: Request, start_response: StartResponse) -> list[bytes]:

        file_name = request.path[len('/static/'):]
        file_path = os.path.join(self.static_path, file_name)
        logger.info(f"[Jamanthi] Static file path is {file_path}")
        if not os.path.exists(file_path):
            raise NotFound(f"[Jamanthi] File not found: {file_name}")

        start_response(HTTP_STATUS_MAPPINGS[200], [('Content-Type', 'text/css')])
        
        with open(file_path, "rb") as f:
            return [f.read()]
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False)->None:
    
        if debug and os.environ.get('JAMANTHI_CHILD', -1) != '1':
            self._run_with_reloader(host, port)

        else:
            self._serve(host, port) 

    def _run_with_reloader(self, host: str, port: int) -> None:
        import subprocess
        import time
        
        env = os.environ.copy()
        env['JAMANTHI_CHILD'] = '1'

        while True:
            process = subprocess.Popen(
                [sys.executable] + sys.argv,
                env=env
            )
            mtimes: dict[str, float] = {}
            try:
                while process.poll() is None:
                    if self._files_changed(mtimes):
                        print(f"[Jamanthi] Detected file changes. Reloading...")
                        process.terminate()
                        process.wait()
                        break
                    time.sleep(1)
                else:
                    break
            except KeyboardInterrupt:
                print(f"[Jamanthi] Shutting down...")
                process.terminate()
                process.wait()
                break
    
    def _serve(self, host: str, port: int)->None:
        from wsgiref.simple_server import make_server
        print(f"* Starting Jamanthi at http://{host}:{port}/")
        print(f"* Press Ctrl+C to force shutdown.")
        srv = make_server(host, port, self)
        
        srv.serve_forever()

    def _files_changed(self, mtimes: dict[str, float]) -> bool:
        # Check and return True if files have changed
        for file in self._watch_files():
            mtime = os.stat(file).st_mtime
            if file in mtimes:
                if mtimes[file] != mtime:
                    return True
            mtimes[file] = mtime
        return False
            
    def _watch_files(self) -> list[str]:
        # Return a list of files that must be watched for changes
        watched = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith(('.py', '.html', '.css')):
                    watched.append(os.path.join(root, file))

        return watched
