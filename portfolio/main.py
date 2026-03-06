import os
from jamanthi import Jamanthi, Request

app = Jamanthi(__name__)

@app.get("/")
def home(request: Request)->str:
    html_file_path = os.path.join(app.html_path, "home.html")
    with open(html_file_path, "r") as f:
        return f.read()
    
app.run()
