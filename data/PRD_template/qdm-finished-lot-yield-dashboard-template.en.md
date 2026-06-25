# QDM Finished Lot Yield Dashboard Requirement Template

> This template was adapted from `D.CHQ.QDM Yield Dashboard Requirement .docx`.  
> The original embedded images have been replaced by text descriptions so the template can be used in structured requirement discovery and Markdown generation.

## 1. Basic Document Information

| Field | Value |
| --- | --- |
| Template name | QDM Finished Lot Yield Dashboard Requirement Template |
| Document name | D.CHQ.QDM Finish Yield Dashboard Requirement |
| System / Module | FinishedLot |
| Initiating department | QDM |
| Author / requester | Ely Yi |
| Version | V1.0 |
| Creation date | 2026-05-21 |
| Business domain | Manufacturing quality / finished lot yield / QDM dashboard |
| Status | Draft / In review / Approved / In development / Released |
| Target release | [YYYY-MM-DD] |

## 2. Background and Objectives

### 2.1 Background

The dashboard is intended as a high-level view of current key yield metrics for different products in the factory. It should be updated by automated scheduled scripts, with a daily refresh unless the data owner confirms another cadence.

The dashboard must support:

- Overall yield trend and drill-down by segments or products.
- Hierarchical trend analysis of main bins and cumulative bins.
- Pareto analysis based on loss code and loss operation.
- Loss attribution by root cause or responsible department.

### 2.2 Objectives

- See a steeper yield improvement curve.
- Drive production costs down rapidly.
- Increase production output without significant additional cost.
- Recover investment costs sooner.

### 2.3 Success Criteria

- Business and data owners agree on metric definitions, filters, source tables, refresh cadence, and acceptance rules.
- Users can identify the latest finished lot yield, output, loss, and major defect contributors from the first screen.
- Users can drill from yield trend to defect-code loss and responsible department details.
- Displayed dashboard data matches approved source query results under representative filters.

## 3. Page / Function Presentation

### 3.1 Finished Lot Performance Overview Trend

| Item | Requirement |
| --- | --- |
| Page name | Finished Lot Performance Overview Trend |
| Page purpose | Display finished yield by time range and display the latest week output, yield, and NSQM loss. |
| Top area | Use the unified search criteria described in Section 4. |
| Y-axis data area | Main chart displays finished product yield rate by default for each week. The right side displays detailed data for the latest week by default. Users can click left-side data points/bars to switch detailed views. |
| X-axis area | Main chart displays week information by default. Detail chart displays the selected data description. |

Text description replacing original screenshot:

- Page header is `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`.
- Top-right controls include a week selector, for example `W 202621`, and an export/download action.
- Main area contains a large chart titled `Weekly Finished Lot Performance Overview Trend`.
- The chart compares weekly finished lot performance across periods such as `202612` to `202621`.
- The chart combines bar and line visualization: weekly values are shown as bars, and comparison lines show target/output/yield trend context.
- The selected week is visually highlighted, and the chart hint says that clicking a weekly yield bar updates the defect analysis below.
- Right-side KPI cards show the selected week's detail, including Yield / Target, Finished Count, NSQM or NSOM Output, and NSQM or NSOM Loss.
- Example values in the source visual include Yield / Target `96.83%`, target `94.81%`, Finished Count `159 Lots`, output `1,335.57`, and loss `63.55`.
- Confirm whether the final metric label should be `NSQM` or `NSOM`, because the source document uses both-looking labels.

### 3.2 Loss Ratio By Defect Code

| Item | Requirement |
| --- | --- |
| Page name | Loss Ratio By Defect Code |
| Page purpose | Display top 10 to 20 defect loss ratio by defect code and defect-code trend. |
| Top area | Use the unified search criteria described in Section 4. |
| Y-axis data area | Main chart displays the top 10 to 20 defect loss ratio. The right side displays selected defect-code trend and cause-department detail. |
| X-axis area | Main chart displays defect-code information. Detail pie/donut chart displays department information. |

Text description replacing original screenshot:

