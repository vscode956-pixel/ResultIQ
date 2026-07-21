import os
import sys
import tempfile
import io
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import base64
import shutil
from pathlib import Path
from typing import Optional
from flask import Flask, jsonify, request, send_file, render_template
from PIL import Image


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from excel_parser import parse_students
from pdf_parser import parse_pdf
from category_mapping import map_category, is_pwd, is_mm, is_om
from demographics import compute_demographics_rows, validate_demographics
from pdf_generator import create_pdf_report
from report.word_renderer import WordReportRenderer
from report.report_data_builder import build_report_data

def summarize_messages(messages):
    summary = {}
    for message in messages or []:
        summary[message] = summary.get(message, 0) + 1
    return [
        {"message": message, "count": count}
        for message, count in summary.items()
    ]


def normalize_usn(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text if text else None


def build_gender_key(value: Optional[str]) -> str:
    if not value:
        return 'total'
    normalized = str(value).strip().lower()
    if normalized.startswith('f') or normalized.startswith('g') or 'female' in normalized or 'girl' in normalized:
        return 'girls'
    return 'boys'


def classify_student(total_marks: Optional[int], max_marks: Optional[int], overall_result: Optional[str]) -> str:
    if overall_result and isinstance(overall_result, str) and overall_result.strip().upper() in {'FAIL', 'FAILED', 'RETEST'}:
        return 'failed'
    if total_marks is None or max_marks is None or max_marks == 0:
        return 'unknown'
    percentage = (total_marks / max_marks) * 100
    rounded_percentage = round(percentage)
    if rounded_percentage >= 85:
        return 'distinction'
    if rounded_percentage >= 60:
        return 'first_class'
    if rounded_percentage >= 50:
        return 'second_class'
    if rounded_percentage >= 40:
        return 'pass_class'
    return 'failed'


def create_ranked_performers(students):
    sorted_students = sorted(
        [student for student in students if student.get('total_marks') is not None],
        key=lambda item: item.get('total_marks'),
        reverse=True,
    )
    rank = 0
    last_marks = None
    seen = 0
    for student in sorted_students:
        seen += 1
        marks = student.get('total_marks')
        if marks != last_marks:
            rank = seen
            last_marks = marks
        student['rank'] = rank
    return sorted_students


def summarize_subjects(merged_students):
    subject_summary = {}
    for student in merged_students:
        for subject in student.get('subjects', []):
            code = subject.get('subject_code') or 'UNKNOWN'
            entry = subject_summary.setdefault(code, {
                'code': code,
                'name': subject.get('subject_name'),
                'passed': 0,
                'failed': 0,
                'absent': 0,
                'centum': 0,
                'topper_marks': 0,
            })
            if not entry.get('name') and subject.get('subject_name'):
                entry['name'] = subject.get('subject_name')

            result = (subject.get('result') or '').strip().upper()
            marks = subject.get('total_marks')
            max_marks = subject.get('max_marks')
            is_absent = result in {'AB', 'ABSENT'} or marks is None
            is_failed = result in {'FAIL', 'FAILED', 'RETEST'}

            if is_absent:
                entry['absent'] += 1
            elif is_failed:
                entry['failed'] += 1
            else:
                entry['passed'] += 1

            if marks is not None and max_marks is not None and marks == max_marks:
                entry['centum'] += 1

            if marks is not None and marks > entry['topper_marks']:
                entry['topper_marks'] = marks

    for entry in subject_summary.values():
        total_attempted = entry['passed'] + entry['failed']
        entry['pass_percentage'] = round((entry['passed'] / total_attempted) * 100) if total_attempted else 0

    return sorted(subject_summary.values(), key=lambda x: (x['name'] or x['code']))


def compute_centum_achievers(merged_students):
    centum_achievers = []
    for student in merged_students:
        for subject in student.get('subjects', []):
            marks = subject.get('total_marks')
            max_marks = subject.get('max_marks')
            if marks is None or max_marks is None:
                continue
            if marks == max_marks:
                centum_achievers.append({
                    'usn': student.get('usn'),
                    'name': student.get('name'),
                    'subject_code': subject.get('subject_code') or 'UNKNOWN',
                    'subject_name': subject.get('subject_name') or 'Unknown Subject',
                    'marks': marks,
                    'max_marks': max_marks,
                    'percentage': round((marks / max_marks) * 100, 2) if max_marks else None,
                })
    return centum_achievers


app = Flask(__name__, template_folder='templates')


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/validate/excel', methods=['POST'])
def validate_excel():
    file = request.files.get('excel')
    if not file or not file.filename:
        return jsonify({'valid': False, 'errors': ['No Excel file provided.'], 'warnings': []}), 400

    suffix = Path(file.filename).suffix.lower()
    if suffix not in {'.xlsx', '.xlsm'}:
        return jsonify({'valid': False, 'errors': ['Invalid file format.'], 'warnings': []}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        parsed = parse_students(temp_path)
        errors = [parsed.get('message')] if parsed.get('error', False) else []
        warnings = parsed.get('warnings', []) or []
        valid = not parsed.get('error', False)
        status = 'passed'
        if not valid:
            status = 'failed'
        elif warnings:
            status = 'passed_with_warnings'

        result = {
            'valid': valid,
            'message': 'Excel validation completed.' if valid else parsed.get('message', 'Excel validation failed.'),
            'errors': errors,
            'warnings': warnings,
            'students': len(parsed.get('rows', [])),
            'validation': {
                'status': status,
                'students': len(parsed.get('rows', [])),
                'warnings': len(warnings),
                'errors': len(errors),
                'warning_summary': summarize_messages(warnings),
                'error_summary': summarize_messages(errors),
            },
        }
        return jsonify(result)
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


@app.route('/api/validate/pdf', methods=['POST'])
def validate_pdf():
    file = request.files.get('pdf')
    if not file or not file.filename:
        return jsonify({'valid': False, 'errors': ['No PDF file provided.'], 'warnings': []}), 400

    suffix = Path(file.filename).suffix.lower()
    if suffix != '.pdf':
        return jsonify({'valid': False, 'errors': ['Invalid PDF file format.'], 'warnings': []}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        parsed = parse_pdf(temp_path)
        errors = parsed.errors or []
        warnings = parsed.warnings or []
        valid = not errors
        status = 'passed'
        if not valid:
            status = 'failed'
        elif warnings:
            status = 'passed_with_warnings'

        result = {
            'valid': valid,
            'message': 'PDF validation completed.' if valid else 'PDF validation failed.',
            'errors': errors,
            'warnings': warnings,
            'students': len(parsed.students),
            'subjects': len(parsed.subject_master),
            'validation': {
                'status': status,
                'students': len(parsed.students),
                'subjects': len(parsed.subject_master),
                'warnings': len(warnings),
                'errors': len(errors),
                'warning_summary': summarize_messages(warnings),
                'error_summary': summarize_messages(errors),
            },
        }
        return jsonify(result)
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


@app.route('/api/analyze', methods=['POST'])
def analyze():
    excel_file = request.files.get('excel')
    pdf_file = request.files.get('pdf')

    if not excel_file or not excel_file.filename:
        return jsonify({'error': 'No Excel file provided.'}), 400
    if not pdf_file or not pdf_file.filename:
        return jsonify({'error': 'No PDF file provided.'}), 400

    excel_suffix = Path(excel_file.filename).suffix.lower()
    pdf_suffix = Path(pdf_file.filename).suffix.lower()
    if excel_suffix not in {'.xlsx', '.xlsm'}:
        return jsonify({'error': 'Invalid Excel file format.'}), 400
    if pdf_suffix != '.pdf':
        return jsonify({'error': 'Invalid PDF file format.'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=excel_suffix) as excel_temp, tempfile.NamedTemporaryFile(delete=False, suffix=pdf_suffix) as pdf_temp:
        excel_file.save(excel_temp.name)
        pdf_file.save(pdf_temp.name)
        excel_path = excel_temp.name
        pdf_path = pdf_temp.name

    try:
        excel_parsed = parse_students(excel_path)
        if excel_parsed.get('error', False):
            return jsonify({'error': excel_parsed.get('message', 'Excel parse failed.')}), 400

        pdf_parsed = parse_pdf(pdf_path)
        if pdf_parsed.errors:
            return jsonify({'error': 'PDF parse failed.', 'details': pdf_parsed.errors}), 400

        excel_rows = excel_parsed.get('rows', [])
        pdf_students = pdf_parsed.students
        pdf_by_usn = {
            normalize_usn(student.usn): student
            for student in pdf_students
            if normalize_usn(student.usn)
        }

        merged = []
        for row in excel_rows:
            usn = normalize_usn(row.get('USN'))
            if not usn:
                continue
            pdf_student = pdf_by_usn.get(usn)
            if not pdf_student:
                continue
            total_marks = None
            max_marks = None
            if pdf_student.totals and pdf_student.totals.total_marks is not None:
                total_marks = pdf_student.totals.total_marks
            else:
                total_marks = sum((subject.total_marks or 0) for subject in pdf_student.subjects) or None
            if pdf_student.totals and pdf_student.totals.max_marks is not None:
                max_marks = pdf_student.totals.max_marks
            else:
                max_marks = sum((subject.max_marks or 0) for subject in pdf_student.subjects) or None

            percentage = None
            if total_marks is not None and max_marks:
                percentage = round((total_marks / max_marks) * 100, 2)

            category = classify_student(total_marks, max_marks, pdf_student.overall_result)
            merged.append({
                'usn': usn,
                'name': row.get('StudentName') or pdf_student.student_name,
                'gender': row.get('Gender'),
                'category': row.get('Category'),
                'caste': row.get('Caste'),
                'religion': row.get('Religion'),
                'overall_result': pdf_student.overall_result,
                'total_marks': total_marks,
                'max_marks': max_marks,
                'percentage': percentage,
                'classification': category,
                'subjects': [subject.to_dict() for subject in pdf_student.subjects],
            })

        if not merged:
            return jsonify({'error': 'No merged student records found between Excel and PDF.'}), 400

        summary = {
            'boys': {'appeared': 0, 'passed': 0, 'failed': 0, 'distinction': 0, 'first_class': 0, 'second_class': 0, 'pass_class': 0, 'pass_percentage': 0},
            'girls': {'appeared': 0, 'passed': 0, 'failed': 0, 'distinction': 0, 'first_class': 0, 'second_class': 0, 'pass_class': 0, 'pass_percentage': 0},
            'total': {'appeared': 0, 'passed': 0, 'failed': 0, 'distinction': 0, 'first_class': 0, 'second_class': 0, 'pass_class': 0, 'pass_percentage': 0},
        }
        classification_details = {
            'distinction': [],
            'first_class': [],
            'second_class': [],
            'pass_class': [],
            'failed': [],
        }

        for student in merged:
            gender_key = build_gender_key(student.get('gender'))
            category = classify_student(student.get('total_marks'), student.get('max_marks'), student.get('overall_result'))
            detail = {
                'usn': student['usn'],
                'name': student['name'],
                'marks': student['total_marks'],
                'percentage': student['percentage'],
            }
            if category in classification_details:
                classification_details[category].append(detail)
            for group in (gender_key, 'total'):
                summary[group]['appeared'] += 1
                if category == 'failed':
                    summary[group]['failed'] += 1
                elif category == 'distinction':
                    summary[group]['passed'] += 1
                    summary[group]['distinction'] += 1
                elif category == 'first_class':
                    summary[group]['passed'] += 1
                    summary[group]['first_class'] += 1
                elif category == 'second_class':
                    summary[group]['passed'] += 1
                    summary[group]['second_class'] += 1
                elif category == 'pass_class':
                    summary[group]['passed'] += 1
                    summary[group]['pass_class'] += 1
                else:
                    summary[group]['failed'] += 1

        for group in summary:
            appeared = summary[group]['appeared']
            passed = summary[group]['passed']
            summary[group]['pass_percentage'] = round((passed / appeared) * 100) if appeared else 0

        subject_summary = summarize_subjects(merged)
        centum_achievers = compute_centum_achievers(merged)
        ranked = create_ranked_performers(merged)
        top = [student for student in ranked if student.get('rank') <= 3]

        demographics_appeared = compute_demographics_rows(merged)

        passed_students = [s for s in merged if s.get('classification') != 'failed']
        demographics_passed = compute_demographics_rows(passed_students)

        passed_60_students = [s for s in passed_students if (s.get('percentage') or 0) >= 60]
        demographics_passed_60 = compute_demographics_rows(passed_60_students)

        demographics_validation = validate_demographics(demographics_appeared, demographics_passed, demographics_passed_60)

        rank_labels = {1: '🥇', 2: '🥈', 3: '🥉'}
        top_performers = [
            {
                'rank': student['rank'],
                'label': rank_labels.get(student['rank'], str(student['rank'])),
                'name': student['name'],
                'usn': student['usn'],
                'marks': student['total_marks'],
                'percentage': student['percentage'],
            }
            for student in top
        ]

        return jsonify({
            'program': pdf_parsed.metadata.program,
            'semester': pdf_parsed.metadata.semester,
            'overall_summary': summary,
            'top_performers': top_performers,
            'classification_details': classification_details,
            'subject_summary': subject_summary,
            'centum_achievers': centum_achievers,
            'demographics': {
                'appeared': demographics_appeared,
                'passed': demographics_passed,
                'passed_60': demographics_passed_60,
                'validation': demographics_validation,
            },
            'students': len(merged),
            'subjects': len(pdf_parsed.subject_master),
        })
    finally:
        for path in (excel_path, pdf_path):
            try:
                os.remove(path)
            except OSError:
                pass


def qname(namespace, tag):
    return f'{{{namespace}}}{tag}'

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
R_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC_NS = 'http://schemas.openxmlformats.org/drawingml/2006/picture'

ET.register_namespace('w', W_NS)
ET.register_namespace('r', R_NS)
ET.register_namespace('wp', WP_NS)
ET.register_namespace('a', A_NS)
ET.register_namespace('pic', PIC_NS)


def make_paragraph(text, bold=False):
    p = ET.Element(qname(W_NS, 'p'))
    r = ET.SubElement(p, qname(W_NS, 'r'))
    rPr = ET.SubElement(r, qname(W_NS, 'rPr'))
    if bold:
        ET.SubElement(rPr, qname(W_NS, 'b'))
    t = ET.SubElement(r, qname(W_NS, 't'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = str(text)
    return p


def make_cell(text, header=False):
    tc = ET.Element(qname(W_NS, 'tc'))
    tcPr = ET.SubElement(tc, qname(W_NS, 'tcPr'))
    ET.SubElement(tcPr, qname(W_NS, 'tcW'), {qname(W_NS, 'w'): '2400'})
    if header:
        ET.SubElement(tcPr, qname(W_NS, 'shd'), {
            qname(W_NS, 'val'): 'clear',
            qname(W_NS, 'color'): 'auto',
            qname(W_NS, 'fill'): 'D9D9D9',
        })
    p = ET.Element(qname(W_NS, 'p'))
    pPr = ET.SubElement(p, qname(W_NS, 'pPr'))
    ET.SubElement(pPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): 'center'})
    r = ET.SubElement(p, qname(W_NS, 'r'))
    rPr = ET.SubElement(r, qname(W_NS, 'rPr'))
    if header:
        ET.SubElement(rPr, qname(W_NS, 'b'))
    t = ET.SubElement(r, qname(W_NS, 't'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = str(text)
    tc.append(p)
    return tc


def make_cell_paragraphs(paragraphs, header=False, width='2400'):
    tc = ET.Element(qname(W_NS, 'tc'))
    tcPr = ET.SubElement(tc, qname(W_NS, 'tcPr'))
    ET.SubElement(tcPr, qname(W_NS, 'tcW'), {qname(W_NS, 'w'): width})
    if header:
        ET.SubElement(tcPr, qname(W_NS, 'shd'), {
            qname(W_NS, 'val'): 'clear',
            qname(W_NS, 'color'): 'auto',
            qname(W_NS, 'fill'): 'D9D9D9',
        })
    for p in paragraphs:
        tc.append(p)
    return tc


def make_table(headers, rows):
    tbl = ET.Element(qname(W_NS, 'tbl'))
    tblPr = ET.SubElement(tbl, qname(W_NS, 'tblPr'))
    ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): '0', qname(W_NS, 'type'): 'auto'})
    ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})
    tblBorders = ET.SubElement(tblPr, qname(W_NS, 'tblBorders'))
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        ET.SubElement(tblBorders, qname(W_NS, border_name), {
            qname(W_NS, 'val'): 'single',
            qname(W_NS, 'sz'): '4',
            qname(W_NS, 'space'): '0',
            qname(W_NS, 'color'): '000000',
        })
    tblGrid = ET.SubElement(tbl, qname(W_NS, 'tblGrid'))
    for _ in headers:
        ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): '2400'})
    tr = ET.SubElement(tbl, qname(W_NS, 'tr'))
    for value in headers:
        tr.append(make_cell(value, header=True))
    for row_values in rows:
        tr = ET.SubElement(tbl, qname(W_NS, 'tr'))
        for value in row_values:
            tr.append(make_cell(value))
    return tbl


