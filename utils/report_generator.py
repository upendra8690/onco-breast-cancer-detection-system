# utils/report_generator.py  ← REPLACE ENTIRE FILE
# Professional Drlogy-style report with actual AI prediction images
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas as rlcanvas
import sqlite3, os, io, matplotlib, matplotlib.pyplot as plt
matplotlib.use('Agg')
import qrcode
import cv2, numpy as np
from datetime import datetime
import pytz

IST        = pytz.timezone("Asia/Kolkata")
DARK_BLUE  = colors.HexColor("#003366")
MID_BLUE   = colors.HexColor("#0066CC")
LIGHT_BLUE = colors.HexColor("#E8F4FD")
RED_ALERT  = colors.HexColor("#CC0000")
GREEN_OK   = colors.HexColor("#006600")
ORANGE_WARN= colors.HexColor("#CC6600")
TBL_HDR    = colors.HexColor("#003366")
TBL_ALT    = colors.HexColor("#F0F7FF")
GREY_LINE  = colors.HexColor("#CCCCCC")
WHITE      = colors.white
BLACK      = colors.black

# ── Hospital config ────────────────────────────────────────────────────────────
HOSPITAL_NAME    = "CMR University Hospital"
HOSPITAL_DEPT    = "Onco AI Breast Cancer Detection System  |  AI-Powered Medical Diagnosis"
HOSPITAL_ADDR    = "CMR University, Bengaluru — 562149"
HOSPITAL_PHONE   = "📞 9342900666"
HOSPITAL_EMAIL   = "📧 onco@cmruniversity.edu.in"
HOSPITAL_WEB     = "www.cmruniversity.edu.in"

def _make_qr(text, path):
    qr = qrcode.QRCode(version=1, box_size=4, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(text); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)
    return path

def _conf_graph(dates, confs, path):
    fig, ax = plt.subplots(figsize=(5, 2.2))
    ax.plot(range(len(dates)), confs, marker='o', color='#003366', linewidth=2, markersize=7)
    ax.fill_between(range(len(dates)), confs, alpha=0.12, color='#0066CC')
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([str(d)[:10] for d in dates], rotation=30, ha='right', fontsize=7)
    ax.set_ylabel("Confidence (%)", fontsize=8)
    ax.set_title("AI Confidence Trend", fontsize=9, fontweight='bold')
    ax.set_ylim(0, 105)
    for i, c in enumerate(confs):
        ax.annotate(f"{c:.1f}%", (i, c), textcoords="offset points",
                    xytext=(0, 8), ha='center', fontsize=7, color='#003366')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path

def _save_image_for_pdf(img_bytes, path, label=""):
    """Save image bytes to temp file for PDF embedding."""
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return None
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.imshow(img_rgb)
        ax.set_title(label, fontsize=8, pad=4)
        ax.axis('off')
        plt.tight_layout(pad=0.3)
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        return path
    except:
        return None


class NumberedCanvas(rlcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(num)
            rlcanvas.Canvas.showPage(self)
        rlcanvas.Canvas.save(self)

    def _draw_header_footer(self, page_count):
        w, h = A4
        # ── Top bar ───────────────────────────────────────────────────────────
        self.setFillColor(DARK_BLUE)
        self.rect(0, h - 25*mm, w, 25*mm, fill=1, stroke=0)
        # Hospital name
        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 15)
        self.drawString(12*mm, h - 11*mm, HOSPITAL_NAME)
        self.setFont("Helvetica", 7.5)
        self.drawString(12*mm, h - 16*mm, HOSPITAL_DEPT)
        self.drawString(12*mm, h - 21*mm, HOSPITAL_ADDR)
        # Right contact
        self.setFont("Helvetica", 7)
        self.drawRightString(w - 12*mm, h - 10*mm, f"{HOSPITAL_PHONE}  |  {HOSPITAL_EMAIL}")
        self.drawRightString(w - 12*mm, h - 15*mm, HOSPITAL_WEB)
        # Accent line
        self.setFillColor(MID_BLUE)
        self.rect(0, h - 26.5*mm, w, 1.5*mm, fill=1, stroke=0)
        # ── Footer ────────────────────────────────────────────────────────────
        self.setFillColor(DARK_BLUE)
        self.rect(0, 0, w, 12*mm, fill=1, stroke=0)
        self.setFillColor(WHITE)
        self.setFont("Helvetica", 6.5)
        self.drawString(12*mm, 8*mm,
            "DISCLAIMER: This report is generated by an AI-assisted system for clinical decision support only.")
        self.drawString(12*mm, 4*mm,
            "All findings MUST be reviewed and confirmed by a qualified medical professional.")
        self.drawRightString(w - 12*mm, 8*mm, f"Page {self._pageNumber} of {page_count}")
        self.drawRightString(w - 12*mm, 4*mm,
            f"Generated: {datetime.now(IST).strftime('%d-%m-%Y %H:%M IST')}")
        self.setFillColor(MID_BLUE)
        self.rect(0, 12*mm, w, 1*mm, fill=1, stroke=0)