- Page header remains `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`.
- A horizontal period selector shows weeks such as `202612` to `202621`.
- The defect analysis section is titled `Loss Ratio By Defect Code`.
- Toggle controls allow the user to show or hide `Loss Ratio` and `Core Loss Ratio`.
- Main chart is a ranked horizontal bar chart for the selected period, for example `202621 Top 10 Loss Ratio By Defect Code`.
- Red bars represent total loss ratio and blue bars represent core loss ratio.
- Example defect codes visible in the source visual include `ED25 - Short in inner layer`, `ED21 - High resistance short`, `AP09 - Component tilting`, `BM31 - Base material dent`, `GE01 - Scratches`, `SM94 - Solder mask thickness`, `SM41 - Soldermask discoloration`, `ED55 - Short bridge die region`, and `HO31 - Via not completely filled`.
- The selected defect code drives right-side detail cards.
- Right-side trend chart, for example `ED25 Weekly Overview Trend`, compares core defect loss and defect loss ratio over time.
- Right-side donut chart shows department attribution. Example segments in the source visual include `Etching + AOI 59%`, `Assembly 23%`, `Final Check 11%`, and `Material 7%`, with a center value of `26.26%`.

## 4. Query Conditions and User Interactions

### 4.1 Filters

Text description replacing original filter screenshot:

- The filter area uses a two-row, three-column layout.
- Row 1 contains `Customer`, `Plant`, and `Date Type`.
- Row 2 contains `Lot Type`, `Unit Type`, and `Project Type`.
- All controls are dropdowns with a visible arrow indicator.
- Default values shown in the source visual are `Customer = All selected`, `Plant = All selected`, `Date Type = Weekly`, `Lot Type = HVM`, `Unit Type = NSQM`, and `Project Type = Overall`.

| Filter | Control type | Default value | Applies to |
| --- | --- | --- | --- |
| Customer | Dropdown | All selected | All applicable charts |
| Plant | Dropdown | All selected | All applicable charts |
| Date Type | Dropdown | Weekly | All applicable charts |
| Lot Type | Dropdown | HVM | All applicable charts |
| Unit Type | Dropdown | NSQM | All applicable charts |
| Project Type | Dropdown | Overall | All applicable charts |

### 4.2 Interaction Rules

- Filter changes should update all affected charts without requiring a full page reload when technically feasible.
- A selected chart segment should visually indicate active state and make the active filter visible to the user.
- Tooltips should be readable on desktop and replaced by tap-friendly detail behavior on touch devices where needed.
- Chart legends must be keyboard reachable if they are interactive.
- Export actions must follow data permission rules and include the applied filter context where practical.

## 5. Data Description and Data Contract

### 5.1 Data Sources

| Source ID | Table / View / API | Business description | Data grain | Refresh cadence | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryData_Internal]` | Master data source for calculated finished lot yield. | Weekly / Quarterly / Monthly | Weekly, or confirmed cadence | QDM |
| DS-02 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryDefectData_Internal]` | Supporting dataset for defect-code comparison and detail charts. | Weekly / Quarterly / Monthly | Weekly, or confirmed cadence | QDM |

### 5.2 Required Data Fields

| Field name | Source | Type | Required | Business definition / logic |
| --- | --- | --- | --- | --- |
| `ATSDate` | DS-01 | Date / period | Yes | Required for trend, period comparison, and date filtering. |
| `DateType` | DS-01 | Date / period | Yes | Defines whether the dashboard uses weekly, monthly, or quarterly grain. |
| `LotType` | DS-01 | String / code | Yes | Required when users filter or compare by lot type. |
| `Project Type` | DS-01 | String / code | Yes | Required when users filter or compare by project type. |
| `Yield` | DS-01 | Number / percent | Yes | Key finished yield metric. |
| `Output_NSQM` | DS-01 | Number | Yes | Key output metric. |
| `DefectCode` | DS-02 | String / code | Yes | Required for defect-code ranking and drill-down. |
| `DefectQty` | DS-02 | Number | Yes | Key defect quantity or loss value. |
| `Department` | DS-02 | String / code | Yes | Required for loss attribution by department. |

### 5.3 Data Rules To Confirm

- Confirm whether the dashboard refresh cadence is weekly, daily, or both. The source document mentions daily automation but source tables list weekly cadence.
- Confirm the exact period grain and allowed `DateType` values.
- Confirm whether `Customer`, `Plant`, `LotType`, `UnitType`, and `ProjectType` are stored directly in DS-01/DS-02 or joined from reference tables.
- Confirm whether output and loss metrics use NSQM, lots, units, or multiple unit modes.
- Define null handling, zero denominator behavior, rounding precision, and percent display format.
- Define permission scope for customer, plant, product, and exportable detail data.

## 6. Yield Calculation Logic

### 6.1 Finished Yield Definition

Finished Yield, also called Product Yield, represents the percentage of units that successfully pass through the full manufacturing process and are shipped as finished goods for a specific lot or week. It reflects overall comprehensive yield performance of the production line.

