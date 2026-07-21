from __future__ import annotations

from typing import Any, Dict, List


def build_report_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize analysis payload into a report contract consumed by the renderer."""
    if not isinstance(raw_data, dict):
        raw_data = {}

    metadata = raw_data.get('metadata') if isinstance(raw_data.get('metadata'), dict) else {}
    if not metadata:
        metadata = {
            'program': raw_data.get('program'),
            'semester': raw_data.get('semester'),
            'academic_year': raw_data.get('academic_year') or raw_data.get('year'),
            'exam': raw_data.get('exam') or raw_data.get('exam_month'),
            'result_date': raw_data.get('result_date') or raw_data.get('print_date') or raw_data.get('generated_at'),
        }

    overall_summary = raw_data.get('overall_summary') if isinstance(raw_data.get('overall_summary'), dict) else {}
    summary = raw_data.get('summary') if isinstance(raw_data.get('summary'), dict) else {}

    if not overall_summary and summary.get('overall_summary'):
        overall_summary = summary.get('overall_summary')

    if not summary:
        total_summary = overall_summary.get('total', {}) if isinstance(overall_summary, dict) else {}
        summary = {
            'appeared': total_summary.get('appeared', raw_data.get('appeared')),
            'passed': total_summary.get('passed', raw_data.get('passed')),
            'failed': total_summary.get('failed', raw_data.get('failed')),
            'distinction': total_summary.get('distinction', raw_data.get('distinction')),
            'first_class': total_summary.get('first_class', raw_data.get('first_class')),
            'second_class': total_summary.get('second_class', raw_data.get('second_class')),
            'pass_class': total_summary.get('pass_class', raw_data.get('pass_class')),
            'pass_percentage': total_summary.get('pass_percentage', raw_data.get('pass_percentage')),
        }

    demographics = raw_data.get('demographics')
    if demographics is None:
        demographics = []

    subjects = raw_data.get('subject_summary')
    if subjects is None:
        subjects = raw_data.get('subjects') or []
    if not isinstance(subjects, list):
        subjects = []
    # Make copy of subjects to avoid mutating raw inputs
    subjects = [dict(s) if isinstance(s, dict) else {} for s in subjects]

    subject_edits = raw_data.get('subject_edits')
    if isinstance(subject_edits, list):
        for idx, edit in enumerate(subject_edits):
            if isinstance(edit, dict):
                target_idx = edit.get('index', idx)
                if isinstance(target_idx, int) and 0 <= target_idx < len(subjects):
                    if edit.get('section'):
                        subjects[target_idx]['section'] = edit.get('section')
                    if edit.get('faculty'):
                        subjects[target_idx]['faculty'] = edit.get('faculty')
                    elif edit.get('faculty_name'):
                        subjects[target_idx]['faculty'] = edit.get('faculty_name')

    toppers = raw_data.get('top_performers')
    if toppers is None:
        toppers = raw_data.get('toppers') or []
    if not isinstance(toppers, list):
        toppers = []

    centum = raw_data.get('centum_achievers')
    if centum is None:
        centum = raw_data.get('centum') or []
    if not isinstance(centum, list):
        centum = []

    return {
        'metadata': {
            'program': metadata.get('program') or 'N/A',
            'semester': metadata.get('semester') or 'N/A',
            'academic_year': metadata.get('academic_year') or 'N/A',
            'exam': metadata.get('exam') or 'N/A',
            'result_date': metadata.get('result_date') or 'N/A',
        },
        'overall_summary': overall_summary,
        'summary': {
            'appeared': summary.get('appeared', 'N/A'),
            'passed': summary.get('passed', 'N/A'),
            'failed': summary.get('failed', 'N/A'),
            'distinction': summary.get('distinction', 'N/A'),
            'first_class': summary.get('first_class', 'N/A'),
            'second_class': summary.get('second_class', 'N/A'),
            'pass_class': summary.get('pass_class', 'N/A'),
            'pass_percentage': summary.get('pass_percentage', 'N/A'),
        },
        'demographics': demographics,
        'subjects': subjects,
        'toppers': toppers,
        'centum_achievers': centum,
    }

