from io import BytesIO
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from sqlalchemy import desc
from sqlmodel import Session, select

from .db import init_db, get_session
from .models import Expense
from .schemas import ExtractedFields, ExpenseIn
from .ocr import orient_image, run_ocr_multi
from .parser import extract_receipt_fields

app = FastAPI(title="SmartReceipt AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/receipts/extract", response_model=ExtractedFields)
async def extract(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg", "image/webp"):
        raise HTTPException(400, "Upload a PNG, JPG or WEBP image")
    image = orient_image(Image.open(BytesIO(await file.read())), 0)
    text = run_ocr_multi(image, 11)
    fields = extract_receipt_fields(text)
    return ExtractedFields(**fields, raw_text=text)

@app.post("/expenses", response_model=Expense)
def create_expense(data: ExpenseIn, session: Session = Depends(get_session)):
    expense = Expense(**data.model_dump())
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense

@app.get("/expenses", response_model=list[Expense])
def list_expenses(session: Session = Depends(get_session)):
    return session.exec(select(Expense).order_by(desc(Expense.receipt_date))).all()

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(404, "Not found")
    session.delete(expense)
    session.commit()
    return {"ok": True}