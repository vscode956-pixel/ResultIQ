#!/usr/bin/env python
"""Generate PDF report from analysis data (A4 Portrait, no template)"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader
from PIL import Image
import datetime
import json
import re

from category_mapping import extract_program_code


def create_pdf_report(data, output_path):
    """Create PDF report from analysis data."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=24,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=14,
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=15,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=18,
    )

    info_label_style = ParagraphStyle(
        'InfoLabel',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111827'),
        leading=14,
        alignment=TA_LEFT,
    )

    info_value_style = ParagraphStyle(
        'InfoValue',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica',
        textColor=colors.HexColor('#111827'),
        leading=14,
        alignment=TA_LEFT,
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=17,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=8,
        fontName='Helvetica-Bold',
    )

    body_font_size = 11

    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=body_font_size,
        leading=13,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )

    cell_left_style = ParagraphStyle(
        'CellLeft',
        parent=styles['Normal'],
        fontSize=body_font_size,
        leading=13,
        alignment=TA_LEFT,
        fontName='Helvetica',
    )

    logo_path = r'D:\projects\SIMS-Result-analysis\Untitled_design.png'
    logo_flowable = None
    try:
        with Image.open(logo_path) as img:
            img = img.convert('RGB')
            max_width = 29 * mm
            max_height = 29 * mm
            ratio = min(max_width / img.width, max_height / img.height, 1)
            width = img.width * ratio
            height = img.height * ratio
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            logo_flowable = RLImage(buffer, width=width, height=height)
    except Exception:
        logo_flowable = None

    header_rows = []
    header_text = [
        Paragraph('<b>SOUNDARYA EDUCATIONAL TRUST (REGD.)</b>', ParagraphStyle('TrustName', parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold', textColor=colors.HexColor('#111827'), alignment=TA_CENTER, leading=16, letterSpacing=0.5)),
        Paragraph('<b>SOUNDARYA INSTITUTE OF MANAGEMENT & SCIENCE</b>', ParagraphStyle('CollegeName', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold', textColor=colors.HexColor('#111827'), alignment=TA_CENTER, leading=20)),
        Paragraph('<font color="#6B7280">Soundarya Nagar, Sidedahalli, Nagasandra Post,<br/>Bengaluru – 560073, Karnataka</font>', ParagraphStyle('Address', parent=styles['Normal'], fontSize=13, fontName='Helvetica', textColor=colors.HexColor('#6B7280'), alignment=TA_CENTER, leading=16)),
        Paragraph('<font color="#6B7280">Recognized by Government of Karnataka | Affiliated to Bangalore University</font>', ParagraphStyle('Affiliation', parent=styles['Normal'], fontSize=13, fontName='Helvetica', textColor=colors.HexColor('#6B7280'), alignment=TA_CENTER, leading=16)),
        Paragraph('<b>NAAC Accredited with "B++" Grade</b>', ParagraphStyle('Accreditation', parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold', textColor=colors.HexColor('#111827'), alignment=TA_CENTER, leading=16)),
    ]

    if logo_flowable:
        header_rows = [
            [
                logo_flowable,
                Table([[header_text[0]], [header_text[1]], [header_text[2]], [header_text[3]], [header_text[4]]], colWidths=[180 * mm], style=[
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]),
            ]
        ]
        header_cols = [30 * mm, 220 * mm]
        header_table_style = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]
    else:
        header_rows = [
            [
                Table([[header_text[0]], [header_text[1]], [header_text[2]], [header_text[3]], [header_text[4]]], colWidths=[250 * mm], style=[
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]),
            ]
        ]
        header_cols = [250 * mm]
        header_table_style = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]

    header_table = Table(header_rows, colWidths=header_cols)
    header_table.setStyle(TableStyle(header_table_style))
    story.append(header_table)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph('<b>RESULT ANALYSIS REPORT</b>', title_style))
    story.append(Paragraph('Academic Performance & Examination Analytics', subtitle_style))
    story.append(Spacer(1, 4 * mm))

    program = data.get('program', '')
    semester = data.get('semester', '')
    academic_year = data.get('academic_year') or data.get('year') or ''
    exam = data.get('exam') or data.get('exam_month') or ''
    result_date = data.get('result_date') or data.get('print_date') or ''

    info_table = Table([
        [
            Paragraph('<b>Program</b>', info_label_style),
            Paragraph('<b>Semester</b>', info_label_style),
            Paragraph('<b>Academic Year</b>', info_label_style),
            Paragraph('<b>Examination</b>', info_label_style),
            Paragraph('<b>Result Date</b>', info_label_style),
        ],
        [
            Paragraph(str(program), info_value_style),
            Paragraph(str(semester), info_value_style),
            Paragraph(str(academic_year), info_value_style),
            Paragraph(str(exam), info_value_style),
            Paragraph(str(result_date), info_value_style),
        ],
    ], colWidths=[40 * mm, 40 * mm, 45 * mm, 45 * mm, 40 * mm])

    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#111827')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#D1D5DB')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph('I. Overall Summary', section_style))
    summary = data.get('overall_summary', {})
    overall_header = [
        'Category',
        'Appeared',
        'Distinction',
        Paragraph('First<br/>Class', cell_style),
        Paragraph('Second<br/>Class', cell_style),
        Paragraph('Pass<br/>Class', cell_style),
        'Passed',
        'Failed',
        'Pass %',
    ]
    category_keys = ['boys', 'girls', 'total']
    overall_data = [overall_header]
    for label, key in zip(['Boys', 'Girls', 'Total'], category_keys):
        row = summary.get(key, {}) if isinstance(summary, dict) else {}
        overall_data.append([
            label,
            str(row.get('appeared', '')),
            str(row.get('distinction', '')),
            str(row.get('first_class', '')),
            str(row.get('second_class', '')),
            str(row.get('pass_class', '')),
            str(row.get('passed', '')),
            str(row.get('failed', '')),
            str(row.get('pass_percentage', '')),
        ])

    overall_table = Table(overall_data, colWidths=[34 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 28 * mm])
    overall_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), body_font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    story.append(overall_table)
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph('II. Top Performers', section_style))
    top_performers = data.get('top_performers', [])[:3]
    performer_data = [['Rank', 'Name', 'Registration No.', 'Marks', '%']]
    for idx, perf in enumerate(top_performers, start=1):
        performer_data.append([
            str(perf.get('rank', idx)),
            Paragraph(str(perf.get('name', '')), cell_left_style),
            str(perf.get('usn', perf.get('registration_no', ''))),
            str(perf.get('marks', perf.get('marks_obtained', perf.get('marks', '')))),
            str(perf.get('percentage', '')),
        ])

    performer_table = Table(performer_data, colWidths=[18 * mm, 80 * mm, 40 * mm, 30 * mm, 30 * mm], repeatRows=1)
    performer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), body_font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
    ]))
    story.append(performer_table)
    story.append(PageBreak())

    story.append(Paragraph('III. Subject-wise Analysis\n(Including Languages)', section_style))
    subject_summary = data.get('subject_summary', [])
    subject_data = [[
        'S.No',
        'Sub Code',
        'Subject Name',
        'Section',
        'Faculty Name',
        'Passed',
        'Failed',
        'Absent',
        'Centum',
        'Pass %',
        Paragraph('Topper<br/>Marks', cell_style),
    ]]
    for idx, subject in enumerate(subject_summary, start=1):
        subject_code = subject.get('code') or subject.get('subject_code') or subject.get('subject') or ''
        subject_name = (
            subject.get('name')
            or subject.get('subject_name')
            or subject.get('subject')
            or subject.get('subject_full_name')
            or ''
        )
        if not subject_name and subject_code:
            hyphen_match = re.match(r"^([A-Z0-9]+)\s*[-–—]\s*(.+)$", subject_code)
            if hyphen_match:
                subject_code = hyphen_match.group(1).strip()
                subject_name = hyphen_match.group(2).strip()
            elif ' ' in subject_code:
                subject_name = subject_code
                subject_code = ''

        faculty_name = (
            subject.get('faculty_name')
            or subject.get('faculty')
            or subject.get('faculty_initial')
            or ''
        )
        subject_data.append([
            str(idx),
            subject_code,
            Paragraph(str(subject_name), cell_left_style),
            subject.get('section', ''),
            Paragraph(str(faculty_name), cell_left_style),
            str(subject.get('passed', '')),
            str(subject.get('failed', '')),
            str(subject.get('absent', '')),
            str(subject.get('centum', '')),
            str(subject.get('pass_percentage', '')),
            str(subject.get('topper_marks', subject.get('topper_percentage', ''))),
        ])

    subject_table = Table(subject_data, colWidths=[10 * mm, 22 * mm, 70 * mm, 18 * mm, 32 * mm, 16 * mm, 16 * mm, 16 * mm, 16 * mm, 16 * mm, 20 * mm], repeatRows=1)
    subject_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), body_font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (4, 1), (4, -1), 'LEFT'),
    ]))
    story.append(subject_table)
    story.append(PageBreak())

    story.append(Paragraph('IV. Performance Analysis\nby Demographics', section_style))
    demographics = data.get('demographics', {})
    appeared_rows = demographics.get('appeared', {}).get('rows', {})
    passed_rows = demographics.get('passed', {}).get('rows', {})
    passed_60_rows = demographics.get('passed_60', {}).get('rows', {})

    label_style = ParagraphStyle(
        'DemoLabel',
        parent=styles['Normal'],
        fontSize=9,
        leading=8,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
    )

    demo_headers = [
        'S. NO', 'Discipline', 'Category',
        'General', '', '',
        'EWS', '', '',
        'SC', '', '',
        'ST', '', '',
        'OBC', '', '',
        'TOTAL', '', '',
    ]
    demo_headers2 = [
        '', '', '',
        'M', 'F', 'TG',
        'M', 'F', 'TG',
        'M', 'F', 'TG',
        'M', 'F', 'TG',
        'M', 'F', 'TG',
        'M', 'F', 'TG',
    ]

    discipline = extract_program_code(data.get('program', ''))
    demo_data = [demo_headers, demo_headers2]
    label_rows = []
    row_keys = ['Total', 'PWD', 'MM', 'OM']
    for label, rows in [('Total Number of Students Appeared', appeared_rows),
                        ('Total Number of Students Passed/Awarded Degree', passed_rows),
                        ('Out of Total, Number of Students Passed with 60% or above', passed_60_rows)]:
        label_rows.append(len(demo_data))
        demo_data.append([Paragraph(f'<b>{label}</b>', label_style)] + [''] * 20)
        for idx, row_key in enumerate(row_keys, start=1):
            row = rows.get(row_key, {})
            demo_data.append([
                str(idx),
                discipline,
                row_key,
                str(row.get('General', {}).get('M', 0)),
                str(row.get('General', {}).get('F', 0)),
                str(row.get('General', {}).get('TG', 0)),
                str(row.get('EWS', {}).get('M', 0)),
                str(row.get('EWS', {}).get('F', 0)),
                str(row.get('EWS', {}).get('TG', 0)),
                str(row.get('SC', {}).get('M', 0)),
                str(row.get('SC', {}).get('F', 0)),
                str(row.get('SC', {}).get('TG', 0)),
                str(row.get('ST', {}).get('M', 0)),
                str(row.get('ST', {}).get('F', 0)),
                str(row.get('ST', {}).get('TG', 0)),
                str(row.get('OBC', {}).get('M', 0)),
                str(row.get('OBC', {}).get('F', 0)),
                str(row.get('OBC', {}).get('TG', 0)),
                str(row.get('TOTAL', {}).get('M', 0)),
                str(row.get('TOTAL', {}).get('F', 0)),
                str(row.get('TOTAL', {}).get('TG', 0)),
            ])

    demo_table = Table(demo_data, colWidths=[18 * mm, 22 * mm, 22 * mm] + [8 * mm] * 18, repeatRows=2)
    demo_style = [
        ('BACKGROUND', (0, 0), (-1, 1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('ROWHEIGHT', (0, 0), (-1, 1), 18 * mm),
        ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), body_font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 1), 4),
        ('TOPPADDING', (0, 0), (-1, 1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 3), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (20, 1), 'CENTER'),
        ('TEXTROTATION', (3, 1), (20, 1), 90),
        ('SPAN', (3, 0), (5, 0)),
        ('SPAN', (6, 0), (8, 0)),
        ('SPAN', (9, 0), (11, 0)),
        ('SPAN', (12, 0), (14, 0)),
        ('SPAN', (15, 0), (17, 0)),
        ('SPAN', (18, 0), (20, 0)),
    ]
    for row_index in label_rows:
        demo_style.extend([
            ('SPAN', (0, row_index), (20, row_index)),
            ('ALIGN', (0, row_index), (20, row_index), 'LEFT'),
            ('VALIGN', (0, row_index), (20, row_index), 'MIDDLE'),
        ])

    demo_table.setStyle(TableStyle(demo_style))
    story.append(demo_table)
    story.append(PageBreak())

    centum_achievers = data.get('centum_achievers', [])
    centum_headers = [
        'Sl. No', 'Name', 'Registration No.', 'Sub Code', 'Subject Name', 'Marks', Paragraph('Max<br/>Marks', cell_style), '%'
    ]
    centum_col_widths = [14 * mm, 46 * mm, 30 * mm, 28 * mm, 55 * mm, 16 * mm, 16 * mm, 16 * mm]

    def add_centum_page(rows, page_title=True):
        if page_title:
            story.append(Paragraph('V. Subject-wise Centum\nAchievers', section_style))
        centum_data = [centum_headers]
        for idx, achiever in rows:
            centum_data.append([
                str(idx),
                Paragraph(str(achiever.get('name', '')), cell_left_style),
                str(achiever.get('usn', achiever.get('registration_no', ''))),
                achiever.get('subject_code', ''),
                Paragraph(str(achiever.get('subject_name', '')), cell_left_style),
                str(achiever.get('marks', '')),
                str(achiever.get('max_marks', '')),
                str(achiever.get('percentage', '')),
            ])

        centum_table = Table(centum_data, colWidths=centum_col_widths, repeatRows=1)
        centum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), body_font_size),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
        ]))
        story.append(centum_table)

    page_rows = [(idx, achiever) for idx, achiever in enumerate(centum_achievers, start=1)]
    for start in range(0, len(page_rows), 15):
        chunk = page_rows[start:start + 15]
        add_centum_page(chunk, page_title=(start == 0))
        if start + 15 < len(page_rows):
            story.append(PageBreak())

    story.append(Spacer(1, 8 * mm))

    sig_titles = [
        'Head of Department',
        'Controller of Examination',
        'Principal',
    ]
    sig_data = [
        ['', '', ''],
        sig_titles,
    ]
    sig_table = Table(sig_data, colWidths=[70 * mm, 70 * mm, 70 * mm], rowHeights=[15 * mm, 12 * mm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)

    doc.build(story)
    print(f'✅ PDF generated: {output_path}')


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/d/projects/SIMS-Result-analysis')

    sample_data = {
        'program': 'BCA',
        'semester': 'II Semester',
        'overall_summary': {
            'boys': {'appeared': 75, 'distinction': 10, 'first_class': 25, 'second_class': 20, 'pass_class': 10, 'passed': 65, 'failed': 10, 'pass_percentage': 86.7},
            'girls': {'appeared': 70, 'distinction': 8, 'first_class': 22, 'second_class': 18, 'pass_class': 12, 'passed': 60, 'failed': 10, 'pass_percentage': 85.7},
            'total': {'appeared': 145, 'distinction': 18, 'first_class': 47, 'second_class': 38, 'pass_class': 22, 'passed': 125, 'failed': 20, 'pass_percentage': 86.2},
        },
        'top_performers': [
            {'rank': 1, 'name': 'Student A', 'usn': 'USN001', 'marks': 98, 'percentage': 98.0},
            {'rank': 2, 'name': 'Student B', 'usn': 'USN002', 'marks': 96, 'percentage': 96.0},
            {'rank': 3, 'name': 'Student C', 'usn': 'USN003', 'marks': 95, 'percentage': 95.0},
        ],
        'subject_summary': [
            {'code': 'BCA23P', 'name': 'LINUX AND SHELL PROGRAMMING LAB', 'section': '', 'faculty_name': '', 'passed': 50, 'failed': 0, 'absent': 0, 'centum': 8, 'pass_percentage': 100, 'topper_marks': 100},
        ],
        'centum_achievers': [
            {'name': 'Harika S', 'usn': 'U03FC24S0064', 'subject_code': 'BCA23P', 'subject_name': 'LINUX AND SHELL PROGRAMMING LAB', 'marks': 50, 'max_marks': 50, 'percentage': 100},
        ],
        'demographics': {
            'appeared': {'rows': {'Total': {'General': {'M': 66, 'F': 64, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 9, 'F': 5, 'TG': 0}, 'ST': {'M': 1, 'F': 1, 'TG': 0}, 'OBC': {'M': 39, 'F': 48, 'TG': 0}, 'TOTAL': {'M': 66, 'F': 64, 'TG': 0}}, 'PWD': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'MM': {'General': {'M': 3, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 1, 'F': 3, 'TG': 0}, 'TOTAL': {'M': 4, 'F': 3, 'TG': 0}}, 'OM': {'General': {'M': 1, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 1, 'TG': 0}, 'TOTAL': {'M': 1, 'F': 1, 'TG': 0}}}},
            'passed': {'rows': {'Total': {'General': {'M': 5, 'F': 8, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 2, 'F': 3, 'TG': 0}, 'ST': {'M': 0, 'F': 1, 'TG': 0}, 'OBC': {'M': 14, 'F': 34, 'TG': 0}, 'TOTAL': {'M': 21, 'F': 46, 'TG': 0}}, 'PWD': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'MM': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'OM': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 1, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 1, 'F': 0, 'TG': 0}}}},
            'passed_60': {'rows': {'Total': {'General': {'M': 5, 'F': 7, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 2, 'F': 2, 'TG': 0}, 'ST': {'M': 0, 'F': 1, 'TG': 0}, 'OBC': {'M': 11, 'F': 33, 'TG': 0}, 'TOTAL': {'M': 18, 'F': 43, 'TG': 0}}, 'PWD': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'MM': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'OM': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 1, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 1, 'F': 0, 'TG': 0}}}},
        },
    }

    create_pdf_report(sample_data, 'test_report.pdf')
