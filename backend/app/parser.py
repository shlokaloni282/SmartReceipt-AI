import re
from datetime import datetime

DATE_PATTERN = re.compile(
    r"\b(?:"
    r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
    r"|"
    r"\d{4}[./-]\d{1,2}[./-]\d{1,2}"
    r")\b"
)

MONEY_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)"
    r"(?!\d)"
)

TOTAL_LABELS = [
    (re.compile(r"\bgrand\s+total\b", re.I), 100),
    (re.compile(r"\bnet\s*a[mnh]t\b", re.I), 95),
    (re.compile(r"\bnet\s*amount\b", re.I), 95),
    (re.compile(r"\btotal\s+(?:amount|payable|due)\b", re.I), 90),
    (re.compile(r"\bamount\s+(?:due|payable)\b", re.I), 85),
    (re.compile(r"\bpayable\b", re.I), 75),
    (re.compile(r"^\s*total\b", re.I), 60),
]

SKIP_MERCHANT_LINE = re.compile(
    r"\b(ocr pass|tax invoice|gstin|fssai|phone|mobile|bill no|invoice no|"
    r"date|cashier|address|computer generated|patient|doctor)\b",
    re.I,
)

SKIP_TOTAL_LINE = re.compile(
    r"\b(sub\s*total|total\s*(?:cgst|sgst|igst)|taxable|gstin|fssai|"
    r"cash|balance|change|discount|amount\s*received)\b",
    re.I,
)


def parse_receipt_date(text: str):
    """Return a parsed date, or None if OCR found no valid date."""
    matches = []

    labelled = re.search(
        rf"\b(?:bill\s*date|invoice\s*date|date)\b\D{{0,20}}({DATE_PATTERN.pattern})",
        text,
        flags=re.I,
    )
    if labelled:
        matches.append(labelled.group(1))

    matches.extend(DATE_PATTERN.findall(text))

    formats = (
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
        "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
    )

    for raw in matches:
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue

    return None


def find_merchant(lines: list[str]) -> str:
    """Choose a likely merchant name from the receipt's top lines."""
    candidates = []

    for index, line in enumerate(lines[:20]):
        line = line.strip()

        if not line or SKIP_MERCHANT_LINE.search(line):
            continue

        letters = re.findall(r"[A-Za-z]", line)
        digits = sum(char.isdigit() for char in line)

        if len(letters) < 4 or digits >= 5:
            continue

        score = min(len(letters), 40)
        if re.search(
            r"\b(mart|market|store|supermarket|medico|medical|pharmacy)\b",
            line,
            re.I,
        ):
            score += 20

        score -= index * 0.5
        candidates.append((score, line[:80]))

    return max(candidates, default=(0, ""))[1]


def find_total(lines: list[str]):
    """Return an amount only when it appears beside a total label."""
    candidates = []

    for index, line in enumerate(lines):
        if SKIP_TOTAL_LINE.search(line):
            continue

        scores = [
            score
            for pattern, score in TOTAL_LABELS
            if pattern.search(line)
        ]
        if not scores:
            continue

        amounts = MONEY_PATTERN.findall(line)
        if not amounts and index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if MONEY_PATTERN.fullmatch(next_line.replace(" ", "")):
                amounts = MONEY_PATTERN.findall(next_line)

        if not amounts:
            continue

        try:
            amount = float(amounts[-1].replace(",", ""))
        except ValueError:
            continue

        if 0 < amount <= 10_000_000:
            candidates.append((max(scores), index, amount))

    if not candidates:
        return None

    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def extract_receipt_fields(text: str) -> dict:
    """Extract editable merchant, date, and total suggestions from OCR text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    return {
        "merchant": find_merchant(lines),
        "date": parse_receipt_date(text),
        "total": find_total(lines),
    }