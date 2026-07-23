import React from 'react';
import mentorPhoto from './assets/dR..jpg';
import aboutPhoto from './assets/aboutPhoto.jpeg';

export default function LandingPage({ onGetStarted }) {
  // Smooth scroll handler
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="landing-container">
      {/* Sticky Navigation Bar */}
      <nav className="landing-navbar">
        <div className="nav-logo" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          <span className="logo-icon">🎓</span>
          <span className="logo-text">Result<span className="text-highlight">IQ</span></span>
        </div>
        <div className="nav-links">
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>Home</button>
          <button onClick={() => scrollToSection('features')}>Features</button>
          <button onClick={() => scrollToSection('about')}>About</button>
          <button onClick={() => scrollToSection('developer')}>Developer</button>
          <button onClick={() => scrollToSection('mentor')}>Mentor</button>
        </div>
        <button className="nav-btn-primary" onClick={onGetStarted}>Get Started</button>
      </nav>

      {/* Hero Section */}
      <header className="hero-section">
        <div className="hero-content">
          <div className="badge">✨ Version 1.0 Release</div>
          <h1 className="hero-title">
            Intelligent University <br />
            <span className="text-gradient">Result Analysis & Report Generation</span>
          </h1>
          <p className="hero-subtitle">
            Automate Bangalore University result analysis in minutes. Upload the University Result Ledger and Student Master Data to instantly generate comprehensive analytics, institutional statistics, and professionally formatted result analysis reports.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={onGetStarted}>
              Get Started <span className="arrow">→</span>
            </button>
            <button className="btn-secondary" onClick={() => scrollToSection('features')}>
              Learn More
            </button>
          </div>
          <div className="features-checklist">
            <span>✓ Automated PDF Result Extraction</span>
            <span>✓ Student Data Integration</span>
            <span>✓ Instant Result Analytics</span>
            <span>✓ Subject-wise Performance Analysis</span>
            <span>✓ Demographic & Category Reports</span>
            <span>✓ Topper Identification</span>
            <span>✓ Pass Percentage Calculation</span>
            <span>✓ Professional Word Report Generation</span>
          </div>
        </div>
        <div className="hero-visual">
          <div className="glass-card main-preview">
            <div className="card-header">
              <span className="dot red"></span>
              <span className="dot yellow"></span>
              <span className="dot green"></span>
              <span className="window-title">result_analysis_report.docx</span>
            </div>
            <div className="card-body">
              <div className="document-mock">
                <div className="doc-header">
                  <div className="doc-logo-placeholder">🏫</div>
                  <div className="doc-header-text">
                    <div className="line-lg"></div>
                    <div className="line-md"></div>
                    <div className="line-sm"></div>
                  </div>
                </div>
                <div className="doc-content-mock">
                  <div className="doc-title-placeholder"></div>
                  <div className="doc-table-placeholder">
                    <div className="table-header-mock"></div>
                    <div className="table-row-mock"></div>
                    <div className="table-row-mock"></div>
                    <div className="table-row-mock"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="glass-card stat-badge-preview float-1">
            <span className="stat-icon">📊</span>
            <div className="stat-desc">
              <h4>Pass Rate</h4>
              <p>94.2% Calculated</p>
            </div>
          </div>
          <div className="glass-card stat-badge-preview float-2">
            <span className="stat-icon">⚡</span>
            <div className="stat-desc">
              <h4>Processing</h4>
              <p>&lt; 2 Minutes</p>
            </div>
          </div>
        </div>
      </header>

      {/* Statistics Section */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <h3>100%</h3>
            <p>Automated Report Generation</p>
          </div>
          <div className="stat-card">
            <h3>90%</h3>
            <p>Manual Work Reduced</p>
          </div>
          <div className="stat-card">
            <h3>&lt; 2 Min</h3>
            <p>Processing Time</p>
          </div>
          <div className="stat-card">
            <h3>Word / PDF</h3>
            <p>Professional Format</p>
          </div>
        </div>
      </section>

      {/* Why ResultIQ Section */}
      <section id="features" className="why-section">
        <div className="section-header">
          <h2 className="section-title">Why ResultIQ?</h2>
          <p className="section-subtitle">Designed to turn complex university ledgers into beautiful institutional insights.</p>
        </div>
        <div className="why-grid">
          <div className="why-card">
            <div className="card-icon-wrapper">🔍</div>
            <h3>Intelligent Parsing</h3>
            <p>Extracts student marks directly from Bangalore University Result Ledger PDFs with high accuracy, eliminating manual typing.</p>
          </div>
          <div className="why-card">
            <div className="card-icon-wrapper">🧠</div>
            <h3>Smart Analysis</h3>
            <p>Automatically computes pass percentage, distinction, first class, second class, fail statistics, toppers, subject performance, and demographic insights.</p>
          </div>
          <div className="why-card">
            <div className="card-icon-wrapper">📝</div>
            <h3>Professional Reports</h3>
            <p>Generates institution-ready Microsoft Word reports following the official university result analysis format.</p>
          </div>
          <div className="why-card">
            <div className="card-icon-wrapper">✨</div>
            <h3>Easy to Use</h3>
            <p>Simple upload workflow requiring only the University Ledger PDF and Student Master Excel file.</p>
          </div>
        </div>
      </section>



      {/* Key Features Details Section */}
      <section className="features-detail-section">
        <div className="section-header">
          <h2 className="section-title">Key Capabilities</h2>
          <p className="section-subtitle">A closer look at how ResultIQ automates your result reporting requirements.</p>
        </div>
        <div className="features-detail-grid">
          <div className="detail-card">
            <h4>📄 PDF Result Extraction</h4>
            <p>Automatically extracts:</p>
            <ul>
              <li>Student Name & USN</li>
              <li>Subject Codes & Names</li>
              <li>Internal/External Marks</li>
              <li>Grades & Result Status</li>
            </ul>
          </div>
          <div className="detail-card">
            <h4>📊 Student Info Integration</h4>
            <p>Matches and maps:</p>
            <ul>
              <li>USN as primary identifier</li>
              <li>Student Gender (M / F / TG)</li>
              <li>Student Admission Category</li>
              <li>Caste and Social Groupings</li>
            </ul>
          </div>
          <div className="detail-card">
            <h4>📈 Advanced Analytics</h4>
            <p>Generates detailed statistics:</p>
            <ul>
              <li>Overall Summary & Pass percentage</li>
              <li>Subject Wise Pass/Fail Counts</li>
              <li>Top Performers list</li>
              <li>Gender & Category demographics</li>
            </ul>
          </div>
          <div className="detail-card">
            <h4>📥 Professional Export</h4>
            <p>Produces formatted outputs:</p>
            <ul>
              <li>Clean, landscape A4 Word file</li>
              <li>Horizontally centered tables</li>
              <li>Dynamic logo and header sizing</li>
              <li>Proper signature blocks</li>
            </ul>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <div className="about-wrapper">
          <div className="about-content">
            <div className="badge">ABOUT PRODUCT</div>
            <h2>Making Academic Result Analysis Smarter</h2>
            <p>
              ResultIQ was developed to simplify and automate the labor-intensive process of university result analysis performed by educational institutions. Traditionally, preparing semester result reports requires hours of manual data entry, calculations, and formatting.
            </p>
            <p>
              ResultIQ transforms this process into an automated workflow by combining intelligent PDF parsing, structured data integration, statistical analysis, and document generation.
            </p>
            <p>
              The software significantly reduces manual effort while improving consistency, accuracy, and reporting efficiency.
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="about-visual-card">
              <img className="about-photo" src={aboutPhoto} alt="ResultIQ About Photo" />
            </div>
            <p style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#aebdd8', opacity: 0.85, textAlign: 'center', fontStyle: 'italic', lineHeight: '1.4' }}>
              Special thanks to faculty members and student coordinators for their continuous support and testing.
            </p>
          </div>
        </div>
      </section>

      {/* Developer Section */}
      <section id="developer" className="developer-section">
        <div className="section-header">
          <h2 className="section-title">Meet the Developer</h2>
          <p className="section-subtitle">The mind behind the design and implementation of ResultIQ.</p>
        </div>
        <div className="developer-card-wrapper">
          <div className="developer-card">
            <div className="developer-avatar-wrapper">
              <div className="avatar-placeholder">DK</div>
            </div>
            <div className="developer-info">
              <h3>Deepu K C</h3>
              <p className="title">Full Stack Developer</p>
              <p className="edu">Bengaluru</p>
              <div className="developer-statement">
                <p style={{ marginBottom: '1rem' }}>
                  ResultIQ was independently designed and developed as a full-stack academic automation solution with the objective of modernizing institutional result analysis. The application integrates intelligent data extraction, analytical processing, and automated document generation into a single workflow using modern web technologies.
                </p>
                <p>
                  Deepu K C is a Full Stack Developer from Bengaluru with a passion for building practical software solutions that solve real-world problems. He specializes in modern web technologies and develops scalable applications with a strong focus on automation, user experience, and performance. ResultIQ reflects his commitment to simplifying academic processes through intelligent data analysis and report generation, helping educational institutions save time and improve efficiency.
                </p>
              </div>
              <div className="social-links">
                <a href="https://github.com/Deepu325" target="_blank" rel="noreferrer" title="GitHub">
                  <span className="social-icon">🐙 GitHub</span>
                </a>
                <a href="https://linkedin.com/in/deepu-kc-03kc02/?skipRedirect=true" target="_blank" rel="noreferrer" title="LinkedIn">
                  <span className="social-icon">💼 LinkedIn</span>
                </a>
                <a href="https://deepukcportfoliov2.vercel.app/" target="_blank" rel="noreferrer" title="Portfolio">
                  <span className="social-icon">🌐 Portfolio</span>
                </a>
                <a href="mailto:DEEPUKC2526@GMAIL.COM" title="Email">
                  <span className="social-icon">📧 Email</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mentor Section */}
      <section id="mentor" className="mentor-section">
        <div className="section-header">
          <h2 className="section-title">Meet My Mentor</h2>
          <p className="section-subtitle">Sincere gratitude for guidance and mentorship.</p>
        </div>
        <div className="mentor-card-wrapper">
          <div className="mentor-card">
            <div className="mentor-avatar-wrapper">
              <img className="mentor-photo" src={mentorPhoto} alt="Dr. Yatish S J" />
            </div>
            <div className="mentor-info">
              <h3>Dr. Yatish S J</h3>
              <p className="designation">Faculty Mentor | Researcher</p>
              <div className="acknowledgement-text">
                Dr. Yatish S J has been a constant source of guidance and encouragement throughout the development of ResultIQ. His mentorship, technical insights, and constructive feedback helped shape the project into a practical solution for academic result analysis. His support inspired me to approach software development with a focus on innovation, quality, and solving real-world institutional challenges.
              </div>
            </div>
          </div>
        </div>
      </section>



      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="footer-logo">ResultIQ</span>
            <p>Intelligent Result Analysis & Report Generation System</p>
          </div>
          <div className="footer-details">
            <p><strong>Developed by:</strong> Deepu K C</p>
            <p><strong>Special Thanks:</strong> Dr. Yatish S J</p>
            <p><strong>Version:</strong> 1.0 (2026)</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 ResultIQ. Made with ❤️ for Educational Institutions.</p>
        </div>
      </footer>
    </div>
  );
}
