import { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || '';

const CSV_COLUMNS = [
  'Sl. No',
  'USN',
  'Student Name',
  'Subject Code',
  'Subject Name',
  'CIA Marks',
  'SEE Marks',
  'Grace Marks',
  'Total Marks',
  'Maximum Marks',
  'Percentage',
  'Credits',
  'Grade Point',
  'Credit Points',
  'Result',
];

function csvCell(value) {
  const text = value == null ? '' : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function getRegistrationYear(usn) {
  return String(usn || '').match(/(\d{2})(?=S\d+$)/i)?.[1] || '';
}

function getSubjectPercentage(record) {
  const result = (record.result || '').trim().toUpperCase();
  const marks = Number(record.marks);
  const maxMarks = Number(record.max_marks);
  if (
    record.marks == null
    || record.max_marks == null
    || result === 'AB'
    || result === 'ABSENT'
    || !Number.isFinite(marks)
    || !Number.isFinite(maxMarks)
    || maxMarks <= 0
  ) {
    return null;
  }
  return (marks / maxMarks) * 100;
}

function matchesPercentageBand(record, band) {
  if (!band) return true;
  const percentage = getSubjectPercentage(record);
  if (band === 'absent') return percentage == null;
  if (percentage == null) return false;
  if (band === '85+') return percentage >= 85;
  if (band === '60-85') return percentage >= 60 && percentage < 85;
  if (band === '50-60') return percentage >= 50 && percentage < 60;
  if (band === '40-50') return percentage >= 40 && percentage < 50;
  return percentage < 40;
}

function summarizeSubjectRecords(subject, records) {
  let passed = 0;
  let failed = 0;
  let absent = 0;
  let centum = 0;
  let topperMarks = null;

  for (const record of records) {
    const result = (record.result || '').trim().toUpperCase();
    if (result === 'AB' || result === 'ABSENT' || record.marks == null) {
      absent += 1;
    } else if (result === 'FAIL' || result === 'FAILED' || result === 'RETEST') {
      failed += 1;
    } else {
      passed += 1;
    }

    if (record.marks != null && record.max_marks != null && record.marks === record.max_marks) {
      centum += 1;
    }
    if (record.marks != null && (topperMarks == null || record.marks > topperMarks)) {
      topperMarks = record.marks;
    }
  }

  const attempted = passed + failed;
  return {
    ...subject,
    records,
    passed,
    failed,
    absent,
    centum,
    topper_marks: topperMarks,
    pass_percentage: attempted ? Math.round((passed / attempted) * 100) : 0,
  };
}

function summarizeSubjectOverallRecords(records, students, includeGender) {
  const createSummary = () => ({
    appeared: 0,
    distinction: 0,
    first_class: 0,
    second_class: 0,
    pass_class: 0,
    passed: 0,
    failed: 0,
    pass_percentage: 0,
  });
  const total = createSummary();
  const groups = { boys: createSummary(), girls: createSummary() };
  const gendersByUsn = new Map(
    students.map((student) => [String(student.usn || '').trim().toUpperCase(), student.gender]),
  );

  for (const record of records) {
    const result = (record.result || '').trim().toUpperCase();
    const isAbsent = result === 'AB' || result === 'ABSENT' || record.marks == null;
    const isFailed = result === 'FAIL' || result === 'FAILED' || result === 'RETEST';
    const percentage = getSubjectPercentage(record);
    const usn = String(record.usn || '').trim().toUpperCase();
    const gender = gendersByUsn.get(usn);
    const targets = [total];
    if (includeGender && groups[gender]) {
      targets.push(groups[gender]);
    }

    for (const summary of targets) {
      summary.appeared += 1;
      if (isAbsent) {
        continue;
      }
      if (isFailed) {
        summary.failed += 1;
      } else {
        summary.passed += 1;
        if (percentage >= 85) summary.distinction += 1;
        else if (percentage >= 60) summary.first_class += 1;
        else if (percentage >= 50) summary.second_class += 1;
        else if (percentage >= 40) summary.pass_class += 1;
      }
    }
  }

  for (const summary of [total, ...Object.values(groups)]) {
    const attempted = summary.passed + summary.failed;
    summary.pass_percentage = attempted
      ? Math.round((summary.passed / attempted) * 10000) / 100
      : 0;
  }

  return {
    boys: includeGender ? groups.boys : null,
    girls: includeGender ? groups.girls : null,
    total,
  };
}

export default function SubjectAnalysis({ onBack }) {
  const [file, setFile] = useState(null);
  const [studentMasterFile, setStudentMasterFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [selectedCode, setSelectedCode] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedPercentageBand, setSelectedPercentageBand] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [reportError, setReportError] = useState('');
  const [downloadingReport, setDownloadingReport] = useState(false);

  const selectedSubject = analysis?.subjects?.find((subject) => subject.code === selectedCode)
    || analysis?.subjects?.[0]
    || null;
  const registrationYears = [...new Set((analysis?.subjects || []).flatMap((subject) => subject.records || [])
    .map((record) => getRegistrationYear(record.usn))
    .filter(Boolean))].sort((first, second) => Number(second) - Number(first));
  const summaryStudents = (analysis?.summary_students || []).filter(
    (student) => !selectedYear || getRegistrationYear(student.usn) === selectedYear,
  );
  const displayedSubject = selectedSubject
    ? summarizeSubjectRecords(
      selectedSubject,
      selectedSubject.records.filter((record) => (
        (!selectedYear || getRegistrationYear(record.usn) === selectedYear)
        && matchesPercentageBand(record, selectedPercentageBand)
      )),
    )
    : null;
  const overallSummary = summarizeSubjectOverallRecords(
    displayedSubject?.records || [],
    summaryStudents,
    analysis?.student_master_matched != null,
  );

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError('Choose a marks ledger PDF to continue.');
      return;
    }

    const formData = new FormData();
    formData.append('pdf', file);
    if (studentMasterFile) {
      formData.append('excel', studentMasterFile);
    }
    setLoading(true);
    setError('');
    setAnalysis(null);
    setSelectedCode('');
    setSelectedYear('');
    setSelectedPercentageBand('');

    try {
      const response = await fetch(`${API_URL}/api/analyze/subjects`, {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || 'Unable to analyze this marks ledger.');
      }
      setAnalysis(result);
      setSelectedCode(result.subjects?.[0]?.code || '');
    } catch (requestError) {
      setError(requestError.message || 'Unable to reach the analysis service.');
    } finally {
      setLoading(false);
    }
  }

  function downloadSelectedSubject() {
    if (!displayedSubject) return;

    const rows = [
      ['Program', analysis.program || ''],
      ['Semester', analysis.semester || ''],
      ['Registration year', selectedYear || 'All years'],
      ['Students in selected subject/year', displayedSubject.records.length],
      ['Subject', displayedSubject.name || displayedSubject.code],
      ['Subject code', displayedSubject.code],
      ['Subject percentage range', selectedPercentageBand || 'All percentages'],
      ['Passed', displayedSubject.passed],
      ['Failed', displayedSubject.failed],
      ['Absent', displayedSubject.absent],
      ['Centum', displayedSubject.centum],
      ['Pass percentage', `${displayedSubject.pass_percentage}%`],
      ['Topper marks', displayedSubject.topper_marks ?? ''],
      [],
      CSV_COLUMNS,
      ...displayedSubject.records.map((record, index) => [
        index + 1,
        record.usn,
        record.name,
        displayedSubject.code,
        displayedSubject.name,
        record.cia,
        record.see,
        record.grace,
        record.marks,
        record.max_marks,
        getSubjectPercentage(record) == null ? '' : `${getSubjectPercentage(record).toFixed(2)}%`,
        record.credits,
        record.grade_point,
        record.credit_points,
        record.result || (record.marks == null ? 'ABSENT' : ''),
      ]),
    ];

    const csv = `\uFEFF${rows.map((row) => row.map(csvCell).join(',')).join('\r\n')}`;
    const blobUrl = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    const safeCode = displayedSubject.code.replace(/[^a-z0-9_-]/gi, '_');
    const yearSuffix = selectedYear ? `_${selectedYear}` : '';
    link.href = blobUrl;
    link.download = `ResultIQ_${safeCode}${yearSuffix}_subject_analysis.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
  }

  async function downloadWordReport() {
    if (!analysis || !displayedSubject) return;

    setDownloadingReport(true);
    setReportError('');
    const payload = {
      metadata: {
        program: analysis.program,
        semester: analysis.semester,
        academic_year: analysis.academic_year,
        exam: analysis.exam_month,
        result_date: analysis.result_date,
        cohort_year: selectedYear || null,
        subject_percentage_band: selectedPercentageBand || null,
      },
      subject: displayedSubject,
    };

    try {
      const response = await fetch(`${API_URL}/api/export-subject-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || 'Unable to generate the Word report.');
      }

      const blobUrl = URL.createObjectURL(await response.blob());
      const link = document.createElement('a');
      const safeSubjectCode = displayedSubject.code.replace(/[^a-z0-9_-]/gi, '_');
      const safeProgram = (analysis.program || 'Program').replace(/[^a-z0-9_-]/gi, '_');
      const safeSemester = (analysis.semester || 'Semester').replace(/[^a-z0-9_-]/gi, '_');
      const yearSuffix = selectedYear ? `_${selectedYear}` : '';
      link.href = blobUrl;
      link.download = `Subject_Analysis_${safeSubjectCode}${yearSuffix}_${safeProgram}_${safeSemester}.docx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
    } catch (requestError) {
      setReportError(requestError.message || 'Unable to reach the report service.');
    } finally {
      setDownloadingReport(false);
    }
  }

  return (
    <main className="app-shell subject-analysis-shell">
      <div className="app-nav-header">
        <button className="btn-back-home" onClick={onBack} type="button">← Back to Standard Analysis</button>
      </div>

      <header className="subject-analysis-heading">
        <p className="subject-analysis-eyebrow">Independent workflow</p>
        <h1>Subject-wise Analysis</h1>
        <p>Analyze a marks ledger on its own, or optionally add a Student Master file to match student names by USN.</p>
      </header>

      <section className="panel subject-upload-panel" aria-labelledby="ledger-upload-title">
        <h2 id="ledger-upload-title">Upload files</h2>
        <form className="subject-upload-form" onSubmit={handleSubmit}>
          <div className="subject-upload-options">
            <div className="subject-upload-option">
              <label className="subject-upload-option-title" htmlFor="subject-ledger-pdf">
                Marks ledger PDF <span className="subject-upload-required">Required</span>
              </label>
              <label className="dropzone subject-analysis-dropzone" htmlFor="subject-ledger-pdf">
                <input
                  id="subject-ledger-pdf"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={(event) => {
                    setFile(event.target.files?.[0] || null);
                    setError('');
                  }}
                  aria-describedby={error ? 'subject-analysis-error' : undefined}
                />
                <span className="visually-hidden">Marks ledger PDF: </span>
                <span>{file ? file.name : 'Choose a marks ledger PDF'}</span>
              </label>
            </div>
            <div className="subject-upload-option">
              <label className="subject-upload-option-title" htmlFor="subject-student-master">
                Student Master Excel <span className="subject-upload-optional">Optional</span>
              </label>
              <label className="dropzone subject-analysis-dropzone" htmlFor="subject-student-master">
                <input
                  id="subject-student-master"
                  type="file"
                  accept=".xlsx,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel.sheet.macroEnabled.12"
                  onChange={(event) => {
                    setStudentMasterFile(event.target.files?.[0] || null);
                    setError('');
                  }}
                  aria-describedby="student-master-help"
                />
                <span className="visually-hidden">Optional Student Master Excel: </span>
                <span>{studentMasterFile ? studentMasterFile.name : 'Choose a Student Master Excel file'}</span>
              </label>
              <p className="subject-upload-help" id="student-master-help">
                Optional: matching USNs can add the official student names to the analysis.
              </p>
            </div>
          </div>
          {error && <p className="subject-analysis-error" id="subject-analysis-error" role="alert">{error}</p>}
          <button type="submit" disabled={!file || loading}>
            {loading ? 'Analyzing ledger…' : 'Analyze Subjects'}
          </button>
        </form>
        {analysis?.student_master_matched != null && (
          <p className="subject-upload-help" role="status">
            Student Master matched {analysis.student_master_matched} of {analysis.students} ledger students by USN.
          </p>
        )}
      </section>

      {selectedSubject && (
        <>
          <section className="subject-analysis-toolbar" aria-label="Subject filter and export">
            <div className="subject-filters">
              <div className="subject-filter-control">
                <label htmlFor="registration-year-filter">Registration year (from USN)</label>
                <select id="registration-year-filter" value={selectedYear} onChange={(event) => setSelectedYear(event.target.value)}>
                  <option value="">All years</option>
                  {registrationYears.map((year) => <option key={year} value={year}>{year}</option>)}
                </select>
              </div>
              <div className="subject-filter-control">
                <label htmlFor="subject-filter">Filter by subject</label>
                <select
                  id="subject-filter"
                  value={selectedSubject.code}
                  onChange={(event) => setSelectedCode(event.target.value)}
                >
                  {analysis.subjects.map((subject) => (
                    <option key={subject.code} value={subject.code}>
                      {subject.code} - {subject.name || 'Unnamed subject'}
                    </option>
                  ))}
                </select>
              </div>
              <div className="subject-filter-control">
                <label htmlFor="subject-percentage-filter">Filter by subject percentage</label>
                <select
                  id="subject-percentage-filter"
                  value={selectedPercentageBand}
                  onChange={(event) => setSelectedPercentageBand(event.target.value)}
                >
                  <option value="">All percentages</option>
                  <option value="85+">85% and above</option>
                  <option value="60-85">60%–&lt;85%</option>
                  <option value="50-60">50%–&lt;60%</option>
                  <option value="40-50">40%–&lt;50%</option>
                  <option value="below-40">Below 40%</option>
                  <option value="absent">Absent / no marks</option>
                </select>
              </div>
            </div>
            <div className="subject-export-actions">
              <button className="subject-download-button" onClick={downloadWordReport} type="button" disabled={downloadingReport}>
                {downloadingReport ? 'Preparing subject report…' : 'Download Selected Subject DOCX'}
              </button>
              <button className="subject-download-button subject-csv-button" onClick={downloadSelectedSubject} type="button">
                Download Subject CSV
              </button>
            </div>
          </section>
          {reportError && <p className="subject-analysis-error" role="alert">{reportError}</p>}

          <section className="subject-analysis-results" aria-live="polite">
            <div className="subject-result-heading">
              <div>
                <p>{analysis.program || 'Program'}{analysis.semester ? ` · Semester ${analysis.semester}` : ''}</p>
                <h2>{selectedSubject.name || selectedSubject.code}</h2>
                <span>
                  {displayedSubject.code} · {displayedSubject.records.length} records
                  {selectedYear ? ` · Registration year ${selectedYear}` : ''}
                  {selectedPercentageBand ? ' · Percentage filtered' : ''}
                </span>
              </div>
            </div>

            <section className="subject-overall-summary" aria-labelledby="subject-overall-summary-title">
              <h3 id="subject-overall-summary-title">Overall Summary</h3>
              <div className="summary-table-wrapper">
                <table className="summary-table subject-overall-summary-table">
                  <thead>
                    <tr>
                      <th scope="col">Category</th>
                      <th scope="col">Students Appeared</th>
                      <th scope="col">Passed with Distinction (85%–100%)</th>
                      <th scope="col">Passed with First Class (60%–&lt;85%)</th>
                      <th scope="col">Passed with Second Class (50%–&lt;60%)</th>
                      <th scope="col">Passed with Pass Class (40%–&lt;50%)</th>
                      <th scope="col">Total Passed</th>
                      <th scope="col">Total Failed</th>
                      <th scope="col">Pass Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ['Boys', overallSummary.boys],
                      ['Girls', overallSummary.girls],
                      ['Total', overallSummary.total],
                    ].map(([label, row]) => (
                      <tr key={label} className={label === 'Total' ? 'summary-total-row' : undefined}>
                        <th scope="row">{label}</th>
                        <td>{row?.appeared ?? ''}</td>
                        <td>{row?.distinction ?? ''}</td>
                        <td>{row?.first_class ?? ''}</td>
                        <td>{row?.second_class ?? ''}</td>
                        <td>{row?.pass_class ?? ''}</td>
                        <td>{row?.passed ?? ''}</td>
                        <td>{row?.failed ?? ''}</td>
                        <td>{row ? `${Number(row.pass_percentage).toFixed(2)}%` : ''}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <div className="subject-metrics-grid">
              <div><span>Passed</span><strong>{displayedSubject.passed}</strong></div>
              <div><span>Failed</span><strong>{displayedSubject.failed}</strong></div>
              <div><span>Absent</span><strong>{displayedSubject.absent}</strong></div>
              <div><span>Centum</span><strong>{displayedSubject.centum}</strong></div>
              <div><span>Pass percentage</span><strong>{displayedSubject.pass_percentage}%</strong></div>
              <div><span>Topper marks</span><strong>{displayedSubject.topper_marks ?? '—'}</strong></div>
            </div>

            <div className="summary-table-wrapper subject-records-wrapper">
              <table className="subject-records-table">
                <thead>
                  <tr>
                    <th scope="col">Sl. No</th>
                    <th scope="col">USN</th>
                    <th scope="col">Student Name</th>
                    <th scope="col">CIA</th>
                    <th scope="col">SEE</th>
                    <th scope="col">Grace</th>
                    <th scope="col">Total</th>
                    <th scope="col">Max</th>
                    <th scope="col">Percentage</th>
                    <th scope="col">Result</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedSubject.records.map((record, index) => (
                    <tr key={`${record.usn || 'student'}-${index}`}>
                      <td>{index + 1}</td>
                      <td>{record.usn || '—'}</td>
                      <td>{record.name || '—'}</td>
                      <td>{record.cia ?? '—'}</td>
                      <td>{record.see ?? '—'}</td>
                      <td>{record.grace ?? '—'}</td>
                      <td>{record.marks ?? '—'}</td>
                      <td>{record.max_marks ?? '—'}</td>
                      <td>{getSubjectPercentage(record) == null ? '—' : `${getSubjectPercentage(record).toFixed(2)}%`}</td>
                      <td>{record.result || (record.marks == null ? 'ABSENT' : '—')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </main>
  );
}