def make_inline_image_run(rId, cx, cy):
    run = ET.Element(qname(W_NS, 'r'))
    drawing = ET.SubElement(run, qname(W_NS, 'drawing'))
    inline = ET.SubElement(drawing, qname(WP_NS, 'inline'), {
        'distT': '0',
        'distB': '0',
        'distL': '0',
        'distR': '0',
    })
    ET.SubElement(inline, qname(WP_NS, 'extent'), {'cx': str(cx), 'cy': str(cy)})
    ET.SubElement(inline, qname(WP_NS, 'effectExtent'), {
        'l': '0',
        't': '0',
        'r': '0',
        'b': '0',
    })
    ET.SubElement(inline, qname(WP_NS, 'docPr'), {'id': '1', 'name': 'Logo'})
    cNvGraphicFramePr = ET.SubElement(inline, qname(WP_NS, 'cNvGraphicFramePr'))
    ET.SubElement(cNvGraphicFramePr, qname(A_NS, 'graphicFrameLocks'), {qname(A_NS, 'noChangeAspect'): '1'})
    graphic = ET.SubElement(inline, qname(A_NS, 'graphic'))
    graphicData = ET.SubElement(graphic, qname(A_NS, 'graphicData'), {
        'uri': 'http://schemas.openxmlformats.org/drawingml/2006/picture'
    })
    pic = ET.SubElement(graphicData, qname(PIC_NS, 'pic'))
    nvPicPr = ET.SubElement(pic, qname(PIC_NS, 'nvPicPr'))
    ET.SubElement(nvPicPr, qname(PIC_NS, 'cNvPr'), {'id': '0', 'name': 'Logo'})
    ET.SubElement(nvPicPr, qname(PIC_NS, 'cNvPicPr'))
    blipFill = ET.SubElement(pic, qname(PIC_NS, 'blipFill'))
    blip = ET.SubElement(blipFill, qname(A_NS, 'blip'), {qname(R_NS, 'embed'): rId})
    ET.SubElement(blipFill, qname(A_NS, 'stretch')).append(ET.Element(qname(A_NS, 'fillRect')))
    spPr = ET.SubElement(pic, qname(PIC_NS, 'spPr'))
    xfrm = ET.SubElement(spPr, qname(A_NS, 'xfrm'))
    ET.SubElement(xfrm, qname(A_NS, 'off'), {'x': '0', 'y': '0'})
    ET.SubElement(xfrm, qname(A_NS, 'ext'), {'cx': str(cx), 'cy': str(cy)})
    prstGeom = ET.SubElement(spPr, qname(A_NS, 'prstGeom'), {'prst': 'rect'})
    ET.SubElement(prstGeom, qname(A_NS, 'avLst'))
    return run


