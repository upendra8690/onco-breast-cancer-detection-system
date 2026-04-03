# utils/qr_generator.py
import qrcode
from PIL import Image
import io
import os


def generate_patient_qr(patient_id, patient_name, hospital="Onco AI Hospital"):
    """
    Generate a QR code for a patient that encodes their ID and info.
    Returns image bytes for embedding in PDF or display.
    """
    qr_data = (
        f"ONCO-PATIENT\n"
        f"ID: {patient_id}\n"
        f"Name: {patient_name}\n"
        f"Hospital: {hospital}\n"
        f"System: Onco Breast Cancer AI\n"
        f"Scan to access patient record"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="#0a0f1e",
        back_color="white"
    )

    # Save to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # Also save to file for PDF embedding
    path = f"qr_{patient_id}.png"
    img.save(path)

    return buf, path


def generate_report_qr(patient_id, report_date):
    """Generate QR for report verification."""
    qr_data = (
        f"ONCO-REPORT\n"
        f"Patient: {patient_id}\n"
        f"Date: {report_date}\n"
        f"Verified by: Onco AI System v2.0\n"
        f"This report is AI-generated and requires doctor verification."
    )

    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    path = f"qr_report_{patient_id}.png"
    img.save(path)
    return path