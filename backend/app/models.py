# models.py
from datetime import date, datetime
from sqlmodel import SQLModel, Field

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    merchant: str
    receipt_date: date
    total: float
    category: str
    saved_at: datetime = Field(default_factory=datetime.now)