Core calculation logic: the calculation is based on multiplying the Output/Input ratios across all key processes, which means the product of individual process yields.

### 6.2 Formula Text Replacing Original Formula Images

| Formula | Text version |
| --- | --- |
| Lot Product Yield | `Lot Product Yield = (PAOI Output / PAOI Input) x (E-test Output / E-test Input) x (CCAOI Output / CCAOI Input) x (Bump AOI Output / Bump AOI Input) x (FVI Output / FVI Input)` |
| Weekly Product Yield | `Weekly Product Yield = product of each process's weekly shipped output/input ratio`, for example `(Total Weekly Shipped PAOI Output / Total Weekly Shipped PAOI Input) x (Total Weekly Shipped E-test Output / Total Weekly Shipped E-test Input) x ...` |
| Extension rule | If the approved process path includes `Inline`, `Others`, or additional inspection steps, extend the formula by multiplying the corresponding process yield ratios. |

### 6.3 Calculation Steps and Example

The calculation follows the principle: `Output / Input = Process Yield`, then multiply each process yield sequentially.

Example table replacing the original calculation screenshot:

| Process | Input | Output | Losses | Yield |
| --- | ---: | ---: | ---: | ---: |
| PAOI | 50000 | 49700 | 300 | 99.4% |
| E-test | 49700 | 49500 | 200 | 99.5% |
| CCAOI | 49250 | 48900 | 350 | 99.29% |
| Bump | 48600 | 48300 | 300 | 99.38% |
| FVI | 48300 | 47900 | 400 | 99.17% |
| Inline | 49500 | 49250 | 250 | 99.49% |
| Others | 48900 | 48600 | 300 | 99.39% |

Example GTY expression from the source:

`GTY = 99.4% x 99.5% x 99.29% x 99.38% x 99.17% x 99.49% x 99.39%`

## 7. Page / Function Layout

The page should use one layout pattern selected by business priority, data density, and screen size. The recommended default is Primary-Detail / Hero Layout for analytic pages, with Uniform Grid as the fallback for monitoring-style dashboards.

| Layout option | Description | Best use case | Recommendation |
| --- | --- | --- | --- |
| Primary-Detail / Hero | One large hero chart occupies the primary area, with supporting KPI cards and charts beside or below it. | Detailed analysis pages with one dominant trend or business question. | Recommended default unless business owner confirms otherwise. |
| Nested / Drill-down | Selecting one chart updates or filters another chart. | Exploratory analysis and cohort/category drill-down. | Use when chart relationships are clearly defined. |
| Uniform Grid | Charts use consistent card sizes and equal visual priority. | Monitoring-style dashboards with many comparable metrics. | Fallback when no chart is dominant. |

## 8. Chart Inventory and Configuration

Each chart should be specified before development starts.

| Chart ID | Chart name | Type | Primary metric | Dimension / grouping | Data source | Interaction |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Finished Overall Trend | Line + bar combo | Yield / target / output | Weekly / Quarterly / Monthly | DS-01 | Hover tooltip; click weekly bar or point to filter detail table and defect analysis. |
| CH-02 | Defect Loss Ratio | Stacked or grouped horizontal bar | Defect loss ratio / core loss ratio | Top 10 to 20 defect codes | DS-02 | Legend toggle; click defect code to update related trend and department attribution. |
| CH-03 | Right-side detail chart | Table / line / pie or donut | Detail content based on selected left-side data | Current period, selected defect, selected filters | DS-01 + DS-02 | Pagination, sorting, tooltip, selected-state linkage, export. |

## 9. Responsible Parties and Stakeholders

| Role | Name / team | Responsibility | Required sign-off |
| --- | --- | --- | --- |
| Business Owner | Yield team | Confirms business purpose, priority, and acceptance of chart meaning. | Yes |
| Product Owner / BA | QDM | Maintains requirements, resolves scope questions, coordinates review. | Yes |
| Data Owner | Yield team | Confirms source tables, field definitions, refresh cadence, and data quality rules. | Yes |
| UI/UX Reviewer | Yield team | Checks AITC visual consistency, layout behavior, and responsive experience. | Recommended |
| Frontend Developer | QDM | Implements dashboard, chart components, interactions, and responsive behavior. | No |
| QA Tester | Yield team | Executes functional, data, compatibility, accessibility, and regression tests. | Yes |

## 10. UI and Visual Design Requirements

