import { useMemo, useState } from 'react';
import './analysis.css';
import ReportDemographicsTable from './ReportDemographicsTable';
import soundaryaLogo from './assets/Untitled_design.png';
import LandingPage from './LandingPage';

const API_URL = import.meta.env.VITE_API_URL || '';

const initialState = {
  excel: null,
  pdf: null,
  excelResult: null,
  pdfResult: null,
  analysisResult: null,
  loadingExcel: false,
  loadingPdf: false,
  loadingAnalysis: false,
  step: 'excel'
};

function App() {
  const [state, setState] = useState(initialState);
  const [subjectEdits, setSubjectEdits] = useState([]);
  const [view, setView] = useState('landing');

  const excelReady = state.excelResult?.valid === true;
  const pdfReady = state.pdfResult?.valid === true;
  const canContinue = excelReady && pdfReady;
  const analysisReady = canContinue && state.analysisResult !== null;

  async function uploadAndValidate(type) {
    const file = type === 'excel' ? state.excel : state.pdf;
    if (!file) return;

    const formData = new FormData();
    formData.append(type, file);

    if (type === 'excel') {
      setState((prev) => ({ ...prev, loadingExcel: true, excelResult: null, analysisResult: null }));
    } else {
      setState((prev) => ({ ...prev, loadingPdf: true, pdfResult: null, analysisResult: null }));
    }

    try {
      const response = await fetch(`${API_URL}/api/validate/${type}`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      if (!response.ok) {
        // backend returned 4xx/5xx with JSON error
        const fallback = { valid: false, errors: [result.error || result.message || 'Validation failed.'], warnings: [] };
        if (type === 'excel') {
          setState((prev) => ({ ...prev, excelResult: fallback, loadingExcel: false }));
        } else {
          setState((prev) => ({ ...prev, pdfResult: fallback, loadingPdf: false }));
        }
      } else {
        if (type === 'excel') {
          setState((prev) => ({ ...prev, excelResult: result, loadingExcel: false, step: result.valid ? 'pdf' : 'excel' }));
        } else {
          setState((prev) => ({ ...prev, pdfResult: result, loadingPdf: false, step: result.valid ? 'done' : 'pdf' }));
        }
      }
    } catch (error) {
      const fallback = {
        valid: false,
        errors: ['Unable to reach validation service.'],
        warnings: []
      };
      if (type === 'excel') {
        setState((prev) => ({ ...prev, excelResult: fallback, loadingExcel: false }));
      } else {
        setState((prev) => ({ ...prev, pdfResult: fallback, loadingPdf: false }));
      }
    }
  }

  async function fetchAnalysis() {
    if (!canContinue) return;

    const formData = new FormData();
    formData.append('excel', state.excel);
    formData.append('pdf', state.pdf);

    setState((prev) => ({ ...prev, loadingAnalysis: true, analysisResult: null }));
    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();
      if (!response.ok) {
        setState((prev) => ({ ...prev, analysisResult: { error: result.error || result.message || 'Analysis failed.' }, loadingAnalysis: false }));
      } else {
        setState((prev) => ({ ...prev, analysisResult: result, loadingAnalysis: false }));
        setSubjectEdits(result.subject_summary?.map((subject) => ({
          code: subject.code,
          name: subject.name,
          section: '',
          faculty: '',
        })) || []);
      }
      setSubjectEdits(result.subject_summary?.map((subject) => ({
        code: subject.code,
        name: subject.name,
        section: '',
        faculty: '',
      })) || []);
    } catch (error) {
      setState((prev) => ({ ...prev, analysisResult: { error: 'Unable to fetch analysis.' }, loadingAnalysis: false }));
    }
  }

  function handleFileChange(type, event) {
    const file = event.target.files?.[0] || null;
    if (type === 'excel') {
      setState((prev) => ({ ...prev, excel: file }));
    } else {
      setState((prev) => ({ ...prev, pdf: file }));
    }
  }

  function updateSubjectEdit(index, field, value) {
    setSubjectEdits((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  }

  async function generateReport(format = 'docx') {
    if (!analysisReady) return;

    const payload = {
      program: state.analysisResult.program,
      semester: state.analysisResult.semester,
      overall_summary: state.analysisResult.overall_summary,
      top_performers: state.analysisResult.top_performers,
      subject_summary: state.analysisResult.subject_summary,
      centum_achievers: state.analysisResult.centum_achievers,
      demographics: state.analysisResult.demographics,
      subject_edits: subjectEdits,
    };

    const endpoint = format === 'pdf' ? '/api/export-pdf' : '/api/export-report';
    const fileExtension = format;

    try {
      const response = await fetch(API_URL + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `Export to ${format.toUpperCase()} failed`);
      }
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Result_Analysis_${state.analysisResult.program}_${state.analysisResult.semester}.${fileExtension}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Report export to ${format.toUpperCase()} failed`, error);
      alert(`Error: ${error.message}`);
    }
  }

  const statusBadge = useMemo(() => {
    if (state.excelResult?.valid && state.pdfResult?.valid) {
      return 'All files validated';
    }
    if (state.excelResult?.valid) {
      return 'Excel validated';
    }
    return 'Awaiting validation';
  }, [state.excelResult, state.pdfResult]);

  if (view === 'landing') {
    return <LandingPage onGetStarted={() => setView('app')} />;
  }

  return (
    <div className="app-shell">
      <div className="app-nav-header">
        <button className="btn-back-home" onClick={() => setView('landing')}>← Back to Home</button>
      </div>
      <div className="hero split-hero">
        <div className="hero-copy">
          <h1>ResultIQ</h1>
          <p className="subtext">Transforming Examination Data into Actionable Insights</p>
        </div>

        <div className="hero-branding">
          <img className="institution-logo" src={soundaryaLogo} alt="Soundarya Institute of Management and Science logo" />
          <div className="hero-branding-text">
            <p className="institution">SOUNDARYA INSTITUTE OF MANAGEMENT AND SCIENCE</p>
            <p className="tagline">Developed by Department of Computer Science</p>
          </div>
        </div>
      </div>

      <div className="status-card">
        <div>
          <strong>Status</strong>
          <div>{statusBadge}</div>
        </div>
        <div>
          <strong>Step</strong>
          <div>{state.step === 'done' ? 'Ready for processing' : state.step === 'pdf' ? 'Validate PDF' : 'Validate Excel'}</div>
        </div>
      </div>

      <div className="panel-grid">
        <section className="panel">
          <h2>1. Upload Student Master Excel</h2>
          <label className="dropzone">
            <input type="file" accept=".xlsx,.xlsm" onChange={(event) => handleFileChange('excel', event)} />
            <span>{state.excel ? state.excel.name : 'Drag & drop Excel or choose a file'}</span>
          </label>
          <button onClick={() => uploadAndValidate('excel')} disabled={!state.excel || state.loadingExcel}>
            {state.loadingExcel ? 'Validating…' : 'Validate Excel'}
          </button>
          {state.excelResult && (
            <div className={`result ${state.excelResult.valid ? 'success' : 'error'}`}>
              <h3>{state.excelResult.valid ? '✔ Excel Parsed Successfully' : '❌ Excel Validation Failed'}</h3>
              <p>{state.excelResult.message || 'Validation complete.'}</p>
              <div className="summary-grid">
                <div>
                  <strong>Students</strong>
                  <div>{state.excelResult.validation?.students ?? 0}</div>
                </div>
                <div>
                  <strong>Warnings</strong>
                  <div>{state.excelResult.validation?.warnings ?? 0}</div>
                </div>
                <div>
                  <strong>Errors</strong>
                  <div>{state.excelResult.validation?.errors ?? 0}</div>
                </div>
              </div>
              {state.excelResult.validation?.warning_summary?.length > 0 && (
                <div className="summary-list">
                  <strong>Warning summary</strong>
                  <ul>
                    {state.excelResult.validation.warning_summary.map((item) => (
                      <li key={item.message}>{item.count} × {item.message}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="panel">
          <h2>2. Upload University Marks Ledger PDF</h2>
          <label className="dropzone disabled">
            <input type="file" accept=".pdf" onChange={(event) => handleFileChange('pdf', event)} disabled={!excelReady} />
            <span>{state.pdf ? state.pdf.name : excelReady ? 'Drag & drop PDF or choose a file' : 'Complete Excel validation first'}</span>
          </label>
          <button onClick={() => uploadAndValidate('pdf')} disabled={!state.pdf || state.loadingPdf || !excelReady}>
            {state.loadingPdf ? 'Validating…' : 'Validate PDF'}
          </button>
          {state.pdfResult && (
            <div className={`result ${state.pdfResult.valid ? 'success' : 'error'}`}>
              <h3>{state.pdfResult.valid ? '✔ PDF Parsed Successfully' : '❌ PDF Validation Failed'}</h3>
              <p>{state.pdfResult.message || 'Validation complete.'}</p>
              <div className="summary-grid">
                <div>
                  <strong>Students</strong>
                  <div>{state.pdfResult.validation?.students ?? 0}</div>
                </div>
                <div>
                  <strong>Subjects</strong>
                  <div>{state.pdfResult.validation?.subjects ?? 0}</div>
                </div>
                <div>
                  <strong>Warnings</strong>
                  <div>{state.pdfResult.validation?.warnings ?? 0}</div>
                </div>
              </div>
              {state.pdfResult.validation?.warning_summary?.length > 0 && (
                <div className="summary-list">
                  <strong>Warning summary</strong>
                  <ul>
                    {state.pdfResult.validation.warning_summary.map((item) => (
                      <li key={item.message}>{item.count} × {item.message}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>
      </div>

      <section className={`final-card ${canContinue ? 'ready' : ''}`}>
        <h2>Final Validation Status</h2>
        <div className="final-row"><span>Excel</span><strong>{excelReady ? '✔ Valid' : 'Pending'}</strong></div>
        <div className="final-row"><span>PDF</span><strong>{pdfReady ? '✔ Valid' : 'Pending'}</strong></div>
        <div className="final-row"><span>Students</span><strong>{state.pdfResult?.students ?? state.excelResult?.students ?? 0}</strong></div>
        <div className="final-row"><span>Subjects</span><strong>{state.pdfResult?.subjects ?? 0}</strong></div>
        <p>{canContinue ? 'Ready for Analysis' : 'Complete both validations to continue.'}</p>
        <div className="analysis-actions">
          <button onClick={fetchAnalysis} disabled={!canContinue || state.loadingAnalysis}>
            {state.loadingAnalysis ? 'Loading preview…' : 'Show Analysis Preview'}
          </button>
        </div>
      </section>

      <div className="result-note">
        Note: This is a computer/system generated result and may be wrong if the input data is incorrect. Kindly cross check with the original documents.
      </div>

      {state.analysisResult && !state.analysisResult.error && (
        <section className="analysis-card">
          <h2>Result Analysis Preview</h2>
          <p><strong>Program:</strong> {state.analysisResult.program}</p>
          <p><strong>Semester:</strong> {state.analysisResult.semester}</p>

          <div className="summary-table-wrapper">
            <table className="summary-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Students Appeared</th>
                  <th>Distinction</th>
                  <th>First<br/>Class</th>
                  <th>Second<br/>Class</th>
                  <th>Pass<br/>Class</th>
                  <th>Total Passed</th>
                  <th>Total Failed</th>
                  <th>Pass Percentage</th>
                </tr>
              </thead>
              <tbody>
                {['boys', 'girls', 'total'].map((group) => {
                  const row = state.analysisResult.overall_summary?.[group] || {};
                  return (
                    <tr key={group} className={group === 'total' ? 'summary-total-row' : ''}>
                      <td>{group === 'total' ? 'Total' : group.charAt(0).toUpperCase() + group.slice(1)}</td>
                      <td>{row.appeared ?? '—'}</td>
                      <td>{row.distinction ?? '—'}</td>
                      <td>{row.first_class ?? '—'}</td>
                      <td>{row.second_class ?? '—'}</td>
                      <td>{row.pass_class ?? '—'}</td>
                      <td>{row.passed ?? '—'}</td>
                      <td>{row.failed ?? '—'}</td>
                      <td>{row.pass_percentage ?? '—'}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <table className="performers-table">

            <thead>
              <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>USN</th>
                <th>Marks</th>
                <th>%</th>
              </tr>
            </thead>
            <tbody>
              {state.analysisResult.top_performers?.map((student) => (
                <tr key={`${student.usn}-${student.rank}`}>
                  <td><span className="performer-label">{student.label}</span>{student.rank}</td>
                  <td>{student.name}</td>
                  <td>{student.usn}</td>
                  <td>{student.marks}</td>
                  <td>{student.percentage?.toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="classification-details">
            <h3>Verification Details</h3>
            <table className="verification-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>USN</th>
                  <th>Name</th>
                  <th>Marks</th>
                  <th>%</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries({
                  distinction: 'Distinction',
                  first_class: 'First Class',
                  second_class: 'Second Class',
                  pass_class: 'Pass Class',
                  failed: 'Failed',
                }).flatMap(([key, label]) => {
                  const details = state.analysisResult.classification_details?.[key] || [];
                  if (details.length === 0) {
                    return [
                      <tr key={`${key}-empty`} className="category-row">
                        <td colSpan={5}>{label} (0)</td>
                      </tr>
                    ];
                  }
                  return [
                    <tr key={`${key}-header`} className="category-row">
                      <td colSpan={5}>{label} ({details.length})</td>
                    </tr>,
                    ...details.map((student) => (
                      <tr key={`${key}-${student.usn}-${student.marks}`}>
                        <td>{label}</td>
                        <td>{student.usn}</td>
                        <td>{student.name}</td>
                        <td>{student.marks}</td>
                        <td>{student.percentage?.toFixed(0)}%</td>
                      </tr>
                    )),
                  ];
                })}
              </tbody>
            </table>
          </div>

          <div className="summary-table-wrapper">
            <h3>Subject-wise Analysis</h3>
            <table className="subject-summary-table">
              <thead>
                <tr>
                  <th>Sl. No</th>
                  <th>Subject</th>
                  <th>Section</th>
                  <th>Faculty Name</th>
                  <th>Passed</th>
                  <th>Failed</th>
                  <th>Absent</th>
                  <th>Centum</th>
                  <th>Pass %</th>
                  <th>Topper Marks</th>
                </tr>
              </thead>
              <tbody>
                {state.analysisResult.subject_summary?.map((subject, index) => (
                  <tr key={subject.code || index}>
                    <td>{index + 1}</td>
                    <td>{subject.name || subject.code}</td>
                    <td>
                      <input
                        type="text"
                        value={subjectEdits[index]?.section || ''}
                        placeholder="Enter Section"
                        onChange={(event) => updateSubjectEdit(index, 'section', event.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        value={subjectEdits[index]?.faculty || ''}
                        placeholder="Enter Faculty"
                        onChange={(event) => updateSubjectEdit(index, 'faculty', event.target.value)}
                      />
                    </td>
                    <td>{subject.passed ?? 0}</td>
                    <td>{subject.failed ?? 0}</td>
                    <td>{subject.absent ?? 0}</td>
                    <td>{subject.centum ?? 0}</td>
                    <td>{subject.pass_percentage ?? 0}%</td>
                    <td>{subject.topper_marks ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="summary-table-wrapper">
            {state.analysisResult?.demographics?.validation && (
              <div style={{marginBottom: 12}}>
                {state.analysisResult.demographics.validation.valid ? (
                  <div style={{color: '#065f46', fontWeight: 700}}>Demographics validation: OK</div>
                ) : (
                  <div style={{color: '#991b1b'}}>
                    <div style={{fontWeight: 700}}>Demographics validation errors:</div>
                    <ul>
                      {state.analysisResult.demographics.validation.errors.map((e, i) => (
                        <li key={i}>{e}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            <ReportDemographicsTable demographicsData={state.analysisResult?.demographics} program={state.analysisResult?.program} />
            
            {/* Legacy: Old fixed table layout preserved for reference (hidden) */}
            <div style={{display: 'none'}}>
              {/* Old demographics tables removed - using ReportDemographicsTable instead */}
            </div>
          </div>

          <div className="summary-table-wrapper">
            <h3 className="demographics-section-title">V. Centum Achievers</h3>
            <table className="subject-summary-table">
              <thead>
                <tr>
                  <th>Sl. No</th>
                  <th>USN</th>
                  <th>Name</th>
                  <th>Subject Code</th>
                  <th>Subject Name</th>
                  <th>Marks</th>
                  <th>Max Marks</th>
                  <th>%</th>
                </tr>
              </thead>
              <tbody>
                {state.analysisResult.centum_achievers?.length ? (
                  state.analysisResult.centum_achievers.map((achiever, index) => (
                    <tr key={`${achiever.usn}-${achiever.subject_code}-${index}`}>
                      <td>{index + 1}</td>
                      <td>{achiever.usn}</td>
                      <td>{achiever.name}</td>
                      <td>{achiever.subject_code}</td>
                      <td>{achiever.subject_name}</td>
                      <td>{achiever.marks}</td>
                      <td>{achiever.max_marks}</td>
                      <td>{achiever.percentage != null ? achiever.percentage.toFixed(0) + '%' : '—'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} style={{ textAlign: 'center', fontStyle: 'italic' }}>
                      NIL
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="analysis-actions">
            <button 
              onClick={() => generateReport('pdf')} 
              disabled={!analysisReady || !state.analysisResult?.subject_summary?.length}
              className="btn-pdf"
            >
              📕 Generate Report (PDF)
            </button>
            <button 
              onClick={() => generateReport('docx')} 
              disabled={!analysisReady || !state.analysisResult?.subject_summary?.length}
              className="btn-docx"
            >
              📄 Generate Report (Word)
            </button>
          </div>
        </section>
      )}

      {state.analysisResult?.error && (
        <section className="analysis-card">
          <h2>Analysis Preview Error</h2>
          <p>{state.analysisResult.error}</p>
        </section>
      )}
    </div>
  );
}

export default App;
