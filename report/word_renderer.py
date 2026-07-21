from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image

from category_mapping import extract_program_code
from report.report_data_builder import build_report_data
from report.template_mapper import TemplateMapper

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC_NS = 'http://schemas.openxmlformats.org/drawingml/2006/picture'

ET.register_namespace('w', W_NS)
ET.register_namespace('r', R_NS)
ET.register_namespace('wp', WP_NS)
ET.register_namespace('a', A_NS)
ET.register_namespace('pic', PIC_NS)


def qname(ns: str, tag: str) -> str:
    return f'{{{ns}}}{tag}'


class WordReportRenderer:
    def __init__(self, template_path: Optional[Path | str] = None):
        base_dir = Path(__file__).resolve().parent.parent
        self.base_dir = base_dir
        self.template_path = Path(template_path or base_dir / 'templates' / 'report_template.docx')
        self.context: Dict[str, Any] = {}
        self._output_bytes: Optional[bytes] = None

    def render(self, context: Dict[str, Any]) -> WordReportRenderer:
        self.context = context or {}
        report_data = build_report_data(self.context)
        mapped_data = TemplateMapper().map(report_data)
        self._output_bytes = self._build_document_bytes(mapped_data)
        return self

    def save(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if self._output_bytes is None:
            raise RuntimeError('Document has not been rendered yet.')
        output_path.write_bytes(self._output_bytes)
        return output_path

    def response(self) -> bytes:
        if self._output_bytes is None:
            raise RuntimeError('Document has not been rendered yet.')
        return self._output_bytes

    def _build_document_bytes(self, mapped_data: Dict[str, Any]) -> bytes:
        document = ET.Element(qname(W_NS, 'document'))
        body = ET.SubElement(document, qname(W_NS, 'body'))

        # 1. Header with Logo & Institution Info
        logo_bytes, logo_run = self._prepare_logo()
        body.append(self._make_header_table(mapped_data['metadata'], logo_run))
        body.append(self._make_p('', space_after=100))

        # 2. Title & Metadata
        body.append(self._make_p('RESULT ANALYSIS REPORT', bold=True, size=36, color='1E3A8A', align='center', space_after=100))

        # Metadata summary line
        meta = mapped_data['metadata']
        program = meta.get('program') or ''
        semester = meta.get('semester') or ''
        result_date = meta.get('result_date') or ''
        academic_year = meta.get('academic_year') or ''

        meta_info = f"Program: {program}   |   Semester: {semester}   |   Result Date: {result_date}   |   Academic Year: {academic_year}"
        body.append(self._make_p(meta_info, bold=True, size=20, color='374151', align='center', space_after=200))

        # 3. Section I: Overall Summary
        body.append(self._make_p('I. Overall Summary', bold=True, size=26, color='1E3A8A', space_before=160, space_after=100))
        body.append(self._build_overall_summary_table(mapped_data.get('overall_summary', {}), mapped_data.get('summary', {})))
        body.append(self._make_p('', space_after=120))

        # 4. Section II: Top Performers
        body.append(self._make_p('II. Top Performers', bold=True, size=26, color='1E3A8A', space_before=160, space_after=100))
        body.append(self._build_top_performers_table(mapped_data.get('toppers', [])))
        body.append(self._make_p('', space_after=120))

        # 5. Section III: Subject-wise Analysis
        body.append(self._make_p('III. Subject-wise Analysis', bold=True, size=26, color='1E3A8A', space_before=160, space_after=100))
        body.append(self._build_subject_summary_table(mapped_data.get('subjects', [])))
        body.append(self._make_p('', space_after=120))

        # 6. Section IV: Performance Analysis by Demographics
        body.append(self._make_p('IV. Performance Analysis by Demographics', bold=True, size=26, color='1E3A8A', space_before=160, space_after=100))
        body.append(self._build_demographics_table(mapped_data.get('demographics', {}), program_name=mapped_data.get('metadata', {}).get('program')))
        body.append(self._make_p('', space_after=120))

        # 7. Section V: Centum Achievers
        body.append(self._make_p('V. Subject-wise Centum Achievers', bold=True, size=26, color='1E3A8A', space_before=160, space_after=100))
        body.append(self._build_centum_table(mapped_data.get('centum_achievers', [])))
        body.append(self._make_p('', space_after=200))

        # 8. Signatures Block
        body.append(self._build_signatures_table())

        # Section Properties (A4 Landscape, 0.5 in margins)
        sectPr = ET.Element(qname(W_NS, 'sectPr'))
        ET.SubElement(sectPr, qname(W_NS, 'pgSz'), {qname(W_NS, 'w'): '16838', qname(W_NS, 'h'): '11906', qname(W_NS, 'orient'): 'landscape'})
        body.append(sectPr)

        xml_bytes = ET.tostring(document, encoding='utf-8', xml_declaration=True)

        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as docx:
            docx.writestr('[Content_Types].xml', self._content_types_xml())
            docx.writestr('_rels/.rels', self._root_rels_xml())
            docx.writestr('word/document.xml', xml_bytes)
            docx.writestr('word/styles.xml', self._styles_xml())
            docx.writestr('word/fontTable.xml', self._font_table_xml())

            rels = [self._document_rels_xml_start()]
            if logo_bytes is not None:
                docx.writestr('word/media/image1.png', logo_bytes)
                rels.append('  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>')
            rels.append('</Relationships>')
            docx.writestr('word/_rels/document.xml.rels', '\n'.join(rels))

        output.seek(0)
        return output.getvalue()

    def _prepare_logo(self) -> tuple[Optional[bytes], Optional[ET.Element]]:
        logo_path = self.base_dir / 'Untitled_design.png'
        if not logo_path.exists():
            return None, None
        try:
            with Image.open(logo_path) as img:
                img = img.convert('RGBA')
                # 2x2 cm in EMUs (1 cm = 360,000 EMUs)
                cx = 720000
                cy = 720000

                stream = io.BytesIO()
                img.save(stream, format='PNG')
                logo_bytes = stream.getvalue()
                logo_run = self._make_inline_image_run('rId4', cx, cy)
                return logo_bytes, logo_run
        except Exception:
            return None, None

    def _make_p(self, text: str, bold: bool = False, size: int = 20, color: Optional[str] = None, align: str = 'left', space_before: int = 0, space_after: int = 60) -> ET.Element:
        p = ET.Element(qname(W_NS, 'p'))
        pPr = ET.SubElement(p, qname(W_NS, 'pPr'))

        if space_before or space_after:
            spacing = {}
            if space_before:
                spacing[qname(W_NS, 'before')] = str(space_before)
            if space_after:
                spacing[qname(W_NS, 'after')] = str(space_after)
            ET.SubElement(pPr, qname(W_NS, 'spacing'), spacing)

        if align != 'left':
            ET.SubElement(pPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): align})

        r = ET.SubElement(p, qname(W_NS, 'r'))
        rPr = ET.SubElement(r, qname(W_NS, 'rPr'))
        ET.SubElement(rPr, qname(W_NS, 'rFonts'), {qname(W_NS, 'ascii'): 'Calibri', qname(W_NS, 'hAnsi'): 'Calibri'})
        if bold:
            ET.SubElement(rPr, qname(W_NS, 'b'))
        if color:
            ET.SubElement(rPr, qname(W_NS, 'color'), {qname(W_NS, 'val'): color})
        if size:
            ET.SubElement(rPr, qname(W_NS, 'sz'), {qname(W_NS, 'val'): str(size)})

        t = ET.SubElement(r, qname(W_NS, 't'))
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = text
        return p

    def _make_cell(self, text_or_p: str | ET.Element | List[ET.Element], header: bool = False, bg_color: Optional[str] = None, align: str = 'center', bold: bool = False, width: Optional[int] = None, col_span: int = 1) -> ET.Element:
        tc = ET.Element(qname(W_NS, 'tc'))
        tcPr = ET.SubElement(tc, qname(W_NS, 'tcPr'))
        if width:
            ET.SubElement(tcPr, qname(W_NS, 'tcW'), {qname(W_NS, 'w'): str(width), qname(W_NS, 'type'): 'dxa'})
        if col_span > 1:
            ET.SubElement(tcPr, qname(W_NS, 'gridSpan'), {qname(W_NS, 'val'): str(col_span)})

        if header and not bg_color:
            bg_color = '1F497D'
        if bg_color:
            ET.SubElement(tcPr, qname(W_NS, 'shd'), {qname(W_NS, 'val'): 'clear', qname(W_NS, 'color'): 'auto', qname(W_NS, 'fill'): bg_color})

        text_color = 'FFFFFF' if (bg_color and bg_color.upper() not in {'FFFFFF', 'F9FAFB'}) else None

        if isinstance(text_or_p, list):
            for item in text_or_p:
                tc.append(item)
        elif isinstance(text_or_p, ET.Element):
            tc.append(text_or_p)
        else:
            p = self._make_p(str(text_or_p), bold=(bold or header), size=22, color=text_color, align=align, space_after=0)
            tc.append(p)

        return tc

    def _make_table(self, headers: List[str], rows: List[List[Any]], col_widths: Optional[List[int]] = None, header_bg: str = '1F497D', table_width: int = 15400) -> ET.Element:
        tbl = ET.Element(qname(W_NS, 'tbl'))
        tblPr = ET.SubElement(tbl, qname(W_NS, 'tblPr'))
        ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): str(table_width), qname(W_NS, 'type'): 'dxa'})
        ET.SubElement(tblPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): 'center'})
        tblBorders = ET.SubElement(tblPr, qname(W_NS, 'tblBorders'))
        for border in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            ET.SubElement(tblBorders, qname(W_NS, border), {qname(W_NS, 'val'): 'single', qname(W_NS, 'sz'): '4', qname(W_NS, 'space'): '0', qname(W_NS, 'color'): 'D1D5DB'})
        ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})

        if col_widths:
            tblGrid = ET.SubElement(tbl, qname(W_NS, 'tblGrid'))
            for w in col_widths:
                ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): str(w)})

        if headers:
            tr = ET.SubElement(tbl, qname(W_NS, 'tr'))
            for i, h in enumerate(headers):
                w = col_widths[i] if col_widths and i < len(col_widths) else None
                tr.append(self._make_cell(h, header=True, bg_color=header_bg, align='center', width=w))

        for row_idx, row in enumerate(rows):
            tr = ET.SubElement(tbl, qname(W_NS, 'tr'))
            bg = 'F9FAFB' if row_idx % 2 == 1 else 'FFFFFF'
            for col_idx, val in enumerate(row):
                w = col_widths[col_idx] if col_widths and col_idx < len(col_widths) else None
                align = 'left' if col_idx in {1, 2} and len(row) > 3 else 'center'
                tr.append(self._make_cell(str(val if val is not None else ''), header=False, bg_color=bg, align=align, width=w))

        return tbl

    def _make_header_table(self, metadata: Dict[str, Any], logo_run: Optional[ET.Element]) -> ET.Element:
        p_trust = self._make_p('SOUNDARYA EDUCATIONAL TRUST (REGD.)', bold=True, size=22, color='111827', align='center', space_after=20)
        p_inst = self._make_p('SOUNDARYA INSTITUTE OF MANAGEMENT & SCIENCE', bold=True, size=36, color='1E3A8A', align='center', space_after=20)
        p_addr = self._make_p('Soundarya Nagar, Sidedahalli, Nagasandra Post, Bengaluru – 560073, Karnataka', size=18, color='4B5563', align='center', space_after=10)
        p_affil = self._make_p('Recognized by Govt. of Karnataka | Affiliated to Bangalore University | NAAC Accredited B++', size=18, color='4B5563', align='center', space_after=0)

        info_cell = self._make_cell([p_trust, p_inst, p_addr, p_affil], align='center', width=14266)

        if logo_run is not None:
            logo_p = ET.Element(qname(W_NS, 'p'))
            pPr = ET.SubElement(logo_p, qname(W_NS, 'pPr'))
            ET.SubElement(pPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): 'center'})
            logo_p.append(logo_run)
            logo_cell = self._make_cell(logo_p, align='center', width=1134)
        else:
            logo_cell = self._make_cell('', width=1134)

        tbl = ET.Element(qname(W_NS, 'tbl'))
        tblPr = ET.SubElement(tbl, qname(W_NS, 'tblPr'))
        ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): '15400', qname(W_NS, 'type'): 'dxa'})
        ET.SubElement(tblPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): 'center'})
        ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})
        tblGrid = ET.SubElement(tbl, qname(W_NS, 'tblGrid'))
        ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): '1134'})
        ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): '14266'})
        tr = ET.SubElement(tbl, qname(W_NS, 'tr'))
        tr.append(logo_cell)
        tr.append(info_cell)
        return tbl

    def _build_overall_summary_table(self, overall_summary: Dict[str, Any], summary_fallback: Dict[str, Any]) -> ET.Element:
        headers = ['Category', 'Appeared', 'Distinction', 'First Class', 'Second Class', 'Pass Class', 'Passed', 'Failed', 'Pass %']
        col_widths = [2600, 1600, 1600, 1600, 1600, 1600, 1600, 1600, 1600]
        rows = []

        if isinstance(overall_summary, dict) and any(k in overall_summary for k in ['boys', 'girls', 'total']):
            for label, key in [('Boys', 'boys'), ('Girls', 'girls'), ('Total', 'total')]:
                grp = overall_summary.get(key, {}) if isinstance(overall_summary.get(key), dict) else {}
                pass_pct = grp.get('pass_percentage')
                pass_pct_str = f"{pass_pct}%" if pass_pct is not None and str(pass_pct) != 'N/A' else 'N/A'
                rows.append([
                    label,
                    grp.get('appeared', 'N/A'),
                    grp.get('distinction', 'N/A'),
                    grp.get('first_class', 'N/A'),
                    grp.get('second_class', 'N/A'),
                    grp.get('pass_class', 'N/A'),
                    grp.get('passed', 'N/A'),
                    grp.get('failed', 'N/A'),
                    pass_pct_str,
                ])
        else:
            pass_pct = summary_fallback.get('pass_percentage')
            pass_pct_str = f"{pass_pct}%" if pass_pct is not None and str(pass_pct) != 'N/A' else 'N/A'
            rows.append([
                'Total',
                summary_fallback.get('appeared', 'N/A'),
                summary_fallback.get('distinction', 'N/A'),
                summary_fallback.get('first_class', 'N/A'),
                summary_fallback.get('second_class', 'N/A'),
                summary_fallback.get('pass_class', 'N/A'),
                summary_fallback.get('passed', 'N/A'),
                summary_fallback.get('failed', 'N/A'),
                pass_pct_str,
            ])

        return self._make_table(headers, rows, col_widths)

    def _build_top_performers_table(self, toppers: List[Dict[str, Any]]) -> ET.Element:
        headers = ['Rank', 'Name', 'Registration No. (USN)', 'Marks', '%']
        col_widths = [1400, 5200, 4000, 2400, 2400]
        if not toppers:
            return self._make_table(headers, [['—', 'No toppers available', '—', '—', '—']], col_widths)

        rows = []
        for idx, t in enumerate(toppers, start=1):
            rank = t.get('label') or str(t.get('rank', idx))
            pct = t.get('percentage')
            pct_str = f"{pct:.1f}%" if isinstance(pct, (int, float)) else str(pct or 'N/A')
            rows.append([
                rank,
                t.get('name', 'N/A'),
                t.get('usn') or t.get('registration_no', 'N/A'),
                t.get('marks', 'N/A'),
                pct_str,
            ])
        return self._make_table(headers, rows, col_widths)

    def _build_subject_summary_table(self, subjects: List[Dict[str, Any]]) -> ET.Element:
        headers = ['Sl. No', 'Sub Code', 'Subject Name', 'Section', 'Faculty Name', 'Passed', 'Failed', 'Absent', 'Centum', 'Pass %', 'Topper Marks']
        col_widths = [900, 1800, 4500, 1100, 2300, 900, 900, 900, 900, 1100, 1100]

        if not subjects:
            return self._make_table(headers, [['—', '—', 'No subject data available', '—', '—', '—', '—', '—', '—', '—', '—']], col_widths)

        rows = []
        for idx, s in enumerate(subjects, start=1):
            code = s.get('code') or s.get('subject_code') or 'N/A'
            name = s.get('name') or s.get('subject_name') or 'N/A'
            sec = s.get('section') or ''
            fac = s.get('faculty') or s.get('faculty_name') or s.get('faculty_initial') or ''
            pass_pct = s.get('pass_percentage')
            pass_pct_str = f"{pass_pct}%" if pass_pct is not None and str(pass_pct) != 'N/A' else '0%'
            rows.append([
                idx,
                code,
                name,
                sec,
                fac,
                s.get('passed', 0),
                s.get('failed', 0),
                s.get('absent', 0),
                s.get('centum', 0),
                pass_pct_str,
                s.get('topper_marks', 'N/A'),
            ])
        return self._make_table(headers, rows, col_widths)

    def _build_demographics_table(self, demographics: Dict[str, Any], program_name: Optional[str] = None) -> ET.Element:
        tbl = ET.Element(qname(W_NS, 'tbl'))
        tblPr = ET.SubElement(tbl, qname(W_NS, 'tblPr'))
        ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): '15400', qname(W_NS, 'type'): 'dxa'})
        ET.SubElement(tblPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): 'center'})
        tblBorders = ET.SubElement(tblPr, qname(W_NS, 'tblBorders'))
        for border in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            ET.SubElement(tblBorders, qname(W_NS, border), {qname(W_NS, 'val'): 'single', qname(W_NS, 'sz'): '4', qname(W_NS, 'space'): '0', qname(W_NS, 'color'): 'D1D5DB'})
        ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})

        # Column widths: 3 meta cols + 18 category cols (Total = 15400 dxa)
        col_widths = [700, 1200, 1100] + [700] * 18
        tblGrid = ET.SubElement(tbl, qname(W_NS, 'tblGrid'))
        for w in col_widths:
            ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): str(w)})

        # Header Row 0
        tr0 = ET.SubElement(tbl, qname(W_NS, 'tr'))
        tr0.append(self._make_cell('S. NO', header=True, bg_color='1F497D', width=700))
        tr0.append(self._make_cell('Discipline', header=True, bg_color='1F497D', width=1200))
        tr0.append(self._make_cell('Category', header=True, bg_color='1F497D', width=1100))
        for cat in ['General', 'EWS', 'SC', 'ST', 'OBC', 'TOTAL']:
            tr0.append(self._make_cell(cat, header=True, bg_color='1F497D', col_span=3, width=2100))

        # Header Row 1 (M / F / TG subheaders)
        tr1 = ET.SubElement(tbl, qname(W_NS, 'tr'))
        tr1.append(self._make_cell('', header=True, bg_color='1F497D', width=700))
        tr1.append(self._make_cell('', header=True, bg_color='1F497D', width=1200))
        tr1.append(self._make_cell('', header=True, bg_color='1F497D', width=1100))
        for _ in range(6):
            for gender in ['M', 'F', 'TG']:
                tr1.append(self._make_cell(gender, header=True, bg_color='2563EB', width=700))

        appeared_rows = demographics.get('appeared', {}).get('rows', {}) if isinstance(demographics.get('appeared'), dict) else {}
        passed_rows = demographics.get('passed', {}).get('rows', {}) if isinstance(demographics.get('passed'), dict) else {}
        passed_60_rows = demographics.get('passed_60', {}).get('rows', {}) if isinstance(demographics.get('passed_60'), dict) else {}

        categories = ['General', 'EWS', 'SC', 'ST', 'OBC', 'TOTAL']
        genders = ['M', 'F', 'TG']
        row_keys = ['Total', 'PWD', 'MM', 'OM']

        discipline = extract_program_code(program_name or demographics.get('program') or '')

        sections = [
            ('Total Number of Students Appeared', appeared_rows),
            ('Total Number of Students Passed/Awarded Degree', passed_rows),
            ('Out of Total, Number of Students Passed with 60% or above', passed_60_rows),
        ]

        for sec_title, sec_dict in sections:
            # Section title row
            tr_sec = ET.SubElement(tbl, qname(W_NS, 'tr'))
            tr_sec.append(self._make_cell(sec_title, header=True, bg_color='3B82F6', align='left', bold=True, col_span=21))

            for idx, rkey in enumerate(row_keys, start=1):
                tr = ET.SubElement(tbl, qname(W_NS, 'tr'))
                tr.append(self._make_cell(str(idx), align='center', width=700))
                tr.append(self._make_cell(discipline, align='center', width=1200))
                tr.append(self._make_cell(rkey, align='center', bold=True, width=1100))

                r_data = sec_dict.get(rkey, {}) if isinstance(sec_dict, dict) else {}
                for cat in categories:
                    cat_data = r_data.get(cat, {}) if isinstance(r_data, dict) else {}
                    for g in genders:
                        val = cat_data.get(g, 0) if isinstance(cat_data, dict) else 0
                        tr.append(self._make_cell(str(val), align='center', width=700))

        return tbl

    def _build_centum_table(self, centum_achievers: List[Dict[str, Any]]) -> ET.Element:
        headers = ['Sl. No', 'Name', 'Registration No. (USN)', 'Sub Code', 'Subject Name', 'Marks', 'Max Marks', '%']
        col_widths = [1000, 4000, 3000, 1800, 3200, 800, 800, 800]

        if not centum_achievers:
            return self._make_table(headers, [['—', 'NIL', '—', '—', '—', '—', '—', '—']], col_widths)

        rows = []
        for idx, c in enumerate(centum_achievers, start=1):
            pct = c.get('percentage')
            pct_str = f"{pct:.1f}%" if isinstance(pct, (int, float)) else str(pct or '100%')
            rows.append([
                idx,
                c.get('name', 'N/A'),
                c.get('usn') or c.get('registration_no', 'N/A'),
                c.get('subject_code', 'N/A'),
                c.get('subject_name', 'N/A'),
                c.get('marks', 'N/A'),
                c.get('max_marks', 'N/A'),
                pct_str,
            ])
        return self._make_table(headers, rows, col_widths)

    def _build_signatures_table(self) -> ET.Element:
        headers = ['Head of Department', 'Controller of Examination', 'Principal']
        col_widths = [5133, 5133, 5134]

        tbl = ET.Element(qname(W_NS, 'tbl'))
        tblPr = ET.SubElement(tbl, qname(W_NS, 'tblPr'))
        ET.SubElement(tblPr, qname(W_NS, 'tblW'), {qname(W_NS, 'w'): '15400', qname(W_NS, 'type'): 'dxa'})
        ET.SubElement(tblPr, qname(W_NS, 'jc'), {qname(W_NS, 'val'): 'center'})
        ET.SubElement(tblPr, qname(W_NS, 'tblLayout'), {qname(W_NS, 'type'): 'fixed'})
        tblGrid = ET.SubElement(tbl, qname(W_NS, 'tblGrid'))
        for w in col_widths:
            ET.SubElement(tblGrid, qname(W_NS, 'gridCol'), {qname(W_NS, 'w'): str(w)})

        # Empty row for signature space
        tr_sig = ET.SubElement(tbl, qname(W_NS, 'tr'))
        for w in col_widths:
            p_empty = self._make_p('', space_before=400, space_after=0)
            tr_sig.append(self._make_cell(p_empty, width=w))

        # Title row
        tr_title = ET.SubElement(tbl, qname(W_NS, 'tr'))
        for i, h in enumerate(headers):
            p_title = self._make_p(h, bold=True, size=22, color='1F497D', align='center', space_after=0)
            tr_title.append(self._make_cell(p_title, width=col_widths[i]))

        return tbl

    def _make_inline_image_run(self, rId: str, cx: int, cy: int) -> ET.Element:
        run = ET.Element(qname(W_NS, 'r'))
        drawing = ET.SubElement(run, qname(W_NS, 'drawing'))
        inline = ET.SubElement(drawing, qname(WP_NS, 'inline'), {'distT': '0', 'distB': '0', 'distL': '0', 'distR': '0'})
        ET.SubElement(inline, qname(WP_NS, 'extent'), {'cx': str(cx), 'cy': str(cy)})
        ET.SubElement(inline, qname(WP_NS, 'effectExtent'), {'l': '0', 't': '0', 'r': '0', 'b': '0'})
        ET.SubElement(inline, qname(WP_NS, 'docPr'), {'id': '1', 'name': 'Picture 1'})
        cNvGraphicFramePr = ET.SubElement(inline, qname(WP_NS, 'cNvGraphicFramePr'))
        ET.SubElement(cNvGraphicFramePr, qname(A_NS, 'graphicFrameLocks'), {qname(A_NS, 'noChangeAspect'): '1'})
        graphic = ET.SubElement(inline, qname(A_NS, 'graphic'))
        graphicData = ET.SubElement(graphic, qname(A_NS, 'graphicData'), {'uri': 'http://schemas.openxmlformats.org/drawingml/2006/picture'})
        pic = ET.SubElement(graphicData, qname(PIC_NS, 'pic'))
        nvPicPr = ET.SubElement(pic, qname(PIC_NS, 'nvPicPr'))
        ET.SubElement(nvPicPr, qname(PIC_NS, 'cNvPr'), {'id': '0', 'name': 'Picture 1'})
        ET.SubElement(nvPicPr, qname(PIC_NS, 'cNvPicPr'))
        blipFill = ET.SubElement(pic, qname(PIC_NS, 'blipFill'))
        ET.SubElement(blipFill, qname(A_NS, 'blip'), {qname(R_NS, 'embed'): rId})
        ET.SubElement(blipFill, qname(A_NS, 'stretch')).append(ET.Element(qname(A_NS, 'fillRect')))
        spPr = ET.SubElement(pic, qname(PIC_NS, 'spPr'))
        xfrm = ET.SubElement(spPr, qname(A_NS, 'xfrm'))
        ET.SubElement(xfrm, qname(A_NS, 'off'), {'x': '0', 'y': '0'})
        ET.SubElement(xfrm, qname(A_NS, 'ext'), {'cx': str(cx), 'cy': str(cy)})
        prstGeom = ET.SubElement(spPr, qname(A_NS, 'prstGeom'), {'prst': 'rect'})
        ET.SubElement(prstGeom, qname(A_NS, 'avLst'))
        return run

    def _content_types_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
</Types>'''

    def _root_rels_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    def _document_rels_xml_start(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>'''

    def _styles_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
</w:styles>'''

    def _font_table_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:font w:name="Calibri"/>
</w:fonts>'''
