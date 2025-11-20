import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, Article

app = FastAPI(title="Canada CRS Waterworks API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Canada CRS Waterworks backend is running"}

# Health & DB test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Simple product list create endpoint
@app.post("/api/products", response_model=dict)
def create_product(product: Product):
    try:
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
def list_products(category: Optional[str] = None, limit: int = 50):
    try:
        filt = {"category": category} if category else {}
        docs = get_documents("product", filt, limit)
        # Convert ObjectId to string for JSON
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Articles (education)
@app.post("/api/articles", response_model=dict)
def create_article(article: Article):
    try:
        inserted_id = create_document("article", article)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/articles")
def list_articles(topic: Optional[str] = None, limit: int = 50):
    try:
        filt = {"topic": topic} if topic else {}
        docs = get_documents("article", filt, limit)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
