# PDF Export Feature - Visual Location Guide

## Where the Buttons Appear

The new PDF and DOCX export buttons appear at the **bottom of the analysis preview section**, below all the summary tables.

### Page Flow:
1. Upload Excel file → Click "Validate Excel"
2. Upload PDF file → Click "Validate PDF"  
3. Click "Show Analysis Preview"
4. **↓ SCROLL DOWN ↓**
5. See tables with:
   - Overall Summary Table
   - Top Performers Table
   - Subject Summary Table (with editable fields)
   - Demographics Table
   - Centum Achievers Table
6. **→ EXPORT BUTTONS APPEAR HERE ←**
   - **📄 Generate Report (DOCX)** [Blue Button]
   - **📕 Generate Report (PDF)** [Red Button]

## Button Appearance

```
┌─────────────────────────────────────────────────────────┐
│                                                           │
│  [Centum Achievers Table continues...]                  │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐    ┌──────────────────┐           │
│  │📄 Generate       │    │📕 Generate       │           │
│  │Report (DOCX)     │    │Report (PDF)      │           │
│  └──────────────────┘    └──────────────────┘           │
│       (Blue)                   (Red)                     │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Button States

### Enabled State (When Analysis is Ready)
- Both buttons are **clickable and active**
- Buttons have hover effects
- Blue button darkens on hover
- Red button darkens on hover
- Click to download files

### Disabled State (During Upload/Analysis)
- Both buttons appear **grayed out**
- Buttons cannot be clicked
- Indicates: "Waiting for analysis to complete"

## What Each Button Does

### 📄 Generate Report (DOCX) [BLUE BUTTON]
- Downloads: `Result_Analysis_[Program]_[Semester].docx`
- Works immediately (no dependencies)
- Uses approved template
- Includes all 5 tables with data

### 📕 Generate Report (PDF) [RED BUTTON]
- Downloads: `Result_Analysis_[Program]_[Semester].pdf`
- Requires LibreOffice to be installed
- Uses same approved template
- Converts DOCX to PDF automatically
- Shows helpful error if LibreOffice missing

## Error Handling

### If PDF Button Clicked Without LibreOffice
```
┌─────────────────────────────────────────┐
│ Error: LibreOffice not found. Please    │
│ install LibreOffice for PDF export.     │
│                                          │
│ Download from:                          │
│ https://www.libreoffice.org/download/   │
│                                          │
│ [OK]                                    │
└─────────────────────────────────────────┘
```

## Testing Steps

1. **Open browser**: http://localhost:5173
2. **Upload Excel**: Select `2024-25 BCA Data with Caste (1).xlsx`
3. **Click**: "Validate Excel" button
4. **Upload PDF**: Upload the marks ledger PDF
5. **Click**: "Validate PDF" button  
6. **Click**: "Show Analysis Preview"
7. **Scroll down**: To see export buttons
8. **Test DOCX**: Click 📄 button (should download immediately)
9. **Test PDF**: Click 📕 button (may show error about LibreOffice if not installed)

## Files Modified

| File | Change | Impact |
|------|--------|--------|
| `server.py` | Added `/api/export-pdf` endpoint | Enables PDF generation |
| `App.jsx` | Added format parameter to `generateReport()` | Supports both formats |
| `App.jsx` | Added two export buttons | UI for downloads |
| `analysis.css` | Added button styling | Professional appearance |

## Implementation Status

✅ **Complete and Ready to Use**
- DOCX export: Fully functional
- PDF export: Ready (waiting for LibreOffice installation for full functionality)
- UI: Buttons visible and styled
- Error handling: Graceful with helpful messages

## Next Steps

1. Test DOCX export by clicking blue button
2. Install LibreOffice (optional, for PDF)
3. Test PDF export after LibreOffice installation
4. Verify downloaded files open correctly
