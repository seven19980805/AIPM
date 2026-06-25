# ABF Yield Analysis Template

> Use this template to define an ABF substrate manufacturing yield-analysis dashboard or analysis page.  
> Replace the prompts in `[]` with confirmed project information and remove items that are not applicable.

## 1. Basic Document Information

| Field | Value |
| --- | --- |
| Template name | ABF Yield Analysis Template |
| Document name | [ABF Yield Analysis Requirement] |
| Analysis topic / page name | [Example: ABF Yield Analysis Dashboard] |
| Business domain | Manufacturing quality / ABF / QDM |
| Requesting team | [Department / team] |
| Business owner | [Person responsible for yield definition and acceptance] |
| Data owner | [Person responsible for source tables and field definitions] |
| Product owner / BA | [Name] |
| Technical owner | [Name] |
| Version | v0.1 draft |
| Status | Draft / In review / Approved / In development / Released |
| Target release / due date | [YYYY-MM-DD] |
| Related systems / modules | [MES / QMS / QDM / data platform / dashboard module] |

## 2. Background and Objectives

### 2.1 Background

[Describe the current ABF yield-management situation, pain points, users, decision scenarios, and why this analysis page is needed.]

Example: ABF manufacturing spans multiple process and inspection steps. The business needs to quickly identify whether yield drops come from product, lot, panel, process step, equipment, or defect category, and use the result for quality meetings, abnormal response, and improvement tracking.

### 2.2 Analysis Objectives

- Show ABF yield by time, product, material, lot, panel, process step, equipment, and defect category.
- Identify the process steps, defect types, and lots that contribute most to yield loss.
- Support drill-down from overall yield to lot / panel / step / defect details.
- Standardize yield definitions, data sources, filter logic, and acceptance criteria.
- Provide data support for abnormal alerts, responsibility assignment, and improvement closure.

### 2.3 Success Criteria

- Business owners confirm yield formulas, exclusions, rework/retest handling, and target thresholds.
- Dashboard data matches approved source queries or existing quality reports.
- Users can locate the main yield-loss source and related detail within the expected time.
- Filters, drill-down, export, and permission rules behave consistently in representative cases.

## 3. Analysis Scope

| Area | Description |
| --- | --- |
| Product scope | [ABF product family, material number, customer, version, or process platform] |
| Process scope | [Covered process steps such as exposure, development, plating, AOI, testing] |
| Data scope | [History start date, refresh cadence, lot status, whether engineering/pilot lots are included] |
| Chart scope | KPI, trend, process-step loss, defect Pareto, lot/panel detail, heatmap, export |
| Out of scope | [Upstream data-capture changes, complex prediction models, automated task assignment] |
| Assumptions and dependencies | [Source availability, field mapping, permission rules, target configuration, API SLA] |

## 4. Responsible Parties and Stakeholders

| Role | Name / team | Responsibility |
| --- | --- | --- |
| Manufacturing owner | [TBD] | Confirms production scenarios, process-step ownership, and daily usage flow. |
| Quality owner | [TBD] | Confirms yield definitions, defect taxonomy, abnormal closure, and acceptance criteria. |
| Process owner | [TBD] | Explains process loss, parameters, and improvement actions. |
| Equipment owner | [TBD] | Confirms equipment dimension, equipment abnormality, and parameter correlation. |
| Data owner | [TBD] | Confirms source tables, field definitions, refresh cadence, and data quality rules. |
| Product owner / BA | [TBD] | Maintains scope, priority, review, and change control. |
| Development owner | [TBD] | Implements data APIs, aggregation logic, page, and chart interactions. |
| QA / UAT owner | [TBD] | Writes test cases and validates data, functions, and permissions. |

## 5. Yield Definitions and Business Rules

### 5.1 Yield Formulas

| Metric | Formula / definition | Grain | Notes |
| --- | --- | --- | --- |
| Overall yield | [Good quantity / input quantity] | Product / lot / period | Define whether rework-pass quantity is included. |
| Step yield | [Step pass quantity / step input quantity] | Step / equipment / lot | Define step entry and exit. |
| First-pass yield | [Direct-pass quantity without rework / input quantity] | Product / step | Shows hidden rework cost. |
| Scrap rate | [Scrap quantity / input quantity] | Defect / step | Separate from rework, hold, and pending disposition. |
| Yield-loss contribution | [Loss quantity for a defect or step / total loss quantity] | Defect / step | Used for Pareto analysis. |

### 5.2 Definition Rules

- Define numerator, denominator, input quantity, good quantity, defect quantity, scrap quantity, and rework quantity.
- Specify whether engineering lots, pilot lots, hold lots, retest records, rework records, and cancelled lots are included.
- Specify whether time attribution uses input time, step completion time, test completion time, or warehouse time.
- The same metric must use the same calculation logic in KPI, trend, detail table, and export.
- Fix percentage precision, units, rounding, and null handling in this document.

## 6. Data Description and Data Contract