def make_header_table(data, logo_paragraph=None):
    header_title = make_paragraph('SOUNDARYA INSTITUTE OF MANAGEMENT AND SCIENCE', bold=True)
    header_subtitle = make_paragraph('Department of Computer Science')
    header_program = make_paragraph(f"Program: {data.get('program', '')}")
    header_semester = make_paragraph(f"Semester: {data.get('semester', '')}")
    text_cell = make_cell_paragraphs([header_title, header_subtitle, header_program, header_semester], header=False, width='7200')
    if logo_paragraph is not None:
        logo_cell = make_cell_paragraphs([logo_paragraph], header=False, width='2400')
    else:
        logo_cell = make_cell_paragraphs([make_paragraph('')], header=False, width='2400')
    table = ET.Element(qname(W_NS, 'tbl'))
    tblPr = ET.SubElement(table, qname(W_NS, 'tblPr'))
    ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): '0', qname(W_NS, 'type'): 'auto'})
    ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})
    tblGrid = ET.SubElement(table, qname(W_NS, 'tblGrid'))
    ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): '2400'})
    ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): '7200'})
    tr = ET.SubElement(table, qname(W_NS, 'tr'))
    tr.append(logo_cell)
    tr.append(text_cell)
    return table


def make_signature_table():
    labels = ['Head of Department', 'Controller of Examination', 'Principal']
    tbl = ET.Element(qname(W_NS, 'tbl'))
    tblPr = ET.SubElement(tbl, qname(W_NS, 'tblPr'))
    ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): '0', qname(W_NS, 'type'): 'auto'})
    ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})
    tblBorders = ET.SubElement(tblPr, qname(W_NS, 'tblBorders'))
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        ET.SubElement(tblBorders, qname(W_NS, border_name), {
            qname(W_NS, 'val'): 'single',
            qname(W_NS, 'sz'): '4',
            qname(W_NS, 'space'): '0',
            qname(W_NS, 'color'): '000000',
        })
    tblGrid = ET.SubElement(tbl, qname(W_NS, 'tblGrid'))
    for _ in range(3):
        ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): '4000'})
    header = ET.SubElement(tbl, qname(W_NS, 'tr'))
    for label in ['Signature', '', '']:
        header.append(make_cell(label, header=True))
    label_row = ET.SubElement(tbl, qname(W_NS, 'tr'))
    for label in labels:
        label_row.append(make_cell(label))
    return tbl


