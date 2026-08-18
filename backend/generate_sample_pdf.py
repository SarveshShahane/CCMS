import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(filename="sample_complaint.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
    )
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#0F172A'),
    )

    story.append(Paragraph("PHARMACEUTICAL QUALITY COMPLAINT REPORT", title_style))
    story.append(Paragraph("FORMAL DEFECT SUBMISSION & INCIDENT NOTICE", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=15))

    meta_data = [
        [Paragraph("<b>Date of Report:</b> 18 August 2026", body_style), Paragraph("<b>Complaint Source:</b> Pharmacy", body_style)],
        [Paragraph("<b>Customer Name:</b> Apollo Pharmacy Main Branch", body_style), Paragraph("<b>Contact Email:</b> quality_manager@apollohealth.com", body_style)],
        [Paragraph("<b>Contact Phone:</b> +91-9876543210", body_style), Paragraph("<b>Report Ref ID:</b> REF-2026-AP-884", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Product & Batch Information", ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1E293B'))))
    story.append(Spacer(1, 6))

    product_data = [
        [Paragraph("Field", header_style), Paragraph("Specification Details", header_style)],
        [Paragraph("Product Name", body_style), Paragraph("Amoxicillin Trihydrate Capsules 500 mg", body_style)],
        [Paragraph("Product Code / SKU", body_style), Paragraph("AMX-500-CAP", body_style)],
        [Paragraph("Dosage Form & Strength", body_style), Paragraph("Capsules, 500 mg", body_style)],
        [Paragraph("Batch / Lot Number", body_style), Paragraph("BATCH-AMX2026-09A", body_style)],
        [Paragraph("Affected Quantity", body_style), Paragraph("1500 capsules (15 commercial boxes)", body_style)],
        [Paragraph("Defect Category", body_style), Paragraph("Discoloration and Capsule Capping", body_style)],
        [Paragraph("Manufacturing Date", body_style), Paragraph("10 March 2026", body_style)],
        [Paragraph("Expiry Date", body_style), Paragraph("31 August 2028", body_style)],
        [Paragraph("Incident Date", body_style), Paragraph("15 August 2026", body_style)],
    ]
    prod_table = Table(product_data, colWidths=[180, 360])
    prod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Incident Summary & Description", ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1E293B'))))
    story.append(Spacer(1, 6))

    desc_text = (
        "During routine incoming quality control inspection at Apollo Pharmacy Main Branch on 15 August 2026, "
        "our QA team unboxed shipment lot for Amoxicillin 500 mg capsules (Batch: BATCH-AMX2026-09A). "
        "Upon inspecting 3 sealed blister packs, multiple capsules exhibited severe yellowish-brown discoloration "
        "and capsule body separation (capping). A total of 1,500 capsules across 15 boxes have been quarantined immediately. "
        "This quality defect poses potential patient safety concerns and stability compromise. "
        "We request urgent quality investigation, CAPA assessment, and immediate batch replacement."
    )
    story.append(Paragraph(desc_text, body_style))
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    story.append(Paragraph("Submitted by Quality Assurance Lead — Apollo Pharmacy", ParagraphStyle('Footer', parent=styles['Italic'], fontSize=9, textColor=colors.HexColor('#94A3B8'))))

    doc.build(story)
    print(f"Successfully generated PDF: {os.path.abspath(filename)}")

if __name__ == "__main__":
    generate_pdf()
