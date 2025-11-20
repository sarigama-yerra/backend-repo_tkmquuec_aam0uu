import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Property, Booking, Testimonial, ContactMessage

app = FastAPI(title="Promparty Rent API", description="Backend for Promparty Rent website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdModel(BaseModel):
    id: str

# Public endpoints
@app.get("/")
def root():
    return {"name": "Promparty Rent", "status": "ok"}

@app.get("/properties", response_model=list)
def list_properties(city: Optional[str] = None, type: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    filt: dict = {}
    if city:
        filt["city"] = city
    if type:
        filt["type"] = type
    if min_price is not None or max_price is not None:
        price_q = {}
        if min_price is not None:
            price_q["$gte"] = min_price
        if max_price is not None:
            price_q["$lte"] = max_price
        filt["price"] = price_q
    docs = get_documents("property", filt)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/properties/{pid}")
def get_property(pid: str):
    try:
        doc = db["property"].find_one({"_id": ObjectId(pid)})
    except Exception:
        raise HTTPException(status_code=400, detail="معرف غير صالح")
    if not doc:
        raise HTTPException(status_code=404, detail="العقار غير موجود")
    doc["id"] = str(doc.pop("_id"))
    return doc

@app.post("/book")
def create_booking(payload: Booking):
    bid = create_document("booking", payload)
    return {"id": bid, "message": "تم استلام طلب الحجز وسنتواصل معك قريبًا"}

@app.post("/contact")
def contact_message(payload: ContactMessage):
    mid = create_document("contactmessage", payload)
    return {"id": mid, "message": "تم استلام رسالتك"}

@app.get("/testimonials")
def get_testimonials():
    docs = get_documents("testimonial", {}, limit=20)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.post("/seed")
def seed():
    # Seed minimal data if collections empty
    if db["property"].count_documents({}) == 0:
        sample_props: List[Property] = [
            Property(
                title="شقة فاخرة بإطلالة بحرية",
                city="طرابلس",
                type="شقة",
                price=350,
                price_unit="اليوم",
                size=140,
                bedrooms=3,
                bathrooms=2,
                images=[
                    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=1600&auto=format&fit=crop"
                ],
                amenities=["إنترنت عالي السرعة", "موقف خاص", "تكييف مركزي"],
                location_map="https://maps.google.com",
                description="شقة حديثة بتجهيزات فاخرة وموقع مميز قرب الكورنيش."
            ),
            Property(
                title="فيلا راقية مع مسبح",
                city="بنغازي",
                type="فيلا",
                price=12000,
                price_unit="الشهر",
                size=420,
                bedrooms=5,
                bathrooms=4,
                images=[
                    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?q=80&w=1600&auto=format&fit=crop"
                ],
                amenities=["مسبح", "حديقة واسعة", "خدمات نظافة"],
                location_map="https://maps.google.com",
                description="فيلا بمستوى راقٍ تناسب العائلات الكبيرة والإقامات الطويلة." 
            )
        ]
        for p in sample_props:
            create_document("property", p)
    if db["testimonial"].count_documents({}) == 0:
        create_document("testimonial", Testimonial(name="أحمد م.", city="طرابلس", rating=5, content="خدمة ممتازة وحجز سريع."))
        create_document("testimonial", Testimonial(name="ليلى ع.", city="بنغازي", rating=5, content="عقارات نظيفة وتعامل راقٍ."))
    return {"message": "تم تجهيز بيانات توضيحية"}

@app.get("/test")
def test_database():
    try:
        collections = db.list_collection_names()
        return {"backend": "ok", "db": "ok", "collections": collections}
    except Exception as e:
        return {"backend": "ok", "db": f"error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