def load_logo_data():
    logo_path = ROOT / 'Untitled_design.png'
    if not logo_path.exists():
        return None
    try:
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        return None


def render_report_html(data):
    return render_template(
        'report.html',
        program=data.get('program', ''),
        semester=data.get('semester', ''),
        generated_at=data.get('generated_at', ''),
        overall_rows=[
            ['Boys',
             data.get('overall_summary', {}).get('boys', {}).get('appeared', ''),
             data.get('overall_summary', {}).get('boys', {}).get('distinction', ''),
             data.get('overall_summary', {}).get('boys', {}).get('first_class', ''),
             data.get('overall_summary', {}).get('boys', {}).get('second_class', ''),
             data.get('overall_summary', {}).get('boys', {}).get('pass_class', ''),
             data.get('overall_summary', {}).get('boys', {}).get('passed', ''),
             data.get('overall_summary', {}).get('boys', {}).get('failed', ''),
             data.get('overall_summary', {}).get('boys', {}).get('pass_percentage', ''),
            ],
            ['Girls',
             data.get('overall_summary', {}).get('girls', {}).get('appeared', ''),
             data.get('overall_summary', {}).get('girls', {}).get('distinction', ''),
             data.get('overall_summary', {}).get('girls', {}).get('first_class', ''),
             data.get('overall_summary', {}).get('girls', {}).get('second_class', ''),
             data.get('overall_summary', {}).get('girls', {}).get('pass_class', ''),
             data.get('overall_summary', {}).get('girls', {}).get('passed', ''),
             data.get('overall_summary', {}).get('girls', {}).get('failed', ''),
             data.get('overall_summary', {}).get('girls', {}).get('pass_percentage', ''),
            ],
            ['Total',
             data.get('overall_summary', {}).get('total', {}).get('appeared', ''),
             data.get('overall_summary', {}).get('total', {}).get('distinction', ''),
             data.get('overall_summary', {}).get('total', {}).get('first_class', ''),
             data.get('overall_summary', {}).get('total', {}).get('second_class', ''),
             data.get('overall_summary', {}).get('total', {}).get('pass_class', ''),
             data.get('overall_summary', {}).get('total', {}).get('passed', ''),
             data.get('overall_summary', {}).get('total', {}).get('failed', ''),
             data.get('overall_summary', {}).get('total', {}).get('pass_percentage', ''),
            ],
        ],
        logo_data=load_logo_data(),
        top_performers=data.get('top_performers', []),
        subject_summary=data.get('subject_summary', []),
        centum_achievers=data.get('centum_achievers', []),
    )


