#!/usr/bin/env python3
"""
Generate test data (Excel and PDF) for testing the ResultIQ application.
Creates matching student records in both files.
"""
import os
import sys
from openpyxl import Workbook
from pathlib import Path

def create_test_excel():
    """Create a test Excel file with student master data."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    # Headers
    headers = ["USN", "StudentName", "Gender", "Category", "Caste", "Religion"]
    ws.append(headers)

    # Test data - 10 students
    students = [
        ("1SI21CS001", "Arjun Kumar", "Male", "GM", "General", "Hindu"),
        ("1SI21CS002", "Priya Singh", "Female", "SC", "SC", "Hindu"),
        ("1SI21CS003", "Rahul Patel", "Male", "GM", "General", "Hindu"),
        ("1SI21CS004", "Ananya Verma", "Female", "ST", "ST", "Christian"),
        ("1SI21CS005", "Vishal Sharma", "Male", "OBC", "OBC", "Hindu"),
        ("1SI21CS006", "Sakshi Desai", "Female", "GM", "General", "Hindu"),
        ("1SI21CS007", "Nikhil Gupta", "Male", "GM", "General", "Jain"),
        ("1SI21CS008", "Divya Nair", "Female", "OBC", "OBC", "Christian"),
        ("1SI21CS009", "Aditya Malhotra", "Male", "SC", "SC", "Sikh"),
        ("1SI21CS010", "Neha Reddy", "Female", "GM", "General", "Hindu"),
    ]

    for student in students:
        ws.append(student)

    # Adjust column widths
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12

    wb.save("test_student_master.xlsx")
    print("✓ Created test_student_master.xlsx")


def create_test_pdf():
    """Create a test PDF with result ledger data using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        pdf_path = "test_result_ledger.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=1
        )
        story.append(Paragraph("BANGALORE UNIVERSITY<br/>B.Sc Computer Science - Semester 4<br/>Examination Result Ledger", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Result table data
        table_data = [
            ["USN", "Name", "Sub1-Code", "Sub1-Marks", "Sub2-Code", "Sub2-Marks", "Sub3-Code", "Sub3-Marks", "SGPA", "Result"],
            ["1SI21CS001", "Arjun Kumar", "CS21", "75", "CS22", "82", "CS23", "88", "8.2", "PASS"],
            ["1SI21CS002", "Priya Singh", "CS21", "92", "CS22", "78", "CS23", "85", "8.5", "PASS"],
            ["1SI21CS003", "Rahul Patel", "CS21", "68", "CS22", "72", "CS23", "65", "6.8", "PASS"],
            ["1SI21CS004", "Ananya Verma", "CS21", "88", "CS22", "90", "CS23", "92", "9.0", "PASS"],
            ["1SI21CS005", "Vishal Sharma", "CS21", "55", "CS22", "60", "CS23", "58", "5.8", "PASS"],
            ["1SI21CS006", "Sakshi Desai", "CS21", "95", "CS22", "93", "CS23", "96", "9.5", "PASS"],
            ["1SI21CS007", "Nikhil Gupta", "CS21", "70", "CS22", "75", "CS23", "78", "7.4", "PASS"],
            ["1SI21CS008", "Divya Nair", "CS21", "82", "CS22", "85", "CS23", "80", "8.2", "PASS"],
            ["1SI21CS009", "Aditya Malhotra", "CS21", "45", "CS22", "48", "CS23", "50", "4.8", "FAIL"],
            ["1SI21CS010", "Neha Reddy", "CS21", "78", "CS22", "81", "CS23", "84", "8.1", "PASS"],
        ]

        # Create table
        table = Table(table_data, colWidths=[1.0*inch, 1.3*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.9*inch, 0.7*inch, 0.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        # Summary
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        story.append(Paragraph("<b>Summary:</b>", summary_style))
        story.append(Paragraph(f"Total Students: 10 | Passed: 9 | Failed: 1 | Pass %: 90%", summary_style))

        doc.build(story)
        print("✓ Created test_result_ledger.pdf")
    except Exception as e:
        print(f"⚠ Could not create PDF with reportlab: {e}")
        print("  Using pdf_generator module instead...")
        create_pdf_with_pdf_generator()


def create_pdf_with_pdf_generator():
    """Create a simple PDF using fpdf2."""
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "BANGALORE UNIVERSITY", 0, 1, "C")
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, "B.Sc Computer Science - Semester 4", 0, 1, "C")
        pdf.cell(0, 10, "Examination Result Ledger", 0, 1, "C")
        pdf.ln(5)

        # Simple table
        pdf.set_font("Arial", "B", 9)
        col_width = 19
        row_height = 7

        headers = ["USN", "Name", "S1", "M1", "S2", "M2", "S3", "M3", "SGPA", "Result"]
        for header in headers:
            pdf.cell(col_width, row_height, header, 1, 0, "C")
        pdf.ln()

        pdf.set_font("Arial", "", 8)
        students = [
            ["1SI21CS001", "Arjun Kumar", "CS21", "75", "CS22", "82", "CS23", "88", "8.2", "PASS"],
            ["1SI21CS002", "Priya Singh", "CS21", "92", "CS22", "78", "CS23", "85", "8.5", "PASS"],
            ["1SI21CS003", "Rahul Patel", "CS21", "68", "CS22", "72", "CS23", "65", "6.8", "PASS"],
            ["1SI21CS004", "Ananya Verma", "CS21", "88", "CS22", "90", "CS23", "92", "9.0", "PASS"],
            ["1SI21CS005", "Vishal Sharma", "CS21", "55", "CS22", "60", "CS23", "58", "5.8", "PASS"],
            ["1SI21CS006", "Sakshi Desai", "CS21", "95", "CS22", "93", "CS23", "96", "9.5", "PASS"],
            ["1SI21CS007", "Nikhil Gupta", "CS21", "70", "CS22", "75", "CS23", "78", "7.4", "PASS"],
            ["1SI21CS008", "Divya Nair", "CS21", "82", "CS22", "85", "CS23", "80", "8.2", "PASS"],
            ["1SI21CS009", "Aditya Malhotra", "CS21", "45", "CS22", "48", "CS23", "50", "4.8", "FAIL"],
            ["1SI21CS010", "Neha Reddy", "CS21", "78", "CS22", "81", "CS23", "84", "8.1", "PASS"],
        ]

        for student in students:
            for cell in student:
                pdf.cell(col_width, row_height, str(cell), 1, 0, "C")
            pdf.ln()

        pdf.output("test_result_ledger.pdf")
        print("✓ Created test_result_ledger.pdf")
    except Exception as e:
        print(f"✗ Error creating PDF: {e}")


if __name__ == "__main__":
    print("\n📊 Generating Test Data for ResultIQ...\n")
    create_test_excel()
    create_test_pdf()
    print("\n✅ Test data created successfully!")
    print("\n📝 How to use:")
    print("   1. In the browser, upload 'test_student_master.xlsx' as the Excel file")
    print("   2. Upload 'test_result_ledger.pdf' as the PDF file")
    print("   3. Click 'Validate Excel' and 'Validate PDF'")
    print("   4. Click 'Show Analysis Preview' to see the analysis")
    print()
