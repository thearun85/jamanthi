from jamanthi import Jamanthi

app = Jamanthi(__name__)

@app.get("/")
def home()->str:
    return f"Welcome to my Portfolio Website"
    
app.run()