The implementation should follow the AITC enterprise UI style: clean, operational, trustworthy, dense but readable, and built around neutral surfaces with blue as the primary action color.

| UI area | Requirement |
| --- | --- |
| Color system | Use background `#f6f8fb` / `#f3f5f7`, panels `#ffffff`, primary blue `#2563eb`, hover `#1d4ed8`, border `#d9e1e7`, and text `#111315` / `#17202a`. Do not introduce green or purple as primary brand colors. |
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
| Browser support | Support current enterprise-approved Chrome and Edge versions. Additional browser requirements must be confirmed. |
| Maintainability | Separate data mapping, chart configuration, and rendering logic so new charts can be added by configuration where practical. |
| Security | Respect role-based data access. Prevent unauthorized export of restricted data and avoid exposing sensitive raw fields in client code. |

## 12. Non-functional Requirements

| Requirement type | Target / rule | Validation method |
| --- | --- | --- |
| Data accuracy | Displayed values must match approved source query results for the same filters. | QA compares sample outputs against source query or validated report. |
| Performance | Normal filter or chart refresh should complete within agreed SLA, target 3 seconds under standard data volume. | Browser timing and API log review. |
| Accessibility | Keyboard reachable controls, visible focus state, sufficient contrast, and non-color-only status communication. | Manual keyboard test and contrast review. |
| Reliability | Failure in one chart should not break the full page; show chart-level error state. | Simulated API failure test. |
| Compatibility | Layout must remain readable across approved desktop, tablet, and mobile widths. | Responsive browser verification. |
| Auditability | Last refresh time and applied filter context should be visible or available in export metadata where practical. | Functional test and export inspection. |

## 13. Acceptance Criteria

1. Business owner confirms chart list, metric definitions, filter list, default view, and layout pattern.
2. Data owner confirms source tables/views/APIs, field mapping, refresh cadence, join logic, and calculation rules.
3. All charts render correctly for default filters and at least three representative filter combinations.
4. Loading, empty, error, active, hover, focus, and disabled states are implemented and visually consistent.
5. The page is responsive on desktop, tablet, and mobile widths with no clipped text, overlapping controls, or unreadable chart labels.
6. Export behavior follows approved data permission rules and includes applied filter context where applicable.
7. QA verifies data accuracy against source queries or an approved reference report.
8. The final page follows the approved color system and does not introduce unapproved primary colors or heavy decorative styling.

## 14. Open Questions and Decisions Needed

| ID | Question / decision | Owner | Target date | Status |
| --- | --- | --- | --- | --- |
| Q-01 | Which layout option is the approved default: Primary-Detail / Hero, Uniform Grid, Tabbed, or another pattern? | Business Owner / Product Owner | To be confirmed | Open |
| Q-02 | What are the final source tables/views/APIs and join keys? | Data Owner | To be confirmed | Open |
| Q-03 | Which charts are mandatory for first release and which are optional? | Business Owner | To be confirmed | Open |
| Q-04 | Which roles may export chart images or underlying data? | Security / Business Owner | To be confirmed | Open |
| Q-05 | What is the approved refresh cadence and SLA for data availability? | Data Owner | To be confirmed | Open |
| Q-06 | Should the final label be NSQM or NSOM for output/loss KPI cards? | Business Owner / Data Owner | To be confirmed | Open |
| Q-07 | Should the product yield formula include Inline and Others in addition to PAOI, E-test, CCAOI, Bump AOI, and FVI? | Data Owner | To be confirmed | Open |

## 15. Appendix A. Color System

| Token | Value / rule |
| --- | --- |
| Background | `#f6f8fb` / `#f3f5f7` |
| Panel | `#ffffff` |
| Hover Surface | `#eef2f4` |
| Soft Blue Panel | `#f0f6ff` |
| Primary Text | `#111315` |
| KMS Text | `#17202a` |
| Secondary Text | `#424a55` / `#647280` |
| Border | `#d9e1e7` / `rgba(17,19,21,0.17)` |
| Active Border | `rgba(17,19,21,0.28)` |
| Primary Blue | `#2563eb` |
| Primary Hover | `#1d4ed8` |
| Primary Soft Background | `#e8f1ff` |
| Accent Blue | `#60a5fa` |
| Accent Soft Background | `rgba(96,165,250,0.17)` |
| Danger / Error / Warning | `#c2413b` / `#b43636` / `#a56313` |
| Shadow | `0 14px 34px rgba(38, 55, 70, 0.1)`, soft elevation only |