### 6.1 Data Sources

| Source ID | Table / view / API | Business description | Grain | Refresh cadence | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | [MES lot/step records] | Lot, process step, input/output quantity, step time. | Lot + step | [Real-time / hourly / daily] | [TBD] |
| DS-02 | [QMS / defect inspection records] | Defect code, defect category, disposition result. | Panel / defect | [TBD] | [TBD] |
| DS-03 | [Test-system records] | Electrical, final, or reliability test result. | Panel / unit | [TBD] | [TBD] |
| DS-04 | [Work-order / product master data] | Product, material, customer, version, target yield. | Product / order | [TBD] | [TBD] |
| DS-05 | [Equipment / parameter logs] | Equipment, machine, key parameters, alarms. | Equipment / time | [TBD] | [TBD] |

### 6.2 Key Fields

| Field name | Source | Type | Required | Business definition / logic |
| --- | --- | --- | --- | --- |
| lot_id | MES | String | Yes | Unique lot identifier. |
| panel_id | MES / QMS | String | Recommended | Unique panel identifier for drill-down and detail tracking. |
| product_code / material_no | Master data | String | Yes | Product or material dimension. |
| process_step | MES | String | Yes | Process step or operation. |
| equipment_id | MES / equipment logs | String | Recommended | Equipment or line dimension. |
| defect_code / defect_type | QMS | String | Recommended | Defect code and category. |
| input_qty / pass_qty / fail_qty / scrap_qty / rework_qty | MES / QMS | Number | Yes | Base quantities for yield and loss calculations. |
| event_time | All sources | DateTime | Yes | Used for period filtering and refresh checks. |

### 6.3 Data Quality Rules

- Define cross-system join keys: lot_id, panel_id, work_order, process_step, equipment_id.
- Handle duplicate records, late-arriving data, missing process steps, missing defect codes, and pending disposition records.
- Define refresh SLA and how the last refresh time is displayed.
- Define reconciliation method and allowed tolerance against source systems.
- Document the impact of historical backfill, recalculation, and definition changes.

## 7. Analysis Dimensions and Filters

| Dimension | Example | Purpose |
| --- | --- | --- |
| Time | Day / week / month / shift | Trend, period comparison, abnormality location. |
| Product | Product family / material / customer / version | Product-yield comparison and target management. |
| Process | Process step / line / equipment | Locate process-loss source. |
| Lot | Work order / lot / panel | Detail tracking and abnormal-lot review. |
| Defect | Defect category / defect code / disposition result | Pareto and root-cause analysis. |

| Filter | Control type | Default | Required | Notes |
| --- | --- | --- | --- | --- |
| Date range | Date picker | Last 30 days / latest period | Yes | Limit maximum query range. |
| Product / material | Searchable select | All or user default scope | No | Filter by permissions where needed. |
| Lot / panel | Search box | Empty | No | Support exact lookup. |
| Process step | Multi-select | All | No | Links charts and detail table. |
| Defect category | Multi-select | All | No | Links Pareto and detail table. |
| Equipment / line | Multi-select | All | No | Helps locate equipment-related abnormalities. |

## 8. Metric System

| Metric | Description | Presentation | Target / threshold |
| --- | --- | --- | --- |
| Input quantity | Total quantity entering the analysis scope. | KPI / detail | [TBD] |
| Good quantity | Passing quantity based on approved definition. | KPI / detail | [TBD] |
| Defect quantity | Failed, scrapped, or pending-disposition quantity. | KPI / Pareto | [TBD] |
| Overall yield | Core yield metric. | KPI / trend | [Target yield] |
| Step yield | Yield by process step. | Matrix / bar chart | [Step target] |
| Defect contribution | Contribution of each defect to yield loss. | Pareto | Top N |
| Abnormal lot count | Lots below threshold or with abnormal movement. | KPI / detail | [Warning line] |

## 9. Page and Chart Presentation

| Area | Content / behavior |
| --- | --- |
| Top filter area | Date, product, lot, step, defect, equipment filters; query, reset, export. |
| KPI area | Overall yield, target gap, input quantity, good quantity, loss quantity, abnormal lots. |
| Trend area | Yield trend, target line, period comparison, and abnormal markers. |
| Analysis area | Step-yield matrix, defect Pareto, product/material comparison, equipment comparison. |
| Detail area | Lot, panel, process step, defect, equipment, quantity, and status details. |

| Chart ID | Chart name | Type | Primary metric | Dimension | Interaction |
| --- | --- | --- | --- | --- | --- |
| CH-01 | ABF Overall Yield Trend | Line chart | Overall yield / target yield | Date | Click abnormal point to filter details. |
| CH-02 | Process Step Yield Loss | Bar chart / heatmap | Step yield / loss quantity | Step | Click step to drill into defects and lots. |
| CH-03 | Defect Pareto | Pareto chart | Defect contribution / defect quantity | Defect category | Click defect to filter details. |
| CH-04 | Product / Material Comparison | Bar chart | Yield / input quantity | Product / material | Sort and export. |
| CH-05 | Lot / Panel Detail | Table | Yield, quantity, status | Lot / panel | Pagination, sort, drill-down. |

