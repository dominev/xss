"""
Pocket Crawl Lint Soup α0.1

    pip install -r requirements.txt
    python app.py

Ports → 8000 → Open in Browser
Login stub: admin / admin
"""

from __future__ import annotations

import uvicorn

if __name__ == "__main__":
    uvicorn.run("tuta.web:app", host="0.0.0.0", port=8000, reload=True)