def find_docx_converter():
    if shutil.which('pandoc'):
        return 'pandoc'
    if shutil.which('soffice'):
        return 'soffice'
    if shutil.which('libreoffice'):
        return 'soffice'
    return None


def convert_html_to_docx(html_content: str) -> bytes:
    converter = find_docx_converter()
    if converter is None:
        raise RuntimeError('No HTML-to-DOCX converter found. Install pandoc or LibreOffice.')

    with tempfile.TemporaryDirectory() as temp_dir:
        html_path = Path(temp_dir) / 'report.html'
        docx_path = Path(temp_dir) / 'report.docx'
        html_path.write_text(html_content, encoding='utf-8')

        if converter == 'pandoc':
            command = ['pandoc', str(html_path), '-f', 'html', '-t', 'docx', '-o', str(docx_path)]
        else:
            command = ['soffice', '--headless', '--convert-to', 'docx', '--outdir', str(temp_dir), str(html_path)]

        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"DOCX conversion failed: {result.stderr or result.stdout}")

        if not docx_path.exists():
            raise RuntimeError('DOCX conversion succeeded but output file was not created.')

        return docx_path.read_bytes()


def build_docx_bytes(data):
    document = ET.Element(qname(W_NS, 'document'))
    body = ET.SubElement(document, qname(W_NS, 'body'))

    logo_bytes = None
    logo_paragraph = None
    logo_path = ROOT / 'Untitled_design.png'
    if logo_path.exists():
        try:
            with Image.open(logo_path) as img:
                img = img.convert('RGBA')
                width, height = img.size
                max_width = 120
                scale = min(max_width / width, 1.0)
                width_px = int(width * scale)
                height_px = int(height * scale)
                cx = width_px * 9525
                cy = height_px * 9525
                image_stream = io.BytesIO()
                img.save(image_stream, format='PNG')
                logo_bytes = image_stream.getvalue()
                image_run = make_inline_image_run('rId4', cx, cy)
                logo_paragraph = ET.Element(qname(W_NS, 'p'))
                logo_paragraph.append(image_run)
        except Exception:
            logo_bytes = None

    body.append(make_header_table(data, logo_paragraph=logo_paragraph))
    body.append(make_paragraph(''))
    body.append(make_paragraph('RESULT ANALYSIS REPORT', bold=True))
    body.append(make_paragraph(''))

    overall = data.get('overall_summary', {})
    table_rows = []
    for label, key in [('Boys', 'boys'), ('Girls', 'girls'), ('Total', 'total')]:
        row = overall.get(key, {})
        table_rows.append([
            label,
            row.get('appeared', ''),
            row.get('distinction', ''),
            row.get('first_class', ''),
            row.get('second_class', ''),
            row.get('pass_class', ''),
            row.get('passed', ''),
            row.get('failed', ''),
            row.get('pass_percentage', ''),
        ])
    body.append(make_table(
        ['Category', 'Appeared', 'Distinction', 'First Class', 'Second Class', 'Pass Class', 'Passed', 'Failed', 'Pass %'],
        table_rows
    ))
    body.append(make_paragraph(''))

    top_performers = data.get('top_performers', [])
    body.append(make_paragraph('Top Performers'))
    body.append(make_table(
        ['Rank', 'Name', 'USN', 'Marks', '%'],
        [[p.get('rank', ''), p.get('name', ''), p.get('usn', ''), p.get('marks', ''), p.get('percentage', '')] for p in top_performers]
    ))
    body.append(make_paragraph(''))

    subjects = data.get('subject_summary', [])
    if subjects:
        body.append(make_paragraph('Subject-wise Analysis'))
        body.append(make_table(
            ['Sl No', 'Code', 'Subject Name', 'Faculty', 'Passed', 'Failed', 'Absent', 'Centum', 'Pass %', 'Topper Marks'],
            [[
                idx + 1,
                subj.get('code', ''),
                subj.get('name', ''),
                subj.get('faculty', subj.get('faculty_initial', '')) or '',
                subj.get('passed', ''),
                subj.get('failed', ''),
                subj.get('absent', ''),
                subj.get('centum', ''),
                subj.get('pass_percentage', ''),
                subj.get('topper_marks', ''),
            ] for idx, subj in enumerate(subjects[:30])]
        ))
        body.append(make_paragraph(''))

    centums = data.get('centum_achievers', [])
    if centums:
        body.append(make_paragraph('Centum Achievers'))
        body.append(make_table(
            ['Sl No', 'Name', 'USN', 'Subject Code', 'Subject Name', 'Marks', 'Max Marks', '%'],
            [[
                idx + 1,
                c.get('name', ''),
                c.get('usn', ''),
                c.get('subject_code', ''),
                c.get('subject_name', ''),
                c.get('marks', ''),
                c.get('max_marks', ''),
                c.get('percentage', ''),
            ] for idx, c in enumerate(centums[:30])]
        ))
        body.append(make_paragraph(''))

    body.append(make_paragraph(''))
    body.append(make_signature_table())

    sectPr = ET.Element(qname(W_NS, 'sectPr'))
    ET.SubElement(sectPr, qname(W_NS, 'pgSz'), {qname(W_NS, 'w'): '11906', qname(W_NS, 'h'): '16838'})
    ET.SubElement(sectPr, qname(W_NS, 'pgMar'), {
        qname(W_NS, 'top'): '1440',
        qname(W_NS, 'right'): '1440',
        qname(W_NS, 'bottom'): '1440',
        qname(W_NS, 'left'): '1440',
        qname(W_NS, 'header'): '720',
        qname(W_NS, 'footer'): '720',
        qname(W_NS, 'gutter'): '0',
    })
    body.append(sectPr)

    xml_bytes = ET.tostring(document, encoding='utf-8', xml_declaration=True)

    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
  <Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
