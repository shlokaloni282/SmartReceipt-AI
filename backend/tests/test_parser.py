from app.parser import extract_receipt_fields


SAMPLE_RECEIPT = """
SAGAR MEDICO
GST TAX INVOICE
Invoice No: CA/3012
Date: 13-06-2026

QTY X PACK  PRODUCT                  AMOUNT
1 x 15 TAB  GALVUSMET 50 / 500       354.71
1 x 20 TAB  NEUROKIND OD             202.02
1 x 300 ML  HEPATOGLOBINE SYRUP      256.19
1 x 15 TAB  DAPANORM 10              282.57

TOTAL CGST: 27.38     SGST: 27.38
GROSS: 1095.49
ADD: 54.76
LESS: 0.00
NET AMT: 1150.25
"""


def main() -> None:
    result = extract_receipt_fields(SAMPLE_RECEIPT)

    print("Parser result:")
    print(result)

    assert result.get("merchant"), "Merchant was not detected"
    assert result.get("date"), "Date was not detected"
    assert result.get("total") is not None, "Total was not detected"

    print("\nBasic parser checks passed.")


if __name__ == "__main__":
    main()