from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def generate_statement(account, month_date):
    """
    Generate a PDF bank statement for a given account + month.
    Returns a Django ContentFile.
    """

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, 750, "Bank Statement")

    c.setFont("Helvetica", 11)
    c.drawString(40, 725, f"Account: {account.nickname or account.get_account_type_display()}")
    c.drawString(40, 710, f"Account ID: {account.public_id}")
    c.drawString(40, 695, f"Statement Month: {month_date.strftime('%B %Y')}")

    # Table header
    y = 660
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Date")
    c.drawString(120, y, "Description")
    c.drawString(420, y, "Amount")

    c.setFont("Helvetica", 10)
    y -= 20

    transactions = account.transactions.filter(
        created_at__year=month_date.year,
        created_at__month=month_date.month,
    ).order_by("created_at")

    if not transactions.exists():
        c.drawString(40, y, "No transactions for this period.")
    else:
        for txn in transactions:
            if y < 60:
                c.showPage()
                y = 750
                c.setFont("Helvetica", 10)

            c.drawString(40, y, txn.created_at.strftime("%Y-%m-%d"))
            c.drawString(120, y, txn.memo or txn.txn_type)
            c.drawRightString(500, y, f"${txn.amount}")
            y -= 16

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()

    return ContentFile(pdf)
