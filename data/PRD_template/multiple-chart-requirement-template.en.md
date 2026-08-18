# Multiple Chart Requirement Template
> Use this template to define a responsive multi-chart dashboard page with one or more coordinated QDM data sources.  
> Replace the prompts in `[]` with confirmed project information; remove items that are not applicable.

## 1. Basic Document Information

| Field | Value |
| --- | --- |
| Template name | Multiple Chart Requirement Template |
| Document name | D.CHQ.QDM Multiple Chart Requirement |
| System / module | D.CHQ.QDM / Dashboard and chart presentation |
| Business owner | [To be confirmed] |
| Product owner | [To be confirmed] |
| Author | [To be confirmed] |
| Version | V1.0 enhanced draft |
| Status | Draft for review |
| Creation date | [YYYY-MM-DD] |
| Last updated | [YYYY-MM-DD] |
| Target release / sprint | [To be confirmed] |
| Approver | [To be confirmed] |

### 1.1 Version History

| Version | Date | Owner | Change description |
| --- | --- | --- | --- |
| V0.1 | [Date] | Original author | Initial outline with basic multiple-chart page sections. |
| V1.0 | [Date] | [Author] | Enhanced requirement structure, suggested fields, acceptance criteria, and implementation guidance. |

## 2. Background and Objectives

### 2.1 Background

[Describe the current need for a multiple-chart page, involved data sources, business questions, and why one coordinated dashboard view is needed.]

Description: The page shall provide one coordinated view for multiple charts fed by one or more QDM data sources. Users must be able to filter, compare, drill into, and export chart-level insights while the implementation remains lightweight, responsive, and consistent with the AITC enterprise UI style.

### 2.2 Objectives

- Provide a single responsive dashboard page that can display multiple related charts with consistent filters and visual treatment.
- Allow users to compare metrics across time, category, status, organization, or other approved dimensions.
- Support drill-down and cross-filter interactions where chart relationships are defined by the business owner.
- Standardize chart configuration fields so future chart additions can be handled with minimal redevelopment.
- Define acceptance criteria for layout, performance, accessibility, data accuracy, and browser compatibility.

## 3. Scope

| Area | In scope | Out of scope / notes |
| --- | --- | --- |
| Page layout | Dashboard container, query condition area, multi-chart display area, detail/axis description area. | Global navigation and unrelated page redesigns are out of scope unless separately approved. |
| Charts | Line, bar, stacked bar, pie/donut, KPI card, heatmap, and table-backed detail views where required. | Advanced custom visualization libraries should be avoided unless approved. |
| Interactions | Filter, reset, refresh, drill-down, tab switch, hover tooltip, legend toggle, export, and empty/error states. | Real-time collaboration and user-authored chart creation are not included in this phase. |
| Data | Approved QDM tables/views/APIs and defined field mapping rules. | New upstream data pipeline development is out of scope unless required. |
| Delivery | Responsive HTML + Bootstrap + JavaScript/jQuery implementation with clean comments and maintainable structure. | Complex plug-in frameworks or heavy charting dependencies require architecture review. |

## 4. Responsible Parties and Stakeholders

| Role | Name | Responsibility | Required sign-off |
| --- | --- | --- | --- |
| Business owner | [To be confirmed] | Confirms business purpose, priority, KPIs, and acceptance of chart meaning. | Yes |
| Product owner / BA | [To be confirmed] | Maintains requirements, resolves scope questions, coordinates review. | Yes |
| Data owner | [To be confirmed] | Confirms source tables, field definitions, refresh cadence, and data quality rules. | Yes |
| UI/UX reviewer | [To be confirmed] | Checks AITC visual consistency, layout behavior, and responsive experience. | Recommended |
| Frontend developer | [To be confirmed] | Implements dashboard, chart components, interactions, and responsive behavior. | No |
| QA tester | [To be confirmed] | Executes functional, data, compatibility, accessibility, and regression tests. | Yes |
| Security / compliance | [To be confirmed] | Reviews access control, export restrictions, and sensitive data exposure. | As needed |

