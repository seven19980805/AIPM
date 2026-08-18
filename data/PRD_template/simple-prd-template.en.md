# PRD Template (Simple Version)

> Use case: simple requirements, internal communication, quick project kickoff  
> Note: this template **does not include performance requirements** or **acceptance criteria**

## 1. Document Information

- Project name:
- Requirement name:

## 2. Background

### 2.1 Background Summary

Briefly explain why this requirement is needed and what problem or opportunity currently exists.

### 2.2 Objective

Clearly state what this requirement is expected to achieve.

Examples:

- Improve the efficiency of a process
- Fill a missing foundational capability
- Enhance user experience

## 3. Scope

### 3.1 In Scope

Describe what is included in this requirement.

Examples:

- Add XX feature
- Update XX page
- Optimize XX workflow

### 3.2 Out of Scope

Describe what is explicitly not included to avoid misunderstandings.

Examples:

- No changes to the admin backend
- No data migration
- No mobile adaptation

## 4. Users and Usage Scenarios

### 4.1 Target Users

Describe who will use this feature.

Examples:

- General platform users
- Operations staff
- Internal administrators

### 4.2 Core Scenarios

Describe when and how users will use this feature.

Examples:

1. When a user needs to do XX, they can complete it through XX
2. When operations staff need to do XX, they can handle it on the XX page

## 5. Functional Requirements

### 5.1 Feature Overview

Use a short paragraph to describe the overall logic of the feature.

### 5.2 Feature Details

#### Feature 1: Feature Name

- Description:
- Trigger:
- Processing logic:
- Inputs:
- Outputs:
- Exception cases:

#### Feature 2: Feature Name

- Description:
- Trigger:
- Processing logic:
- Inputs:
- Outputs:
- Exception cases:

> Add more feature items using the same format if needed

## 6. Business Rules

Describe the relevant rules, constraints, conditions, and status transitions of the feature.

Examples:

- Users can perform XX only when they are in XX status
- Submission is not allowed when field A is empty
- If a user repeats an action, show XX prompt

## 7. Page / Interaction Notes

If the requirement involves pages or user flows, describe them here.

### 7.1 Page Description

- Page name:
- Entry point:
- Page elements:
- Button actions:

### 7.1.1 Chart Requirement Notes (if single or multiple charts are needed)

- Chart name:
- Chart type: line / bar / pie / table chart / other
- Data source:
- Key fields:
- Field logic:
- Dimension / metric / axis notes:
- Query filters:
- Detail data display:
- Multi-chart relationships:
- Chart interactions: linked filtering / drill-down / tab switching / tooltip / click filtering, etc.

### 7.1.2 Multi-Chart Layout Reference (if multiple charts are needed)

If a page includes one or more charts, choose a layout based on data hierarchy, comparison needs, and available space:

1. **Uniform Grid**: chart containers share the same size and align like a chessboard; suitable for monitoring dashboards, peer-level data cards, and status overview pages.
2. **Primary-Detail / Hero Layout**: one main chart occupies 50%-70% of the top or left area, with supporting charts beside or below it; suitable for analysis pages such as one large trend chart plus composition charts and a detail table.
3. **Nested / Drill-down Layout**: one chart contains, links to, or updates another chart; suitable for exploratory and drill-down analysis.
4. **Tabbed Layout**: multiple homogeneous charts share one container and switch via tabs; suitable for Day/Week/Month views where space is limited.
5. **Masonry / Waterfall Layout**: cards share a consistent width but vary in height and fill gaps sequentially; suitable for mixed media reports, mobile H5 pages, and feeds, but use cautiously in dashboards to avoid clutter.

### 7.1.3 Business Process Page Notes (if a process is involved)

- Process name:
- Process trigger:
- Participating roles:
- Process nodes:
- Node actions and status changes:
- Exception / return / termination paths:
- Flowchart notes:
- Related pages: initiation page / to-do list / process detail and history page / configuration page / permission management
- Permission rules:

### 7.2 Interaction Flow

You can describe the flow in text and optionally add a flowchart.

Examples:

1. The user enters the XX page
2. The user clicks the XX button
3. The system displays XX content
4. After submission, the user sees XX result

## 8. Copywriting

List page messages, button labels, error messages, and related text.

Examples:

- Button text: Submit Now
- Empty state: No data available
- Error message: Submission failed. Please try again later.

## 9. Data and Dependencies

Describe whether this requirement depends on other systems, APIs, configurations, or data sources.

Examples:

- Depends on the user center to return user information
- Depends on the configuration platform to deliver feature flags
- Depends on XX API to provide query results

## 10. Risks and Notes

List known risks, constraints, or items that need to be confirmed in advance.

Examples:

- Related APIs are not ready yet; integration timeline needs confirmation
- Existing users may need time to adapt to the updated flow
- Some field definitions are still pending final business confirmation
