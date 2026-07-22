import zipfile
from pathlib import Path
from report.word_renderer import WordReportRenderer

context = {
    'program': 'Bachelor of Computer Applications',
    'semester': 'II Semester',
    'generated_at': '02 July 2026',
    'overall_summary': {
        'boys': {'appeared': 10, 'distinction': 1, 'first_class': 2, 'second_class': 3, 'pass_class': 2, 'passed': 8, 'failed': 2, 'pass_percentage': 80},
        'girls': {'appeared': 12, 'distinction': 2, 'first_class': 3, 'second_class': 4, 'pass_class': 2, 'passed': 11, 'failed': 1, 'pass_percentage': 92},
        'total': {'appeared': 22, 'distinction': 3, 'first_class': 5, 'second_class': 7, 'pass_class': 4, 'passed': 19, 'failed': 3, 'pass_percentage': 86},
    },
    'top_performers': [
        {'rank': 1, 'name': 'Asha', 'usn': '1MS21CS001', 'marks': 480, 'percentage': 96.0},
    ],
    'subject_summary': [
        {'code': 'CS101', 'name': 'Data Structures', 'section': '', 'faculty_name': '', 'passed': 18, 'failed': 4, 'absent': 0, 'centum': 2, 'topper_marks': 95, 'pass_percentage': 82},
    ],
    'centum_achievers': [
        {'name': 'Asha', 'usn': '1MS21CS001', 'subject_code': 'CS101', 'subject_name': 'Data Structures', 'marks': 100, 'max_marks': 100, 'percentage': 100},
    ],
    'demographics': {
        'appeared': {'rows': {'Total': {'General': {'M': 2, 'F': 1, 'TG': 0}, 'EWS': {'M': 1, 'F': 1, 'TG': 0}, 'SC': {'M': 1, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 1, 'TG': 0}, 'OBC': {'M': 2, 'F': 1, 'TG': 0}, 'TOTAL': {'M': 6, 'F': 4, 'TG': 0}}, 'PWD': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'MM': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}, 'OM': {'General': {'M': 0, 'F': 0, 'TG': 0}, 'EWS': {'M': 0, 'F': 0, 'TG': 0}, 'SC': {'M': 0, 'F': 0, 'TG': 0}, 'ST': {'M': 0, 'F': 0, 'TG': 0}, 'OBC': {'M': 0, 'F': 0, 'TG': 0}, 'TOTAL': {'M': 0, 'F': 0, 'TG': 0}}}},
        'passed': {'rows': {}, 'row_totals': {}},
        'passed_60': {'rows': {}, 'row_totals': {}},
    },
}

renderer = WordReportRenderer()
renderer.render(context)
output = renderer.response()
path = Path('out_test.docx')
path.write_bytes(output)
print('wrote', path)
with zipfile.ZipFile(path) as z:
    print('entries', z.namelist())
    xml = z.read('word/document.xml').decode('utf-8')
print('document.xml length', len(xml))
print(xml[:800])
import xml.etree.ElementTree as ET
ET.fromstring(xml)
print('XML valid')
