from datetime import date
from pydantic import BaseModel

class ExtractedFields(BaseModel):
    merchant: str | None
    date: date | None
    total: float | None
    raw_text: str

class ExpenseIn(BaseModel):
    merchant: str
    receipt_date: date
    total: float
    category: str