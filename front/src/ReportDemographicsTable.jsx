import React from 'react';

const CATEGORIES = ['General', 'EWS', 'SC', 'ST', 'OBC', 'TOTAL'];
const SUBHEADERS = ['Male', 'Female', 'Trans Gender'];
const SECTIONS = [
  { key: 'appeared', title: 'Total Number of Students Appeared' },
  { key: 'passed', title: 'Total Number of Students Passed/Awarded Degree' },
  { key: 'passed_60', title: 'Out of Total, Number of Students Passed with 60% or above' },
];
const ROW_KEYS = ['Total', 'PWD', 'MM', 'OM'];

function formatNumber(value) {
  if (value === null || value === undefined || value === '') {
    return '';
  }
  return Number(value).toString();
}

function getCellValue(demographicsData, sectionKey, rowKey, category, gender) {
  return formatNumber(demographicsData?.[sectionKey]?.rows?.[rowKey]?.[category]?.[gender]);
}

function getSpecialValue(demographicsData, sectionKey, rowKey, specialKey) {
  return formatNumber(demographicsData?.[sectionKey]?.row_totals?.[rowKey]?.[specialKey]);
}

export default function ReportDemographicsTable({ demographicsData, program }) {
  const disciplineLabel = program || 'Program';

  return (
    <div className="report-demographics-wrapper">
      <div className="report-demographics-title">IV. Performance Analysis by Demographics</div>
      <div className="report-demographics-table-wrapper">
        <table className="report-demographics-table">
          <thead>
            <tr>
              <th rowSpan={3} className="vertical-header vertical-sno">S. NO</th>
              <th rowSpan={3} className="vertical-header vertical-discipline">Discipline</th>
              <th rowSpan={3} className="vertical-header vertical-category">Category</th>
              {CATEGORIES.map((category) => (
                <th key={category} colSpan={3}>{category}</th>
              ))}
            </tr>
            <tr>
              {CATEGORIES.map((category) => (
                <th key={`${category}-group`} colSpan={3}>{category === 'EWS' ? 'EWS (Out of General)' : category}</th>
              ))}
            </tr>
            <tr>
              {CATEGORIES.map((category) => (
                SUBHEADERS.map((sub) => (
                  <th key={`${category}-${sub}`} className="subheader-cell">{sub}</th>
                ))
              ))}
            </tr>
          </thead>
          <tbody>
            {SECTIONS.map((section, sectionIndex) => (
              <React.Fragment key={section.key}>
                <tr className="report-demographics-section-title-row">
                  <td colSpan={3 + CATEGORIES.length * 3} className="section-title-cell">{section.title}</td>
                </tr>
                {ROW_KEYS.map((rowKey, rowIndex) => (
                  <tr key={`${section.key}-${rowKey}`}>
                    <td className="row-index-cell">{rowIndex + 1}</td>
                    <td className="discipline-cell">{disciplineLabel}</td>
                    <td className="category-cell">{rowKey}</td>
                    {CATEGORIES.map((category) => (
                      ['M', 'F', 'TG'].map((gender) => (
                        <td key={`${section.key}-${rowKey}-${category}-${gender}`} className="number-cell">
                          {category === 'TOTAL' ? getSpecialValue(demographicsData, section.key, rowKey, gender) : getCellValue(demographicsData, section.key, rowKey, category, gender)}
                        </td>
                      ))
                    ))}
                  </tr>
                ))}
              </React.Fragment>
            ))}
            <tr className="report-demographics-footer-row">
              <td colSpan={3 + CATEGORIES.length * 3} className="report-demographics-footer-text">
                *PBD – Persons with Benchmark Disabilities (Out of Total), MM – Muslim Minority (Out of Total), OM – Other Minority (Out of Total)
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