</Types>''')
        docx.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')

        docx.writestr('word/document.xml', xml_bytes)
        docx.writestr('word/styles.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
</w:styles>''')
        docx.writestr('word/fontTable.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:font w:name="Times New Roman"/>
</w:fonts>''')
        docx.writestr('word/theme/theme1.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
      <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F497D"/></a:dk2>
      <a:lt2><a:srgbClr val="EEECE1"/></a:lt2>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont>
        <a:latin typeface="Times New Roman"/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Calibri"/>
      </a:minorFont>
    </a:fontScheme>
  </a:themeElements>
</a:theme>''')

        rels = ['''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>''']
        if logo_bytes is not None:
            docx.writestr('word/media/image1.png', logo_bytes)
            rels.append('  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>')
        rels.append('</Relationships>')
        docx.writestr('word/_rels/document.xml.rels', '\n'.join(rels))

    output.seek(0)
    return output


@app.route('/api/export-report', methods=['POST'])
def export_report():
    """Generate and return a populated DOCX report based on analyzed data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No analysis data provided'}), 400

        data['generated_at'] = data.get('generated_at') or __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')
        program = data.get('program', 'Program')
        semester = data.get('semester', 'Semester')

        if request.args.get('format') == 'html':
            html = render_report_html(data)
            return send_file(
                io.BytesIO(html.encode('utf-8')),
                mimetype='text/html',
                as_attachment=True,
                download_name=f'Result_Analysis_{program}_{semester}.html'
            )

        renderer = WordReportRenderer()
        renderer.render(data)
        return send_file(
            io.BytesIO(renderer.response()),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f'Result_Analysis_{program}_{semester}.docx'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500


@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    """Generate and return a PDF report based on analyzed data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No analysis data provided'}), 400

        data['generated_at'] = data.get('generated_at') or __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')
        program = data.get('program', 'Program')
        semester = data.get('semester', 'Semester')

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            pdf_path = tmp_pdf.name

        try:
            create_pdf_report(data, pdf_path)

            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()

            return send_file(
                io.BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'Result_Analysis_{program}_{semester}.pdf'
            )
        finally:
            try:
                os.remove(pdf_path)
            except Exception:
                pass

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


