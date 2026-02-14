import io
import logging

from reportlab.pdfgen import canvas


logger = logging.getLogger(__name__)


sale = {
    "result": {"is_ok": "true", "has_warnings": "false"},
    "details": {
        "origin": "Gualeguaychú(Av Costanera y Rivera)",
        "destination": "RETIRO",
        "departure": "2025-06-30 10:00",
        "arrival": "2025-06-30 14:05",
        "created": "2025-06-29 18:21",
        "category": "                              ",
        "company": "EVA",
        "company_description": "EL VALLE TURISM",
        "company_address": "MALASPINA 2569 - HURLINGHAM - Santiago de Chile - Suiza",
        "company_tax_category": "Responsable Inscript",
        "company_tax_id": None,
        "company_tax_iibb": "               ",
        "company_email": "                                                                           ",
    },
    "items": [
        {
            "ticket_number": "10283",
            "seat": "42",
            "price_gross": "600.0000",
            "price_net": "600.0000",
            "first_name": "Narendra",
            "last_name": "Pal",
            "document_type": "D.N.I.",
            "document_number": "8763389",
            "Nationality": "Argentina",
            "date_of_birth": "1981-10-27",
            "phone_number": "119321234",
            "email": "passenger@email.com",
            "gender": "M",
            "bar_code": "0000000102838888899999999999000600,00  02072025180018A5    00000001000PAL NARENDRA                            108763389       1000096",
            "qr_code": "10283",
        },
        {
            "ticket_number": "10284",
            "seat": "43",
            "price_gross": "600.0000",
            "price_net": "600.0000",
            "first_name": "Aastha",
            "last_name": "Chadha",
            "document_type": "D.N.I.",
            "document_number": "92283001",
            "Nationality": "Argentina",
            "date_of_birth": "1982-07-01",
            "phone_number": "118321234",
            "email": "passenger@email.com",
            "gender": "F",
            "bar_code": "0000000102848888899999999999000600,00  02072025180018A5    00000011000CHADHA AASTHA                           192283001       1000091",
            "qr_code": "10284",
        },
    ],
}


class Render:
    def get_ticket_pdf(self):
        # first we create a file like buffer to receive PDF data
        buffer = io.BytesIO()

        # Create the PDF object using the buffer as its 'file'
        p = canvas.Canvas(buffer)

        # Draw things on the pdf
        p.drawString(100, 100, "Hello Veer")

        # Close the PDF object cleanly
        p.showPage()
        p.save()

        buffer.seek(0)

        return buffer
