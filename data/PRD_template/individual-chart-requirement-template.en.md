# Individual Chart Requirement Template
> Use this template to define the business need, data contract, chart behavior, development scope, and acceptance criteria for one chart or dashboard component.  
> Replace the prompts in `[]` with confirmed project information; remove items that are not applicable.

## 1. Basic Document Information

| Field | Value / Description |
| --- | --- |
| Template name | Individual Chart Requirement Template |
| Document name | [D.CHQ.QDM Single Chart Requirement] |
| Chart / page name | [Enter chart or page name] |
| Business domain | [CHQ / QDM / KMS / other] |
| Requestor | [Name / team] |
| Business owner | [Name / team responsible for business approval] |
| Product owner / BA | [Name] |
| Technical owner | [Name] |
| Author | [Name] |
| Version | v0.1 Draft |
| Status | Draft / In Review / Approved / In Development / Released |
| Priority | High / Medium / Low |
| Target release / due date | [YYYY-MM-DD] |
| Related system / module | [Application, module, or menu path] |

## 2. Background and Objectives

### 2.1 Background

[Describe the business context, current pain point, decision scenario, and why this chart is required. Include the user group and operational process this chart supports.]

### 2.2 Objectives

- Provide a clear visual summary of [primary metric] by [key dimension / time period].
- Enable users to identify trends, exceptions, and comparison gaps quickly.
- Support drill-down or detail review for the records behind the chart where applicable.
- Standardize chart logic, data source, and UI behavior for development and UAT.

### 2.3 Success Criteria

- Users can understand the chart meaning without manual data reconciliation.
- Displayed values match the agreed source data and calculation rules.
- Filters, sorting, export, and detail behaviors work consistently across supported screen widths.

## 3. Scope

| Area | Description |
| --- | --- |
| In scope | [Chart visualization, query filters, data detail table, export, permission handling, and UAT validation.] |
| Out of scope | [Excluded features such as new upstream data capture, historical backfill, or complex workflow approval.] |
| Assumptions | [Source table availability, refresh timing, user roles, browser support.] |
| Dependencies | [APIs, ETL jobs, data owners, UI assets, platform components.] |
| Constraints | [Performance, security, compliance, layout, or technical limitations.] |

## 4. Responsible Parties and Stakeholders

| Role | Name / Team | Responsibility |
| --- | --- | --- |
| Business owner | [TBD] | Owns business definition, priority, and final approval. |
| Data owner | [TBD] | Confirms data source, field definitions, refresh frequency, and quality rules. |
| Product owner / BA | [TBD] | Maintains requirement scope, acceptance criteria, and change control. |
| UI / UX | [TBD] | Confirms layout, responsiveness, chart readability, and interaction design. |
| Front-end developer | [TBD] | Implements page layout, chart rendering, interaction, and browser behavior. |
| Back-end / data engineer | [TBD] | Provides API, aggregation logic, data security, and performance support. |
| QA / UAT owner | [TBD] | Creates test cases, validates results, and records defects. |
| Approver | [TBD] | Signs off requirement readiness and production release. |

## 5. Data Description

### 5.1 Data Source

| Source / table / API | Owner | Refresh frequency | Data grain | Notes |
| --- | --- | --- | --- | --- |
| XXX_Table | [Data owner] | Real-time / Daily / Weekly / Monthly | [One row per ...] | [Availability, SLA, known limitations] |
| [Additional source if needed] | [Owner] | [Frequency] | [Grain] | [Join key / dependency] |

### 5.2 Key Fields and Business Definitions

| Field name | Business definition | Data type | Required | Source mapping / logic |
| --- | --- | --- | --- | --- |
| XXX_Field_1 | [Define business meaning] | String / Number / Date | Y / N | [Source column or formula] |
| XXX_Field_2 | [Define business meaning] | String / Number / Date | Y / N | [Source column or formula] |
| Dimension field | [Grouping field used on axis, legend, or filter] | String / Date | Y / N | [Mapping / hierarchy rule] |
| Metric field | [Measure displayed in chart] | Number | Y | [Aggregation, rounding, null handling] |
| Status field | [Used for color, status split, or exception flag] | String | N | [Valid values and mapping] |

### 5.3 Calculation and Logic Rules

- Metric formula: [Define numerator, denominator, aggregation method, rounding rule, and unit].
- Filtering logic: [Define included/excluded records before aggregation].
- Date logic: [Define date field, timezone, fiscal calendar, and period boundary].
- Null/blank handling: [Exclude, group as Unknown, or treat as zero].
- Deduplication rule: [Define unique key and duplicate handling if applicable].

## 6. Page and Chart Presentation

### 6.1 Page Layout

| Area | Content / Behavior |
| --- | --- |
| Top: Query condition area | Filters, search controls, reset/apply buttons, and default selection rules. |
| Middle: Chart display area | Single chart with title, legend, axis labels, tooltip, empty/loading/error states. |
| Bottom: Data detail area | Detail table for records behind the chart, including pagination and export if required. |

### 6.2 Chart Specification