def populate_overall_summary(table, program, semester, summary):
    """Populate Table 0: Overall Summary with program, semester, and pass rates."""
    try:
        # Find and update title/header cells with program and semester info
        # This depends on actual template structure - adjust as needed
        total_summary = summary.get('total', {})
        boys_summary = summary.get('boys', {})
        girls_summary = summary.get('girls', {})
        
        # Typically first few rows contain the summary statistics
        if len(table.rows) >= 2:
            # Row 0, Col 1: Program name
            if len(table.rows[0].cells) > 1:
                table.rows[0].cells[1].text = str(program)
            # Row 0/1, next col: Semester
            if len(table.rows[0].cells) > 2:
                table.rows[0].cells[2].text = str(semester)
        
        # Populate data rows (adjust indices based on actual template)
        row_idx = 1
        if len(table.rows) > row_idx:
            cells = table.rows[row_idx].cells
            if len(cells) >= 4:
                cells[1].text = str(total_summary.get('appeared', 0))  # Total appeared
                cells[2].text = str(total_summary.get('passed', 0))     # Total passed
                cells[3].text = f"{total_summary.get('pass_percentage', 0):.1f}%"  # Pass percentage
    except Exception as e:
        print(f"Error populating overall summary: {e}")


def populate_top_performers(table, top_performers):
    """Populate Table 1: Top Performers with rank, name, marks."""
    try:
        # Table rows: header + data rows for each performer
        for idx, performer in enumerate(top_performers[:10], start=1):
            if idx < len(table.rows):
                row = table.rows[idx]
                if len(row.cells) >= 5:
                    row.cells[0].text = str(performer.get('rank', ''))
                    row.cells[1].text = str(performer.get('label', ''))
                    row.cells[2].text = performer.get('name', '')
                    row.cells[3].text = performer.get('usn', '')
                    row.cells[4].text = str(performer.get('percentage', 0))
    except Exception as e:
        print(f"Error populating top performers: {e}")