## 5. Data Description and Data Contract

### 5.1 Data Sources

| Source ID | Table / view / API | Business description | Data grain | Refresh cadence | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | XXX_Table | Primary dataset used by the main chart group. | [To be confirmed] | [To be confirmed] | [To be confirmed] |
| DS-02 | XXX_Table2 | Supporting dataset used for comparison or detail charts. | [To be confirmed] | [To be confirmed] | [To be confirmed] |
| DS-03 | Optional additional source | Use only if a required metric cannot be derived from DS-01 or DS-02. | [To be confirmed] | [To be confirmed] | [To be confirmed] |

### 5.2 Required Data Fields

| Field name | Source | Type | Required | Business definition / logic |
| --- | --- | --- | --- | --- |
| XXX_Field | XXX_Table | [To be confirmed] | Yes | Primary measure or dimension used by one or more charts. |
| XXX_Field2 | XXX_Table2 | [To be confirmed] | Yes | Supporting field used for comparison, segmentation, or tooltip detail. |
| Date / period | All applicable sources | Date / period | Recommended | Required when trend, period comparison, or date filtering is needed. |
| Organization / entity | All applicable sources | String / code | Recommended | Required for filtering or comparison by unit, department, site, customer, or similar entity. |
| Status / category | All applicable sources | String / code | Recommended | Required for grouped charts, stacked bars, legends, and status counts. |
| Measure value | Calculated or source field | Number | Recommended | Numeric value used for KPI, axis, tooltip, and aggregation logic. |

### 5.3 Field Logic and Data Rules

- Define the join key and relationship between each data source before development starts.
- Specify whether each chart uses raw records, aggregated records, or pre-calculated metrics.
- Document all formulas, filters, exclusions, null handling, and rounding rules in the chart inventory table.
- When two charts use the same metric, they must use the same calculation logic unless an exception is documented.
- All visible labels, units, and legends must match approved business terminology.

## 6. Page / Function Layout

The page should use one layout pattern selected by business priority, data density, and screen size. The recommended default is Primary-Detail / Hero Layout for analytic pages, with Uniform Grid as the fallback for monitoring-style dashboards.

| Layout option | Description | Best use case | Recommendation |
| --- | --- | --- | --- |
| Uniform Grid | All chart containers use the same size and align in a consistent grid. | Monitoring dashboards and peer-level KPI comparison. | Use when all charts have equal importance. |
| Primary-Detail / Hero | One large hero chart occupies the primary area, with supporting charts beside or below it. | Detailed analysis pages with one dominant trend or business question. | Recommended default unless business owner confirms otherwise. |
| Nested / Drill-down | Selecting one chart updates or filters another chart. | Exploratory analysis and cohort/category drill-down. | Use only when chart relationships are clearly defined. |
| Tabbed | Multiple related charts share one container and are switched by tabs. | High data homogeneity such as Day / Week / Month views. | Use to save space, but avoid hiding critical charts. |
| Masonry / Waterfall | Cards share width but vary in height based on content. | Mixed media reports or mobile-first feeds. | Not recommended for core operational dashboards because it can reduce comparability. |

## 7. Page / Function Presentation

| Field | Requirement |
| --- | --- |
| Page name | Multiple Chart Dashboard - exact menu label to be confirmed |
| Page purpose | Display multiple QDM metrics in one coordinated, filterable, and exportable view. |
| Top area | Query conditions: date range, organization/entity, category/status, data source, and role-specific filters. |
| Middle area | Chart display area with selected layout pattern, chart title, legends, tooltip behavior, and loading/empty/error states. |
| Bottom area | Data detail, axis description, metric definitions, last refresh time, and optional source notes. |
| Diagram / illustration | Insert final approved wireframe or screenshot after UX review. Until then, use chart inventory and layout rules as the build reference. |

## 8. Chart Inventory and Configuration

### 8.1 Chart Inventory

