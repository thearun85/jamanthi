# Jamanthi
A tiny Python web framework built from scratch on top of WSGI.

## Installation
Jamanthi is not yet on PyPI. Install directly from the repository:
```bash
git clone https://github.com/thearun85/jamanthi
cd jamanthi
poetry install

poetry run python -m portfolio.main 
```

---

## Quickstart

```python
from jamanthi import Jamanthi

app = Jamanthi(__name__)

@app.get("/")
def home(request):
    return "Hello from Jamanthi"

app.run(debug=True)
```

---

## Features

### Routing
Register handlers for GET routes using the `@app.get()` decorator.

```python
@app.get("/about")
def about(request):
    return "About"
```

### Static Files
Place files in a `static/` directory next to your app. They are served automatically at `/static/<filename>`.

```html

```

### Request Object
Every handler receives a `Request` object with `method` and `path`.

```python
@app.get("/")
def home(request):
    return f"Method: {request.method}, Path: {request.path}"
```

### Auto-Reloader
Pass `debug=True` to `app.run()`. Jamanthi watches `.py`, `.html`, and `.css` files and restarts the server automatically on changes.

```python
app.run(debug=True)
```

### Live Browser Reload
In debug mode, Jamanthi injects a small script into every HTML response. When the server restarts, the browser detects the change and reloads the page automatically — no manual refresh needed.

---

## Why Jamanthi?

Jamanthi is built as a learning exercise and portfolio project — to understand how web frameworks like Flask work under the hood. Every feature is implemented from scratch: WSGI handling, routing, static file serving, and the dev server.

The framework powers this portfolio site. "Built with Jamanthi" is not a tagline — it's a test.

---

## Status

`0.1.0` — early development. API will change.

| Feature | Status |
|---|---|
| GET routing | ✅ |
| Static file serving | ✅ |
| Request object | ✅ |
| Auto-reloader | ✅ |
| Live browser reload | ✅ |

---

# License

MIT