def populate_subject_summary(table, subject_summary, subject_edits):
    """Populate Table 2: Subject Summary with subject details."""
    try:
        # Apply any edits first
        edited_subjects = {}
        if subject_edits:
            for edit in subject_edits:
                idx = edit.get('index')
                if idx is not None and idx < len(subject_summary):
                    subject_summary[idx].update(edit.get('changes', {}))
        
        # Table rows: header + data rows for each subject
        for idx, subject in enumerate(subject_summary[:50], start=1):
            if idx < len(table.rows):
                row = table.rows[idx]
                if len(row.cells) >= 8:
                    row.cells[0].text = str(idx)
                    row.cells[1].text = subject.get('code', '')
                    row.cells[2].text = subject.get('name', '')
                    row.cells[3].text = subject.get('faculty', subject.get('faculty_initial', ''))
                    row.cells[4].text = str(subject.get('passed', 0))
                    row.cells[5].text = str(subject.get('failed', 0))
                    row.cells[6].text = str(subject.get('absent', 0))
                    row.cells[7].text = str(subject.get('centum', 0))
    except Exception as e:
        print(f"Error populating subject summary: {e}")


def populate_demographics(table, demographics):
    """Populate Table 3: Demographics with category/gender/caste breakdowns."""
    try:
        # Demographics table structure (from earlier inspection):
        # Row 0: Headers (S.NO, Discipline, Title)
        # Row 1-2: Category headers and gender subheaders
        # Rows 3-6: Appeared section (Total, PWD, MM, OM)
        # Row 7: "Passed" section header
        # Rows 8-11: Passed section
        # Row 12: "Passed 60%" section header
        # Rows 13-16: Passed 60% section
        
        appeared_data = demographics.get('appeared', {}).get('rows', {})
        passed_data = demographics.get('passed', {}).get('rows', {})
        passed_60_data = demographics.get('passed_60', {}).get('rows', {})
        
        categories = ['General', 'EWS', 'SC', 'ST', 'OBC', 'TOTAL']
        genders = ['M', 'F', 'TG']
        row_keys = ['Total', 'PWD', 'MM', 'OM']
        
        # Populate Appeared section (rows 3-6)
        for row_idx, row_key in enumerate(row_keys):
            table_row_idx = 3 + row_idx
            if table_row_idx < len(table.rows):
                row = table.rows[table_row_idx]
                col_idx = 1  # Start after label column
                
                for category in categories:
                    for gender in genders:
                        if col_idx < len(row.cells):
                            value = appeared_data.get(row_key, {}).get(category, {}).get(gender, 0)
                            row.cells[col_idx].text = str(value or 0)
                            col_idx += 1
        
        # Populate Passed section (rows 8-11)
        for row_idx, row_key in enumerate(row_keys):
            table_row_idx = 8 + row_idx
            if table_row_idx < len(table.rows):
                row = table.rows[table_row_idx]
                col_idx = 1
                
                for category in categories:
                    for gender in genders:
                        if col_idx < len(row.cells):
                            value = passed_data.get(row_key, {}).get(category, {}).get(gender, 0)
                            row.cells[col_idx].text = str(value or 0)
                            col_idx += 1
        
        # Populate Passed 60% section (rows 13-16)
        for row_idx, row_key in enumerate(row_keys):
            table_row_idx = 13 + row_idx
            if table_row_idx < len(table.rows):
                row = table.rows[table_row_idx]
                col_idx = 1
                
                for category in categories:
                    for gender in genders:
                        if col_idx < len(row.cells):
                            value = passed_60_data.get(row_key, {}).get(category, {}).get(gender, 0)
                            row.cells[col_idx].text = str(value or 0)
                            col_idx += 1
    
    except Exception as e:
        print(f"Error populating demographics: {e}")


def populate_centum_achievers(table, centum_achievers):
    """Populate Table 4: Centum Achievers with student details."""
    try:
        # Table 4 structure: Sl. No | Name | Registration No. (USN) | Subject Name
        for idx, achiever in enumerate(centum_achievers[:7], start=1):
            if idx < len(table.rows):
                row = table.rows[idx]
                if len(row.cells) >= 4:
                    row.cells[0].text = str(idx)
                    row.cells[1].text = achiever.get('name', '')
                    row.cells[2].text = achiever.get('usn', '')
                    row.cells[3].text = achiever.get('subject_name', '')
    except Exception as e:
        print(f"Error populating centum achievers: {e}")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
