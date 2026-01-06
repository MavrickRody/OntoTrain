# Quick Wins Features - OntoTrain Chat UI

This document describes the recently added "Quick Wins" enhancements to the OntoTrain Chat UI.

## Overview

Four major UX improvements have been added to enhance productivity and user experience:

1. **Dark/Light Theme Toggle**
2. **Keyboard Shortcuts**
3. **Search/Filter Insights**
4. **PDF Report Export**

---

## 1. Dark/Light Theme Toggle 🎨

### Description
Switch between light and dark themes for comfortable viewing in different lighting conditions.

### Location
- **Sidebar** → **Appearance** section (top of sidebar)

### Usage
- Click **☀️ Light** button for light theme
- Click **🌙 Dark** button for dark theme
- Current theme button is disabled to show active state

### Theme Features
**Light Theme:**
- Clean white background
- Blue accents (#1f77b4)
- High contrast for daylight viewing

**Dark Theme:**
- Dark gray backgrounds (#2b2b2b)
- Royal blue accents (#6495ed)
- Reduced eye strain for low-light environments

---

## 2. Keyboard Shortcuts ⌨️

### Description
Boost productivity with keyboard shortcuts for common actions.

### Available Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + K` | Focus Input | Jump to query input field |
| `Ctrl/Cmd + Enter` | Submit Query | Execute the current query |
| `Ctrl/Cmd + /` | Show Templates | Open query templates panel |

### Usage
1. View shortcuts by expanding the **⌨️ Keyboard Shortcuts** section at the top of the chat interface
2. Use shortcuts anywhere in the application (works across all pages)
3. Shortcuts work on both Windows/Linux (Ctrl) and Mac (Cmd)

### Benefits
- Faster navigation
- Reduced mouse usage
- Improved workflow efficiency
- Familiar key bindings

---

## 3. Search & Filter Insights 🔍

### Description
Quickly find specific insights from the autonomous agent's analysis using search and filter capabilities.

### Location
- **Sidebar** → **Agent Insights** section

### Features

#### Search
- **Input Field**: "🔍 Search Insights"
- **Searches**: Insight content and source metadata
- **Case-insensitive**: Matches regardless of letter case
- **Real-time**: Updates as you type

#### Filter
- **Dropdown**: "🎯 Filter by Type"
- **Options**:
  - All (no filter)
  - Statistics
  - Patterns
  - Validation
  - Hierarchies
  - Clusters
- **Purpose**: Narrow down insights by category/source

### Usage
1. Load a dataset and run the agent to generate insights
2. Navigate to **Agent Insights** in sidebar
3. Enter search terms in the **Search Insights** field
4. Select a filter type from the **Filter by Type** dropdown
5. Click **📋 View Filtered Insights** to see results

### Example Searches
- Search: `"triple"` → Find all insights mentioning triples
- Search: `"class"` + Filter: `Statistics` → Find class-related statistics
- Search: `"pattern"` → Find pattern discoveries
- Filter: `Validation` → See only validation results

### Results Display
- Shows count: "Showing X of Y insights"
- Expandable cards with full insight details
- Preserves all metadata (source, iteration, timestamp)

---

## 4. PDF Report Export 📕

### Description
Export agent reports and insights to professional PDF documents for sharing and archiving.

### Location
- **Sidebar** → **Export** section
- Button: **📕 Export Report to PDF**

### Requirements
- `reportlab` library (automatically installed with requirements.txt)
- At least one dataset loaded
- Agent insights generated (run agent first)

### PDF Contents

#### 1. Header
- Title: "OntoTrain - Agent Report"
- Generation timestamp
- Dataset name

#### 2. Dataset Statistics Table
- Total Triples
- Total Classes  
- Total Properties
- Professionally formatted table with headers

#### 3. Agent Insights
- Numbered insights (Insight #1, #2, etc.)
- Source information
- Full insight text (truncated to 500 chars for readability)
- Proper spacing and formatting

### Features
- **Professional Layout**: Letter-sized pages with proper margins
- **Styled Content**: Headers, tables, and paragraphs with appropriate styling
- **Color Accents**: Blue headers matching OntoTrain brand
- **Download Button**: Immediate download after generation
- **Timestamped Filenames**: `ontotrain_report_YYYYMMDD_HHMMSS.pdf`

### Usage
1. Load dataset and run agent to generate insights
2. Navigate to **Export** section in sidebar
3. Click **📕 Export Report to PDF**
4. Wait for generation (usually <5 seconds)
5. Click **📥 Download PDF Report** button
6. PDF saves to your downloads folder

### Use Cases
- Share analysis results with team members
- Archive exploration sessions
- Create documentation for knowledge graphs
- Generate reports for stakeholders
- Offline reference material

### Error Handling
- Shows warning if reportlab not installed
- Alerts if no insights available
- Displays specific error messages for troubleshooting

---

## Installation

All Quick Wins features are included in the standard installation:

```bash
# Install dependencies (includes reportlab for PDF export)
pip install -r requirements.txt

# Launch the Chat UI
streamlit run app.py
```

---

## Tips & Tricks

### Theme Selection
- Use dark theme for evening work sessions
- Switch to light theme for screenshots/presentations
- Theme persists during session

### Keyboard Shortcuts
- Memorize `Ctrl+K` and `Ctrl+Enter` for fastest workflow
- Use `Ctrl+/` when you forget SPARQL syntax

### Search & Filter
- Combine search + filter for precise results
- Use quotes for exact phrase matching
- Clear search to see all insights again

### PDF Export
- Run agent before exporting for best reports
- PDFs include timestamp for versioning
- Share PDFs with non-technical stakeholders

---

## Future Enhancements

Potential additions based on user feedback:
- Custom theme colors
- More keyboard shortcuts
- Export to Excel/CSV
- Advanced filters (date range, confidence score)
- Batch PDF generation

---

## Troubleshooting

### Theme not changing
- Refresh the page (Ctrl+R)
- Check browser console for errors

### Keyboard shortcuts not working
- Ensure input field doesn't have focus for non-input shortcuts
- Try refreshing the page
- Check browser compatibility (modern browsers required)

### Search not finding results
- Check spelling
- Try fewer search terms
- Ensure insights exist (run agent first)

### PDF export fails
- Verify reportlab is installed: `pip list | grep reportlab`
- Check that agent has generated insights
- Ensure write permissions in data/ directory

---

## Technical Implementation

### Files Modified
- `app.py`: Main application with all Quick Wins features
- `requirements.txt`: Added reportlab dependency

### New Methods
- `get_theme_css(theme)`: Dynamic CSS generation for themes
- `export_report_to_pdf()`: PDF generation using reportlab
- `filter_insights(insights, search, filter_type)`: Search/filter logic

### Session State Variables
- `theme`: Current theme ('light' or 'dark')
- `insight_search`: Current search term
- `insight_filter`: Selected filter type

---

## Feedback

For issues, suggestions, or feature requests related to Quick Wins features:
- Open an issue on GitHub
- Contact the development team
- Submit a pull request with improvements

---

**Version**: 1.0  
**Last Updated**: 2026-01-06  
**Author**: GitHub Copilot