## 10. Drill-down and Root-Cause Analysis

| Path | Description | Output |
| --- | --- | --- |
| Product -> lot | View low-yield lots under a product. | Lot list, lot yield, target gap. |
| Lot -> panel | View panel distribution within a lot. | Panel yield, defect count, status. |
| Panel -> step | Track panel performance at each step. | Step pass/fail, time, equipment. |
| Step -> defect | View major defects at the selected step. | Defect Pareto and defect details. |
| Defect -> equipment / parameter | Check whether defects concentrate on equipment or parameter ranges. | Equipment comparison, parameter notes, improvement record. |

Root-cause support rules:

- Rank by loss contribution by default and show Top 10.
- Support comparison by equipment, shift, product, and lot for the same step.
- Abnormal points must show definition, filters, and last refresh time.
- Users can record cause category, responsible department, containment action, and long-term action.

## 11. Alerts and Improvement Closure

| Alert item | Trigger condition | Severity | Recipients | Response SLA |
| --- | --- | --- | --- | --- |
| Overall yield below target | [Overall yield < target - tolerance] | High / Medium | Quality / manufacturing | [TBD] |
| Step yield abnormal | [Step yield below threshold or period drop] | High / Medium | Process / equipment | [TBD] |
| Defect spike | [Defect share exceeds threshold] | Medium | Quality / process | [TBD] |
| Refresh abnormality | [Refresh exceeds SLA] | Medium | Data owner | [TBD] |

Improvement closure fields: responsible department, cause category, containment action, long-term action, due date, closure condition, review notes.

## 12. Interactions, Permissions, and Export

| Requirement | Expected behavior |
| --- | --- |
| Linked filtering | Clicking trend point, step, defect, or product updates related charts and details by context. |
| Tooltip | Show metric value, numerator/denominator, target gap, period, filters, and definition note. |
| Detail drill-down | Detail table must match current filters and permission scope. |
| Export | Export chart image or detail CSV/Excel for current filters; include filter context in export. |
| Permissions | Users only see authorized products, lines, customers, or plant data. |
| Audit | Log export, sensitive detail viewing, alert closure, and improvement-action changes. |

## 13. Technical Specifications and Non-Functional Requirements

| Category | Requirement |
| --- | --- |
| API / aggregation | Define request parameters, response structure, pagination, sorting, aggregation level, and error codes. |
| Performance | Default first-screen charts target completion within 3 seconds; large queries need prompts or async export. |
| Data accuracy | KPI, charts, detail table, and export must be consistent under the same filters. |
| Reliability | One chart failure must not break the page; show chart-level error state and retry. |
| Security | Follow role permissions and protect customer, product, or sensitive process information during export. |
| Accessibility | Status cannot rely only on color; charts need titles, units, and readable labels. |
| Maintainability | Yield formulas, target thresholds, and chart configuration should be configurable where practical. |

## 14. Acceptance Criteria

| ID | Acceptance criterion | Owner | Status |
| --- | --- | --- | --- |
| AC-01 | Yield formulas, numerators, denominators, exclusions, rework/retest rules are approved by business and data owners. | Business / data | Pending |
| AC-02 | KPI, trend, step, defect Pareto, and detail data match source queries under default filters. | QA / data | Pending |
| AC-03 | Date, product, lot, step, defect, and equipment filters work correctly and can be reset. | QA | Pending |
| AC-04 | After chart drill-down, related charts, detail table, and export keep the same context. | QA / product | Pending |
| AC-05 | Permission limits, sensitive-field display, and export rules meet security requirements. | Security / QA | Pending |
| AC-06 | Loading, empty, error, alert, and last-refresh states display correctly. | QA / UI | Pending |
| AC-07 | Page works in target browsers and key screen widths without overlap, truncation, or unreadable labels. | QA / UI | Pending |

## 15. Open Questions and Change Log

| ID | Question | Owner | Due date | Decision |
| --- | --- | --- | --- | --- |
| Q-01 | Does the final yield definition include quantity that passes after rework? | Quality / manufacturing | [YYYY-MM-DD] | Open |
| Q-02 | Are engineering, pilot, and hold lots included in the default analysis? | Business owner | [YYYY-MM-DD] | Open |
| Q-03 | Which system maintains target yield and warning thresholds? | Data / quality | [YYYY-MM-DD] | Open |
| Q-04 | Should alerts trigger automatic notifications or only display on the dashboard? | Product / business | [YYYY-MM-DD] | Open |
| Q-05 | Does detail export need masking by customer, material, or role? | Security / business | [YYYY-MM-DD] | Open |

| Version | Date | Author | Change description |
| --- | --- | --- | --- |
| v0.1 | [YYYY-MM-DD] | [Name] | Initialized ABF yield analysis template. |
