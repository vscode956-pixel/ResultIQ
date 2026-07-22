from pathlib import Path
from excel_parser import parse_students

files = [
    '2024-25 BCA Data with Caste.xlsx',
    '2024-25 BCA Data with Caste (1).xlsx',
]

for f in files:
    p = Path(f)
    print('FILE', f, 'EXISTS', p.exists())
    if not p.exists():
        continue
    parsed = parse_students(str(p))
    print(' error:', parsed.get('error'))
    print(' message:', parsed.get('message'))
    print(' rows:', len(parsed.get('rows', [])))
    print(' warnings:', parsed.get('warnings'))
    print(' mapping:', {k: v['header'] for k, v in parsed.get('mapping', {}).items()})
    print(' header_row:', parsed.get('header_row_index'))
    print('---')