| Chart ID | Chart name | Type | Primary metric | Dimension / grouping | Data source | Interaction |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Overall Trend | Line / area | [To be confirmed] | Date / period | DS-01 | Hover tooltip; click filters detail table |
| CH-02 | Composition | Pie / donut | [To be confirmed] | Status / category | DS-01 or DS-02 | Legend toggle; click filters related charts |
| CH-03 | Comparison by Entity | Bar / stacked bar | [To be confirmed] | Organization / entity | DS-01 | Sort; hover tooltip; export data |
| CH-04 | Detail Table | Table | Underlying records or aggregated detail | Selected filters | DS-01 + DS-02 | Pagination; sort; export |

### 8.2 Chart Configuration Fields

| Configuration field | Required? | Guidance |
| --- | --- | --- |
| Chart title | Yes | Use concise business wording; avoid technical table names in user-facing titles. |
| X-axis / Y-axis | Yes for axis charts | Define labels, units, sorting, date granularity, and min/max behavior. |
| Legend | As needed | Define display order, color mapping, and behavior when series are hidden. |
| Tooltip | Yes | Show metric value, unit, period/category, and calculation notes when useful. |
| Empty state | Yes | Display a clear message when filters return no data; do not show a broken chart. |
| Loading state | Yes | Show lightweight loading indicator or skeleton state while data is retrieved. |
| Error state | Yes | Show user-friendly message and log technical details for troubleshooting. |
| Export behavior | Recommended | Define whether image, CSV, or detail-table export is allowed by role. |

## 9. Query Conditions and User Interactions

### 9.1 Filters

| Filter | Control type | Default value | Applies to | Notes |
| --- | --- | --- | --- | --- |
| Date range / period | Date picker or segmented period selector | Latest available period | All charts unless excluded | Required for trend and comparison views. |
| Organization / entity | Dropdown / searchable select | User default scope | All applicable charts | Respect user permission scope. |
| Category / status | Dropdown / multi-select | All | Category, status, composition charts | Use approved business labels. |
| Data source | Dropdown / hidden parameter | Primary source | Source-specific charts | Show only if users need to switch sources. |
| Reset | Button | N/A | Entire page | Restores approved default filter state. |

### 9.2 Interaction Rules

- Filter changes shall update all affected charts without requiring a full page reload when technically feasible.
- A selected chart segment should visually indicate active state and make the active filter visible to the user.
- Tooltips shall be readable on desktop and replaced by tap-friendly detail behavior on touch devices where needed.
- Chart legends must be keyboard reachable if they are interactive.
- Export actions must follow data permission rules and include the applied filter context where practical.

## 10. UI and Visual Design Requirements

The implementation shall follow the AITC enterprise UI style: clean, operational, trustworthy, dense but readable, and built around neutral surfaces with blue as the primary action color.

| UI area | Requirement |
| --- | --- |
| Color system | Use background #f6f8fb / #f3f5f7, panels #ffffff, primary blue #2563eb, hover #1d4ed8, border #d9e1e7, and text #111315 / #17202a. Do not introduce green or purple as primary brand colors. |
| Typography | Use Arial Nova if available, then Plus Jakarta Sans, Arial, and Chinese fallback fonts. Avoid overly heavy weights and negative letter spacing. |
| Spacing and radius | Use an 8px spacing rhythm, 8px general radius, and 6px compact radius for dense controls. |
| Cards / panels | Use white chart panels with clear titles, consistent padding, and soft elevation only when needed. |
| Responsive layout | Desktop should prioritize comparison; tablet should keep chart readability; mobile should stack charts vertically with horizontal scroll only for real tables. |
| States | Define loading, empty, error, disabled, active, hover, focus, and selected states for filters and charts. |

## 11. Technical Specifications

