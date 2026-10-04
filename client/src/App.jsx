import { useEffect, useMemo, useState } from 'react';
import './analysis.css';
import ReportDemographicsTable from './ReportDemographicsTable';
import soundaryaLogo from './assets/Untitled_design.png';
import LandingPage from './LandingPage';
import SubjectAnalysis from './SubjectAnalysis';

const API_URL = import.meta.env.VITE_API_URL || '';
const DEFAULT_LOGIN = {
  username: import.meta.env.VITE_LOGIN_USERNAME || 'admin',
  password: import.meta.env.VITE_LOGIN_PASSWORD || 'ResultIQ@2026',
};

const getStoredAuth = () => {
  try {
    return localStorage.getItem('resultiq_auth') === 'true';
  } catch {
    return false;
  }
};

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
  const [isAuthenticated, setIsAuthenticated] = useState(getStoredAuth());
  const [view, setView] = useState(getStoredAuth() ? 'app' : 'landing');
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [formErrors, setFormErrors] = useState({});
  const [activeTool, setActiveTool] = useState('standard');

  useEffect(() => {
    if (!isAuthenticated && view === 'app') {
      setView('login');
    }
  }, [isAuthenticated, view]);

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

  function handleLoginSubmit(event) {
    event.preventDefault();
    const submittedUsername = loginForm.username.trim();
    const submittedPassword = loginForm.password;

    const nextErrors = {};

    if (!submittedUsername) {
      nextErrors.username = 'Please enter your username.';
    }

    if (!submittedPassword) {
      nextErrors.password = 'Please enter your password.';
    }

    if (Object.keys(nextErrors).length > 0) {
      setFormErrors(nextErrors);
      setLoginError('');
      return;
    }

    setFormErrors({});

    if (submittedUsername === DEFAULT_LOGIN.username && submittedPassword === DEFAULT_LOGIN.password) {
      localStorage.setItem('resultiq_auth', 'true');
      setIsAuthenticated(true);
      setLoginError('');
      setView('app');
      return;
    }

    setLoginError('Invalid username or password. Please use the authorized login details.');
  }

  function handleFieldChange(field, value) {
    setLoginForm((prev) => ({ ...prev, [field]: value }));
    setFormErrors((prev) => ({ ...prev, [field]: '' }));
    setLoginError('');
  }

  function InputIcon({ type = 'user' }) {
    if (type === 'password') {
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 10V8a5 5 0 0 1 10 0v2M6 10h12a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="12" cy="14.5" r="1.5" fill="currentColor" />
        </svg>
      );
    }

    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" strokeWidth="1.8" />
        <path d="M5 20a7 7 0 0 1 14 0" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    );
  }

  function handleLogout() {
    localStorage.removeItem('resultiq_auth');
    setIsAuthenticated(false);
    setLoginForm({ username: '', password: '' });
    setLoginError('');
    setView('login');
  }

  if (view === 'landing') {
    return <LandingPage onGetStarted={() => setView('login')} />;
  }

  if (view === 'login') {
    return (
      <div className="auth-shell">
        <div className="auth-layout">
          <section className="auth-card" aria-labelledby="login-title">
            <div className="brand-row" aria-label="ResultIQ branding">
              <div className="brand-mark" aria-hidden="true">
                <span className="bar bar-a" />
                <span className="bar bar-b" />
                <span className="bar bar-c" />
              </div>
              <div className="brand-name" aria-label="ResultIQ">
                <span className="brand-first">Result</span>
                <span className="brand-second">IQ</span>
              </div>
            </div>

            <p className="brand-tagline">Analyze • Visualize • Empower</p>

            <div className="auth-header">
              <span className="auth-badge">Secure Access</span>
              <h1 id="login-title">Login to ResultIQ</h1>
            </div>

            <form className="auth-form" onSubmit={handleLoginSubmit} noValidate>
              <div className="field-group">
                <label htmlFor="username">Username</label>
                <div className={`input-wrap ${formErrors.username ? 'is-invalid' : ''}`}>
                  <span className="input-icon" aria-hidden="true">
                    <InputIcon type="user" />
                  </span>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={loginForm.username}
                    onChange={(event) => handleFieldChange('username', event.target.value)}
                    placeholder="Enter username"
                    autoComplete="username"
                    aria-invalid={Boolean(formErrors.username || loginError)}
                  />
                </div>
                {formErrors.username && <p className="field-error">{formErrors.username}</p>}
              </div>

              <div className="field-group">
                <label htmlFor="password">Password</label>
                <div className={`input-wrap ${formErrors.password ? 'is-invalid' : ''}`}>
                  <span className="input-icon" aria-hidden="true">
                    <InputIcon type="password" />
                  </span>
                  <input
                    id="password"
                    name="password"
                    type={isPasswordVisible ? 'text' : 'password'}
                    value={loginForm.password}
                    onChange={(event) => handleFieldChange('password', event.target.value)}
                    placeholder="Enter password"
                    autoComplete="current-password"
                    aria-invalid={Boolean(formErrors.password || loginError)}
                  />
                  <button
                    type="button"
                    className="password-visibility-btn"
                    onClick={() => setIsPasswordVisible((visible) => !visible)}
                    aria-label={isPasswordVisible ? 'Hide password' : 'Show password'}
                    aria-pressed={isPasswordVisible}
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" strokeWidth="1.8" />
                      {!isPasswordVisible && (
                        <path d="m4 4 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                      )}
                    </svg>
                  </button>
                </div>
                {formErrors.password && <p className="field-error">{formErrors.password}</p>}
              </div>

              {loginError && <div className="auth-error" role="alert">{loginError}</div>}

              <button type="submit" className="auth-submit-btn">
                <span>Login</span>
                <span aria-hidden="true">→</span>
              </button>
            </form>

            <div className="auth-divider" aria-hidden="true">
              <span>OR</span>
            </div>

            <button className="btn-back-home auth-back" onClick={() => setView('landing')} type="button">
              <span aria-hidden="true">←</span>
              <span>Back to Home</span>
            </button>
          </section>

          <aside className="auth-info-panel" aria-label="Subscription access information">
            <div className="info-visual" aria-hidden="true">
              <div className="visual-window visual-window-one" />
              <div className="visual-window visual-window-two" />
              <div className="visual-cap" />
            </div>

            <div className="info-copy">
              <div className="info-header">
                <div className="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M4 10.5V8.5A2 2 0 0 1 6 6.5h12a2 2 0 0 1 2 2v2M5 10.5h14v8a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-8Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M9 14h6M9 17h6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                  </svg>
                </div>
                <h2>Need subscription access for your institution or department?</h2>
              </div>

              <p>Contact the developer to request a valid subscription ID and institutional access.</p>
            </div>

            <div className="info-contact-list">
              <div className="contact-row">
                <span className="contact-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M7 8.5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-7Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M8 9.5 12 13l4-3.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
                <span><strong>Developer:</strong> Deepu K C</span>
              </div>
              <div className="contact-row">
                <span className="contact-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h11A2.5 2.5 0 0 1 20 8.5v7A2.5 2.5 0 0 1 17.5 18h-11A2.5 2.5 0 0 1 4 15.5v-7Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M5 8.5 12 13l7-4.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
                <span><strong>Email:</strong> deepukc2526@gmail.com</span>
              </div>
            </div>
          </aside>
        </div>
      </div>
    );
  }

  if (activeTool === 'subjects') {
    return <SubjectAnalysis onBack={() => setActiveTool('standard')} />;
  }

  return (
    <div className="app-shell">
      <div className="app-nav-header">
        <button className="btn-back-home" onClick={() => setView('landing')}>← Back to Home</button>
        <button className="btn-subject-analysis" onClick={() => setActiveTool('subjects')} type="button">Subject-wise Analysis</button>
        <button className="btn-logout" onClick={handleLogout}>Logout</button>
      </div>
      <div className="hero split-hero">
        <div className="hero-copy">
          <h1>ResultIQ</h1>
          <p className="subtext">Transforming Examination Data into Actionable Insights</p>
        </div>
      </div>

      <div className="instructions-card">
        <h2>📋 Instructions & File Requirements</h2>
        <div className="instructions-grid">
          <div className="inst-group">
            <h3>📊 Student Master Excel Requirements</h3>
            <ul>
              <li><strong>First Row must be the header row</strong> containing column names.</li>
              <li><strong>Mandatory Columns:</strong> <code>USN</code> (register no, registration number) and <code>StudentName</code> (candidate name, name).</li>
              <li><strong>Optional Columns (recommended for demographic reports):</strong> <code>Gender</code> (sex), <code>Category</code> (admission category), <code>Caste</code>, and <code>Religion</code>.</li>
              <li>Ensure there are no blank USN or Student Name cells in your data rows.</li>
            </ul>
            <div className="inst-example-table-wrapper">
              <table className="inst-example-table">
                <thead>
                  <tr>
                    <th>USN</th>
                    <th>StudentName</th>
                    <th>Gender</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>1SI21CA001</td>
                    <td>John Doe</td>
                    <td>Male</td>
                    <td>GM</td>
                  </tr>
                  <tr>
                    <td>1SI21CA002</td>
                    <td>Jane Smith</td>
                    <td>Female</td>
                    <td>IIA</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="inst-group">
            <h3>📄 Result Ledger PDF Requirements</h3>
            <ul>
              <li>Upload the official <strong>Bangalore University Semester Result Ledger PDF</strong>.</li>
              <li>The PDF must contain the course details, subject codes, obtained internal/external marks, grades, and SGPA info.</li>
              <li>Ensure the PDF file is readable and not password-protected or corrupted.</li>
              <li>The results in the PDF will be matched with the USNs provided in your Student Master Excel sheet to generate reports.</li>
            </ul>
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