def generate_report(patient_id, lang="English",
                    ultrasound_img_bytes=None, gradcam_img_bytes=None):
    """
    Generate a professional Drlogy-style PDF report.
    ultrasound_img_bytes: raw bytes of uploaded ultrasound image (optional)
    gradcam_img_bytes:    raw bytes of GradCAM heatmap image (optional)
    """
    conn = sqlite3.connect("patients.db")
    cur  = conn.cursor()
    cur.execute("SELECT name,age,gender,phone,address FROM patients WHERE patient_id=?",
                (patient_id,))
    patient = cur.fetchone()
    if not patient:
        conn.close()
        return None

    cur.execute("""SELECT result,confidence,created FROM diagnosis
                   WHERE patient_id=? ORDER BY created""", (patient_id,))
    diagnoses = cur.fetchall()

    cur.execute("""SELECT risk_level,risk_score,created FROM risk_assessment
                   WHERE patient_id=? ORDER BY created DESC LIMIT 1""", (patient_id,))
    risk = cur.fetchone()

    cur.execute("""SELECT doctor_name,note,recommendation,follow_up_date
                   FROM doctor_notes WHERE patient_id=? ORDER BY created DESC LIMIT 1""",
                (patient_id,))
    note = cur.fetchone()
    conn.close()

    tmpfiles = []

    # ── QR Code ───────────────────────────────────────────────────────────────
    qr_path = f"tmp_qr_{patient_id}.png"
    _make_qr(
        f"ONCO AI REPORT\nPatient: {patient[0]}\nID: {patient_id}\n"
        f"Hospital: {HOSPITAL_NAME}\n{HOSPITAL_ADDR}\nVerified Report",
        qr_path
    )
    tmpfiles.append(qr_path)

    # ── Confidence graph ───────────────────────────────────────────────────────
    graph_path = None
    if diagnoses:
        graph_path = f"tmp_graph_{patient_id}.png"
        _conf_graph([d[2] for d in diagnoses], [d[1] for d in diagnoses], graph_path)
        tmpfiles.append(graph_path)

    # ── Save ultrasound + gradcam images if provided ──────────────────────────
    us_path  = None
    gcam_path= None
    if ultrasound_img_bytes:
        us_path = f"tmp_us_{patient_id}.png"
        r = _save_image_for_pdf(ultrasound_img_bytes, us_path, "Uploaded Ultrasound Image")
        if r: tmpfiles.append(us_path)
        else: us_path = None

    if gradcam_img_bytes:
        gcam_path = f"tmp_gcam_{patient_id}.png"
        r = _save_image_for_pdf(gradcam_img_bytes, gcam_path, "GradCAM Attention Heatmap")
        if r: tmpfiles.append(gcam_path)
        else: gcam_path = None

    # ── Build PDF ──────────────────────────────────────────────────────────────
    filename = f"report_{patient_id}.pdf"
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        topMargin=32*mm, bottomMargin=18*mm,
        leftMargin=12*mm, rightMargin=12*mm
    )
    styles = getSampleStyleSheet()
    story  = []

    def H(text, size=11, color=DARK_BLUE, bold=True, align=TA_LEFT):
        return Paragraph(text, ParagraphStyle('h',
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            fontSize=size, textColor=color, alignment=align, spaceAfter=2))

    def P(text, size=9, color=BLACK, bold=False):
        return Paragraph(text, ParagraphStyle('p',
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            fontSize=size, textColor=color, spaceAfter=2))

    story.append(Spacer(1, 3*mm))

    # ── SECTION 1: Patient Info ────────────────────────────────────────────────
    result_latest = diagnoses[-1][0] if diagnoses else "Pending"
    res_color = "#CC0000" if result_latest=="Malignant" else \
                ("#006600" if result_latest=="Benign" else "#0066CC")

    qr_img = RLImage(qr_path, width=20*mm, height=20*mm)

    info_data = [
        [Paragraph("<b>Patient Information</b>",
                   ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=11,
                                  textColor=DARK_BLUE)), "", "", "", qr_img],
        [P("<b>Patient ID</b>"), P(f": {patient_id}"),
         P("<b>Name</b>"),       P(f": {patient[0]}"), ""],
        [P("<b>Age</b>"),        P(f": {patient[1]} years"),
         P("<b>Gender</b>"),     P(f": {patient[2]}"), ""],
        [P("<b>Phone</b>"),      P(f": {patient[3]}"),
         P("<b>Address</b>"),    P(f": {patient[4]}"), ""],
        [P("<b>Report Date</b>"),P(f": {datetime.now(IST).strftime('%d-%m-%Y')}"),
         P("<b>Latest Result</b>"),
         Paragraph(f"<b>: <font color='{res_color}'>{result_latest}</font></b>",
                   ParagraphStyle('r', fontName='Helvetica-Bold', fontSize=9)), ""],
    ]

    info_tbl = Table(info_data, colWidths=[30*mm, 48*mm, 32*mm, 52*mm, 22*mm])
    info_tbl.setStyle(TableStyle([
        ("SPAN",         (0,0),(3,0)),
        ("SPAN",         (4,0),(4,4)),
        ("BACKGROUND",   (0,0),(3,0), LIGHT_BLUE),
        ("VALIGN",       (4,0),(4,0), "MIDDLE"),
        ("ALIGN",        (4,0),(4,0), "CENTER"),
        ("TOPPADDING",   (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING",  (0,0),(-1,-1), 4),
        ("BOX",          (0,0),(-1,-1), 0.5, GREY_LINE),
        ("INNERGRID",    (0,0),(-1,-1), 0.3, GREY_LINE),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 4*mm))

    # ── SECTION 2: Ultrasound + GradCAM Images (if available) ─────────────────
    if us_path or gcam_path:
        story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=3))
        story.append(H("Ultrasound Imaging & AI Analysis", 11))
        story.append(Spacer(1, 2*mm))

        img_row = []
        img_captions = []

        if us_path and os.path.exists(us_path):
            img_row.append(RLImage(us_path, width=78*mm, height=62*mm))
            img_captions.append(P("Uploaded Ultrasound Image", size=8, color=colors.grey))
        else:
            img_row.append(Spacer(1,1))
            img_captions.append(P(""))

        if gcam_path and os.path.exists(gcam_path):
            img_row.append(RLImage(gcam_path, width=78*mm, height=62*mm))
            img_captions.append(P("GradCAM AI Attention Heatmap", size=8, color=colors.grey))
        else:
            img_row.append(Spacer(1,1))
            img_captions.append(P(""))

        if len(img_row) == 2:
            img_tbl = Table([img_row, img_captions],
                            colWidths=[82*mm, 82*mm])
            img_tbl.setStyle(TableStyle([
                ("ALIGN",        (0,0),(-1,-1), "CENTER"),
                ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
                ("BOX",          (0,0),(-1,-1), 0.5, GREY_LINE),
                ("INNERGRID",    (0,0),(-1,-1), 0.3, GREY_LINE),
                ("TOPPADDING",   (0,0),(-1,-1), 4),
                ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ]))
            story.append(img_tbl)
            story.append(Spacer(1, 3*mm))

            # Image findings box
            if diagnoses:
                d = diagnoses[-1]
                res_col = RED_ALERT if d[0]=="Malignant" else \
                          GREEN_OK  if d[0]=="Benign"    else MID_BLUE
                impression = {
                    "Malignant": f"AI model detected MALIGNANT features with {d[1]:.1f}% confidence. Suspicious lesion noted. Urgent clinical review recommended.",
                    "Benign":    f"AI model classified as BENIGN with {d[1]:.1f}% confidence. No malignant features detected.",
                    "Normal":    f"AI model classified as NORMAL with {d[1]:.1f}% confidence. No abnormal findings.",
                }.get(d[0], "Classification pending.")
                suggestion = {
                    "Malignant": "Immediate referral to oncologist. Biopsy confirmation strongly recommended.",
                    "Benign":    "Continue regular annual screening. Self-examination monthly.",
                    "Normal":    "Routine annual mammogram at age 40+. Continue healthy lifestyle.",
                }.get(d[0], "Consult treating physician.")

                findings_data = [
                    [Paragraph("<b>IMPRESSION</b>",
                               ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE)),
                     Paragraph(f"<b><font color='#{res_col.hexval()[2:]}'>{d[0]}</font></b> — {impression}",
                               ParagraphStyle('fv', fontName='Helvetica', fontSize=9))],
                    [Paragraph("<b>SUGGESTION</b>",
                               ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE)),
                     P(suggestion, size=9)],
                    [Paragraph("<b>NOTE</b>",
                               ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE)),
                     P("The AI confidence score represents the model's prediction certainty. "
                       "This is an AI-assisted result — it does not replace clinical diagnosis by a radiologist.", size=8)],
                ]
                ft = Table(findings_data, colWidths=[25*mm, 152*mm])
                ft.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0),(0,-1), DARK_BLUE),
                    ("ROWBACKGROUNDS",(1,0),(1,-1), [LIGHT_BLUE, TBL_ALT, WHITE]),
                    ("VALIGN",        (0,0),(-1,-1), "TOP"),
                    ("TOPPADDING",    (0,0),(-1,-1), 5),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 5),
                    ("LEFTPADDING",   (0,0),(-1,-1), 6),
                    ("BOX",           (0,0),(-1,-1), 0.8, DARK_BLUE),
                    ("INNERGRID",     (0,0),(-1,-1), 0.3, GREY_LINE),
                ]))
                story.append(ft)
                story.append(Spacer(1, 4*mm))

    # ── SECTION 3: Diagnosis History ──────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=3))
    story.append(H("Diagnosis History — All Visits", 11))
    story.append(Spacer(1, 2*mm))

    if diagnoses:
        hdr = [Paragraph(f"<b>{t}</b>",
               ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=9,
                              textColor=WHITE, alignment=TA_CENTER))
               for t in ["Visit","Date & Time","AI Result","Confidence","Clinical Status"]]
        rows = [hdr]
        for i, d in enumerate(diagnoses):
            rc = RED_ALERT if d[0]=="Malignant" else (GREEN_OK if d[0]=="Benign" else MID_BLUE)
            st = "⚠ Urgent Review" if d[0]=="Malignant" else ("✓ Normal" if d[0]=="Normal" else "✓ Non-cancerous")
            rows.append([
                P(f"Visit {i+1}", size=9),
                P(str(d[2])[:19], size=8),
                Paragraph(f"<b><font color='#{rc.hexval()[2:]}'>{d[0]}</font></b>",
                          ParagraphStyle('td', fontName='Helvetica-Bold', fontSize=9, alignment=TA_CENTER)),
                Paragraph(f"<b>{d[1]:.2f}%</b>",
                          ParagraphStyle('td', fontName='Helvetica-Bold', fontSize=9,
                                        textColor=rc, alignment=TA_CENTER)),
                P(st, size=8),
            ])
        dt = Table(rows, colWidths=[20*mm, 48*mm, 36*mm, 30*mm, 48*mm])
        ts = [
            ("BACKGROUND",    (0,0),(-1,0), TBL_HDR),
            ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[TBL_ALT, WHITE]),
            ("ALIGN",         (0,0),(-1,-1),"CENTER"),
            ("VALIGN",        (0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("BOX",           (0,0),(-1,-1), 0.8, DARK_BLUE),
            ("INNERGRID",     (0,0),(-1,-1), 0.3, GREY_LINE),
        ]
        for i, d in enumerate(diagnoses, 1):
            if d[0]=="Malignant":
                ts.append(("BACKGROUND",(0,i),(-1,i),colors.HexColor("#FFF0F0")))
        dt.setStyle(TableStyle(ts))
        story.append(dt)
    else:
        story.append(P("No diagnosis records found.", color=colors.grey))
    story.append(Spacer(1, 4*mm))

    # ── SECTION 4: Confidence Graph ────────────────────────────────────────────
    if graph_path and diagnoses:
        story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=3))
        story.append(H("AI Confidence Trend", 11))
        story.append(Spacer(1, 2*mm))
        story.append(RLImage(graph_path, width=155*mm, height=55*mm))
        story.append(Spacer(1, 4*mm))

    # ── SECTION 5: Risk Assessment ─────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=3))
    story.append(H("Risk Assessment", 11))
    story.append(Spacer(1, 2*mm))
    if risk:
        rc2 = RED_ALERT if "High" in risk[0] else (ORANGE_WARN if "Moderate" in risk[0] else GREEN_OK)
        risk_tbl = Table([
            [P("<b>Risk Level</b>",bold=True), P("<b>Score</b>",bold=True), P("<b>Assessment Date</b>",bold=True)],
            [Paragraph(f"<b><font color='#{rc2.hexval()[2:]}'>{risk[0]}</font></b>",
                       ParagraphStyle('rv', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER)),
             Paragraph(f"<b>{risk[1]}/17</b>",
                       ParagraphStyle('rv', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER)),
             P(str(risk[2])[:19], size=9)],
        ], colWidths=[60*mm, 60*mm, 62*mm])
        risk_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0), TBL_HDR),
            ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
            ("BACKGROUND",    (0,1),(-1,1), LIGHT_BLUE),
            ("ALIGN",         (0,0),(-1,-1),"CENTER"),
            ("VALIGN",        (0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("BOX",           (0,0),(-1,-1), 0.8, DARK_BLUE),
            ("INNERGRID",     (0,0),(-1,-1), 0.3, GREY_LINE),
        ]))
        story.append(risk_tbl)
    else:
        story.append(P("No risk assessment completed yet.", color=colors.grey))
    story.append(Spacer(1, 4*mm))

    # ── SECTION 6: Doctor Notes ────────────────────────────────────────────────
    if note:
        story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=3))
        story.append(H("Doctor's Clinical Notes & Recommendation", 11))
        story.append(Spacer(1, 2*mm))
        nd = [
            [P("<b>Field</b>",bold=True), P("<b>Details</b>",bold=True)],
            [P("Doctor"),         P(note[0])],
            [P("Clinical Note"),  P(note[1])],
            [P("Recommendation"), P(note[2])],
            [P("Follow-up Date"), P(note[3] or "Not specified")],
        ]
        nt = Table(nd, colWidths=[40*mm, 142*mm])
        nt.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0), TBL_HDR),
            ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[TBL_ALT, WHITE]),
            ("VALIGN",        (0,0),(-1,-1),"TOP"),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("BOX",           (0,0),(-1,-1), 0.8, DARK_BLUE),
            ("INNERGRID",     (0,0),(-1,-1), 0.3, GREY_LINE),
        ]))
        story.append(nt)
        story.append(Spacer(1, 4*mm))

    # ── SECTION 7: Model Reference ─────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=3))
    story.append(H("AI Model Reference Information", 11))
    story.append(Spacer(1, 2*mm))
    ref_data = [
        [P("<b>Parameter</b>",bold=True), P("<b>Value</b>",bold=True), P("<b>Benchmark</b>",bold=True)],
        [P("Model"),          P("CNN + VGG19"),          P("BUSI Dataset (Cairo University)")],
        [P("Accuracy"),       P("93.0%"),                P("Better than 4 published methods")],
        [P("Classification"), P("Benign/Malignant/Normal"),P("3-class softmax output")],
        [P("Image Size"),     P("224 × 224 pixels"),      P("Standardized preprocessing")],
        [P("Explainability"), P("GradCAM Heatmap"),       P("Visual attention region")],
    ]
    rt = Table(ref_data, colWidths=[45*mm, 72*mm, 65*mm])
    rt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), TBL_HDR),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[TBL_ALT, WHITE]),
        ("ALIGN",         (0,0),(-1,-1),"LEFT"),
        ("VALIGN",        (0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 0.8, DARK_BLUE),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, GREY_LINE),
    ]))
    story.append(rt)
    story.append(Spacer(1, 6*mm))

    # ── SECTION 8: Signatures ──────────────────────────────────────────────────
    sig_data = [[
        Paragraph("___________________<br/><b>Medical Lab Technician</b><br/>(AI System Operator)",
                  ParagraphStyle('s', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)),
        Paragraph("___________________<br/><b>Radiologist / Doctor</b><br/>(Clinical Reviewer)",
                  ParagraphStyle('s', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)),
        Paragraph("___________________<br/><b>Senior Oncologist</b><br/>(Final Authority)",
                  ParagraphStyle('s', fontName='Helvetica', fontSize=8, alignment=TA_CENTER)),
    ]]
    st_tbl = Table(sig_data, colWidths=[60*mm, 60*mm, 62*mm])
    st_tbl.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),8)]))
    story.append(st_tbl)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("**** End of Report ****",
                            ParagraphStyle('end', fontName='Helvetica', fontSize=8,
                                           textColor=colors.grey, alignment=TA_CENTER)))

    doc.build(story, canvasmaker=NumberedCanvas)

    for f in tmpfiles:
        try: os.remove(f)
        except: pass

    return filename
