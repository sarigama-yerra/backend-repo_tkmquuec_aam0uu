"""
Database Schemas for Promparty Rent

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase class name.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class Property(BaseModel):
    title: str = Field(..., description="عنوان العقار")
    city: str = Field(..., description="المدينة")
    type: str = Field(..., description="نوع العقار: شقة، فيلا، مكتب، قاعة")
    price: float = Field(..., ge=0, description="السعر")
    price_unit: str = Field(..., description="اليوم أو الشهر")
    size: Optional[int] = Field(None, description="المساحة بالمتر")
    bedrooms: Optional[int] = Field(None, description="عدد الغرف")
    bathrooms: Optional[int] = Field(None, description="عدد الحمامات")
    images: List[str] = Field(default_factory=list, description="روابط الصور")
    amenities: List[str] = Field(default_factory=list, description="المزايا")
    location_map: Optional[str] = Field(None, description="رابط خريطة جوجل")
    description: Optional[str] = Field(None, description="وصف العقار")

class Booking(BaseModel):
    property_id: str = Field(..., description="معرف العقار")
    name: str = Field(..., description="الاسم الكامل")
    phone: str = Field(..., description="رقم الهاتف")
    start_date: str = Field(..., description="تاريخ البداية ISO")
    end_date: str = Field(..., description="تاريخ النهاية ISO")
    notes: Optional[str] = Field(None, description="ملاحظات")

class Testimonial(BaseModel):
    name: str = Field(..., description="اسم العميل")
    city: Optional[str] = Field(None, description="المدينة")
    rating: int = Field(5, ge=1, le=5, description="التقييم من 1 إلى 5")
    content: str = Field(..., description="رأي العميل")

class ContactMessage(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    message: str