| Category | Requirement |
| --- | --- |
| Frontend stack | HTML + Bootstrap + JavaScript/jQuery. Code should be clean, structured, commented where helpful, and easy for secondary development. |
| Chart library | Use an approved lightweight charting library or existing project standard. Avoid complex plugins unless approved by architecture review. |
| Responsiveness | Support desktop, tablet, and mobile breakpoints. Use native responsive grids and avoid fixed widths that cause overflow. |
| Performance | Initial page should render shell quickly; charts should load asynchronously where possible. Target chart refresh within 3 seconds for normal data volume, subject to API performance. |
| Browser support | Support current enterprise-approved Chrome and Edge versions. Additional browser requirements to be confirmed. |
| Maintainability | Separate data mapping, chart configuration, and rendering logic so new charts can be added by configuration where practical. |
| Security | Respect role-based data access. Prevent unauthorized export of restricted data and avoid exposing sensitive raw fields in client code. |

## 12. Non-Functional Requirements

| Requirement type | Target / rule | Validation method |
| --- | --- | --- |
| Data accuracy | Displayed values must match approved source query results for the same filters. | QA compares sample outputs against source query or validated report. |
| Performance | Normal filter or chart refresh should complete within agreed SLA, target 3 seconds under standard data volume. | Browser timing and API log review. |
| Accessibility | Keyboard reachable controls, visible focus state, sufficient contrast, and non-color-only status communication. | Manual keyboard test and contrast review. |
| Reliability | Failures in one chart should not break the full page; show chart-level error state. | Simulated API failure test. |
| Compatibility | Layout must remain readable across approved desktop, tablet, and mobile widths. | Responsive browser verification. |
| Auditability | Last refresh time and applied filter context should be visible or available in export metadata where practical. | Functional test and export inspection. |

## 13. Acceptance Criteria

- Business owner confirms chart list, metric definitions, filter list, default view, and layout pattern.
- Data owner confirms source tables/views/APIs, field mapping, refresh cadence, join logic, and calculation rules.
- All charts render correctly for default filters and at least three representative filter combinations.
- Loading, empty, error, active, hover, focus, and disabled states are implemented and visually consistent.
- The page is responsive on desktop, tablet, and mobile widths with no clipped text, overlapping controls, or unreadable chart labels.
- Export behavior follows approved data permission rules and includes applied filter context where applicable.
- QA verifies data accuracy against source queries or an approved reference report.
- The final page follows the approved color system and does not introduce unapproved primary colors or heavy decorative styling.

## 14. Open Questions and Decisions Needed

| ID | Question / decision | Owner | Target date | Status |
| --- | --- | --- | --- | --- |
| Q-01 | Which layout option is the approved default: Primary-Detail / Hero, Uniform Grid, Tabbed, or another pattern? | Business owner / Product owner | [To be confirmed] | Open |
| Q-02 | What are the final source tables/views/APIs and join keys? | Data owner | [To be confirmed] | Open |
| Q-03 | Which charts are mandatory for first release and which are optional? | Business owner | [To be confirmed] | Open |
| Q-04 | Which roles may export chart images or underlying data? | Security / Business owner | [To be confirmed] | Open |
| Q-05 | What is the approved refresh cadence and SLA for data availability? | Data owner | [To be confirmed] | Open |

## 15. Suggested Additional Requirement Fields

| Field group | Suggested fields | Why it matters |
| --- | --- | --- |
| Document governance | Owner, approver, version history, status, target release, change log | Clarifies accountability and prevents uncontrolled requirement drift. |
| Business definition | Persona, business goal, KPI definition, success metric, priority | Ensures charts answer a real business question and can be accepted objectively. |
| Data contract | Source, field type, grain, refresh cadence, join key, null handling, calculation formula | Prevents mismatched numbers and rework during QA. |
| Chart configuration | Chart type, metric, dimension, axis labels, legend, tooltip, sorting, default filters | Allows development to configure charts consistently and add future charts faster. |
| Interaction design | Drill-down, cross-filtering, tab behavior, export, reset, active state, error state | Defines how users actually operate the dashboard, not only how it looks. |
| Quality and release | Acceptance criteria, test cases, browser support, accessibility, performance target, sign-off | Makes the release measurable and reviewable. |