| Field | Value / Description |
| --- | --- |
| Chart type | Line / Bar / Pie / Donut / Combo / KPI / Other |
| Primary metric | [Metric name and unit] |
| X-axis / category | [Dimension, period, or category] |
| Y-axis / value | [Metric and unit] |
| Legend / series | [Series grouping field, if any] |
| Sort order | Ascending / Descending / Custom business order |
| Default time range | [Current month / Last 12 months / other] |
| Tooltip content | [Metric value, percentage, dimension, period, source note] |
| Drill-down behavior | None / Open detail table / Navigate to page / Show modal |
| Empty state | [Message when no data is returned] |
| Loading / error state | [Spinner, retry message, fallback text] |

### 6.3 Query Conditions and Filters

| Filter field | Control type | Default value | Required | Dependency / notes |
| --- | --- | --- | --- | --- |
| Date range | Date picker | Current period | Y / N | Timezone, max range, fiscal period rule |
| Organization / region | Single / multi-select | User scope / All | Y / N | Permission-based options |
| Status | Dropdown / checkbox group | All | N | Valid status list |
| Keyword | Search box | Blank | N | Searchable fields and fuzzy/exact match rule |

### 6.4 Detail Table Fields

| Column | Source field | Display format | Sortable | Notes |
| --- | --- | --- | --- | --- |
| [Column 1] | [Source field] | Text / number / date | Y / N | Masking, link, or status style |
| [Column 2] | [Source field] | Text / number / date | Y / N | Format and alignment |
| [Column 3] | [Source field] | Text / number / date | Y / N | Format and alignment |

### 6.5 Diagram / Illustration

[Insert the approved chart mockup, screenshot, or wireframe here. Confirm chart type, axis labels, legend position, and detail table placement before development.]

## 7. Interaction, Permission, and Export Requirements

| Requirement | Expected behavior |
| --- | --- |
| Responsive layout | Page must support desktop and agreed responsive breakpoints without clipped labels or overlapping controls. |
| Hover / click | Tooltip appears on hover; click behavior follows the drill-down rule defined above. |
| Export | None / export chart image / export detail CSV or Excel. Exported data must follow active filters. |
| Permissions | Users only see data within their authorized organization, role, or data scope. |
| Audit / logging | [Define whether chart access, export, or drill-down actions need logging.] |
| Accessibility | Color must not be the only status indicator; chart labels, contrast, and keyboard access should be considered. |

## 8. Development Requirements

### 8.1 Technical Specifications

- Develop with HTML, Bootstrap, JavaScript, and jQuery unless the target platform requires another approved stack.
- Use clean, structured, maintainable code with clear comments for non-obvious logic.
- Keep the implementation responsive, lightweight, and suitable for secondary development.
- Use lightweight hover, fade, and sticky interactions only where they improve usability.
- Avoid complex plugins unless approved by the technical owner.
- Confirm API contract, request parameters, response schema, error codes, and pagination before development starts.

### 8.2 Performance and Security

| Category | Requirement |
| --- | --- |
| Performance | [Define target load time, max rows, aggregation approach, caching rule, and timeout behavior.] |
| Security | [Define authentication, authorization, data masking, export restriction, and sensitive-field handling.] |
| Compatibility | [Define supported browsers, screen widths, and platform constraints.] |
| Error handling | [Define user-facing error messages and fallback behavior for API or data failures.] |

## 9. Color System

| Token | Approved value |
| --- | --- |
| Background | #f6f8fb / #f3f5f7 |
| Panel | #ffffff |
| Hover Surface | #eef2f4 |
| Soft Blue Panel | #f0f6ff |
| Primary Text | #111315 |
| KMS Text | #17202a |
| Secondary Text | #424a55 / #647280 |
| Border | #d9e1e7 / rgba(17,19,21,0.17) |
| Active Border | rgba(17,19,21,0.28) |
| Primary Blue | #2563eb |
| Primary Hover | #1d4ed8 |
| Primary Soft BG | #e8f1ff |
| Accent Blue | #60a5fa |
| Accent Soft BG | rgba(96,165,250,0.17) |
| Danger / Error / Warning | #c2413b / #b43636 / #a56313 |

## 10. Acceptance Criteria and UAT Checklist

| ID | Acceptance criteria | Owner | Status |
| --- | --- | --- | --- |
| AC-01 | Chart values match the agreed source data and calculation rules. | QA / Data owner | Pending |
| AC-02 | All query filters apply correctly and reset to documented default values. | QA | Pending |
| AC-03 | Tooltip, legend, axis labels, and empty/loading/error states display correctly. | QA / UI | Pending |
| AC-04 | Detail table records reconcile with the selected chart segment and active filters. | QA / Data owner | Pending |
| AC-05 | Exported data, if enabled, follows active filters and permission scope. | QA / Security | Pending |
| AC-06 | Page is responsive and has no clipping, overlap, or unreadable labels on supported screen widths. | QA / UI | Pending |
| AC-07 | Permission and data-scope rules are validated for each target user role. | Security / QA | Pending |

## 11. Open Questions and Change Log

### 11.1 Open Questions

| No. | Question | Owner | Due date | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Confirm source table and final field mapping. | TBD | YYYY-MM-DD | Open |
| 2 | Confirm chart type and drill-down behavior. | TBD | YYYY-MM-DD | Open |
| 3 | Confirm permission scope and export policy. | TBD | YYYY-MM-DD | Open |

### 11.2 Change Log

| Version | Date | Author | Change description |
| --- | --- | --- | --- |
| v0.1 | [YYYY-MM-DD] | [Name] | Initial enhanced requirement template. |
| v0.2 | [YYYY-MM-DD] | [Name] | [Update description] |
