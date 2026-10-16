# SmartReceipt AI

A beginner-friendly receipt processing MVP. Upload a printed receipt image and run local Tesseract OCR, or paste receipt text. The app uses transparent parsing rules to suggest a merchant, date, and total; you can correct the fields, assign a category, save the expense for the current browser session, view a spending summary, and download the session as CSV.

This demonstrates a small document-processing flow: OCR converts image pixels into text, and rule-based extraction turns some of that text into structured fields. It is a prototype, not a trained AI model or a production expense system. Receipt layouts vary, so check every extracted value. Expenses are held in Streamlit session memory and are not saved after the session ends.

## Run locally on Windows

1. Install Python 3.10 or newer. During installation, select **Add Python to PATH**.
2. Install the Tesseract OCR engine and ensure its install folder is on PATH. The `pytesseract` Python package is only a connector; it does not install the Tesseract engine. See the [Tesseract project installation notes](https://github.com/tesseract-ocr/tesseract).
3. Open PowerShell in this project folder and create an isolated environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

4. If PowerShell blocks environment activation, use Command Prompt instead:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate.bat
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

The app opens in a browser. For a quick demo without the OCR engine, paste the sample below and choose **Extract from pasted text**.

## Smoke check

Paste this sample:

```text
GREEN MART
Date: 15/10/2026
Milk 60.00
Bread 40.00
Grand Total Rs. 100.00
```

Expected suggestions: merchant `GREEN MART`, date `2026-10-15`, total `₹100.00`. Correct any field, save it, then confirm the expense appears in the table and the CSV download opens.

## What is implemented

- PNG, JPG, JPEG, and WEBP receipt upload.
- Local Tesseract OCR with grayscale and contrast preprocessing.
- Heuristic suggestions for merchant, date, and total, plus manual editing.
- Expense category, session-only table, category chart, and CSV export.
- Pasted-text path so the extraction flow can be shown even before OCR is installed.

## Known limits

- Rules are intentionally small and may misread unfamiliar date formats, currencies, totals, or merchant names.
- No line-item extraction, cloud sync, login, database, tax handling, or claim of production-grade accuracy.
- Image OCR requires a separately installed Tesseract executable.

## Resume wording

Use only after you have run the app and verified the smoke check:

> Built SmartReceipt AI, a Streamlit receipt-processing MVP using Tesseract OCR and Python parsing rules to extract editable merchant, date, and total fields; added expense categorization, session summaries, and CSV export.

For GitHub, create a repository named `smartreceipt-ai`, add these files, and include one screenshot of the running app. Do not upload real receipts because they may contain personal information.
