# Business Process Requirement Template
> Use this template to confirm a business process, required data, page behavior, permissions, integrations, non-functional requirements, and acceptance criteria before development starts.  
> Replace the prompts in `[]` with confirmed project information; remove items that are not applicable.

## 1. Basic Document Information

| Field | Details |
| --- | --- |
| Template name | Business Process Requirement Template |
| Document name | [D.CHQ.QDM Business Process Requirement] |
| Document ID | [Suggested: BRD-QDM-001] |
| Business process name | [To be completed] |
| Business owner | [To be completed] |
| Process owner / product owner | [To be completed] |
| Author | [To be completed] |
| Creation date | [YYYY-MM-DD] |
| Current version | v0.1 Draft |
| Document status | Draft / Under Review / Approved |
| Target release / milestone | [To be completed] |
| Related systems | [Upstream, downstream, workflow, reporting, authentication systems] |
| Confidentiality level | Internal |

### 1.1 Version History

| Version | Date | Author | Change summary | Approver |
| --- | --- | --- | --- | --- |
| v0.1 | [Date] | [Author] | Initial requirement structure prepared. | [Approver] |
| v0.2 | [Date] | [Author] | [Update after business review] | [Approver] |

## 2. Background and Objectives

### 2.1 Background

[Describe the current process background, business problem, operational pain points, and why this process needs to be standardized or system-supported.]

Description: The business process requires a clear and auditable workflow covering data input, validation, approval, execution, tracking, and configuration. This document should be completed by business and technical stakeholders so the final solution reflects the actual operating process and development constraints.

### 2.2 Objectives

- Define the end-to-end business process and ownership of each step.
- Identify required data sources, key fields, validation logic, and data quality expectations.
- Specify pages, functions, permissions, and configuration behavior needed by users.
- Document technical, integration, non-functional, and acceptance requirements for development and testing.
- Capture open questions and approval checkpoints before implementation begins.

## 3. Scope

| Scope area | Included | Excluded / out of scope | Notes |
| --- | --- | --- | --- |
| Business workflow | [To be completed] | [To be completed] | Confirm initiation, review, approval, rejection, exception, and closure steps. |
| Data management | [To be completed] | [To be completed] | Include data ownership, source tables, refresh rules, and retention expectations. |
| User interface | [To be completed] | [To be completed] | Include page list, role access, filters, actions, and audit history. |
| Reporting / analytics | [To be completed] | [To be completed] | Confirm dashboard, export, and operational report requirements. |

## 4. Responsible Parties and Stakeholders

| Role | Name / team | Responsibility | Decision authority | Contact |
| --- | --- | --- | --- | --- |
| Business sponsor | [To be completed] | Owns business outcome, funding, and priority. | Yes / No | [Email/IM] |
| Business owner | [To be completed] | Defines process policy and confirms requirement completeness. | Yes / No | [Email/IM] |
| Process operator | [To be completed] | Executes daily process activities and raises operational issues. | No | [Email/IM] |
| IT owner | [To be completed] | Owns technical design, delivery, and deployment readiness. | Yes / No | [Email/IM] |
| Data owner | [To be completed] | Confirms source tables, fields, data quality, and retention. | Yes / No | [Email/IM] |
| QA / tester | [To be completed] | Prepares test cases and verifies acceptance criteria. | No | [Email/IM] |
| Security / compliance | [To be completed] | Reviews permission, audit, data protection, and compliance requirements. | Yes / No | [Email/IM] |

## 5. Data Description

### 5.1 Data Sources

| Source name | Type | Owner | Refresh frequency | Usage in process | Notes |
| --- | --- | --- | --- | --- | --- |
| XXX_Table | Database table | [Data owner] | Real-time / Daily / Manual | Primary source for process data. | Confirm actual table name and environment. |
| [Suggested source] | API / File / Manual input | [Owner] | [Frequency] | [Usage] | [Notes] |

### 5.2 Key Fields and Data Dictionary

| Field name | Business definition | Data type | Required | Validation / logic | Example |
| --- | --- | --- | --- | --- | --- |
| XXX_Fields | [Describe the business meaning of this field] | Text / Number / Date | Yes / No | [Validation rule] | [Example value] |
| Request ID | Unique identifier for each process instance. | Text | Yes | System generated; must be unique. | QDM-2026-0001 |
| Requester | User who initiates the process. | User | Yes | Must be an active authorized user. | [User name] |
| Status | Current workflow state. | Text | Yes | Controlled by workflow status list. | Draft / Submitted / Approved / Rejected / Closed |
| Created time | Timestamp when the process instance is created. | DateTime | Yes | System generated. | 2026-05-20 09:30 |
| Last updated time | Timestamp for the most recent update. | DateTime | Yes | System generated after each save/action. | 2026-05-20 10:15 |

### 5.3 Data Logic and Quality Rules

| Rule ID | Rule description | Trigger | Expected system behavior | Error / warning message |
| --- | --- | --- | --- | --- |
| DQ-01 | Required fields must be completed before submission. | Submit | Block submission and highlight missing fields. | Please complete all required fields before submitting. |
| DQ-02 | Only valid status transitions are allowed. | Workflow action | Allow action only when current role and status match the transition rule. | This action is not available for the current status. |
| DQ-03 | [Suggested rule] | [Trigger] | [Behavior] | [Message] |

## 6. Process Description

### 6.1 Flowchart Illustration

[Insert the final flowchart here after the workflow is confirmed.]

Recommended notation: Start, user action, system validation, approval decision, rejection loop, completion, and exception path.

### 6.2 Workflow Step Matrix

| Step | Actor / role | Input | Activity | System output | Next status |
| --- | --- | --- | --- | --- | --- |
| 1 | Requester | Business data and attachments | Create process request and save draft. | Draft record created. | Draft |
| 2 | Requester | Completed request | Submit request for review. | Validation result and workflow task. | Submitted |
| 3 | Approver / reviewer | Submitted request | Review details, comments, and supporting data. | Approval decision recorded. | Approved / Rejected |
| 4 | System | Approved request | Update status, write audit history, and notify related users. | Completed process record. | Closed / Completed |
| 5 | Requester | Rejected request | Revise and resubmit or cancel. | Updated request and history. | Draft / Cancelled |
| 6 | [Suggested role] | [Input] | [Exception handling / escalation step] | [Output] | [Status] |

## 7. Business Rules

| Rule ID | Business rule | Owner | Priority | Remarks |
| --- | --- | --- | --- | --- |
| BR-01 | The process must maintain a complete audit trail for creation, submission, approval, rejection, reassignment, and closure. | Business / IT | High | Audit history should be visible on the details page. |
| BR-02 | Only authorized users may initiate, review, approve, configure, or manage permissions. | Business / Security | High | Map authorization to the permission matrix. |
| BR-03 | Rejected requests must preserve reviewer comments and allow requester correction. | Business | Medium | Confirm whether resubmission uses the same request ID. |
| BR-04 | [Suggested business rule] | [Owner] | High / Medium / Low | [Remarks] |

## 8. Page / Function Presentation

| Page / function | Purpose | Key components | Primary actions | Access role |
| --- | --- | --- | --- | --- |
| Process initiation page | Allows authorized users to create and submit a process request. | Input form, required fields, attachments, save draft, submit. | Save, Submit, Cancel | Requester |
| Process to-do list | Shows tasks requiring user action. | Task list, filters, status, due date, owner, quick action entry. | Open, Approve, Reject, Reassign | Reviewer / Approver |
| Process details and history page | Displays full process detail and audit trail. | Header summary, data fields, comments, history timeline, attachments. | Comment, Export, Print | Authorized roles |
| Configuration | Maintains configurable values used by the process. | Status list, routing rules, thresholds, notification templates. | Add, Edit, Disable | Admin |
| Permission management | Manages role-based access and authorization. | User-role mapping, function access, data scope. | Grant, Revoke, Audit | Security / Admin |
| [Suggested reporting page] | Provides operational visibility and export capability. | Filters, KPI summary, table, export. | Search, Export | [Role] |

### 8.1 UI Behavior and Layout Requirements

| Requirement area | Requirement | Priority |
| --- | --- | --- |
| Responsiveness | Pages must support desktop and common tablet widths without horizontal overflow. | High |
| Form validation | Required, format, and business-rule validation messages must appear near the affected field. | High |
| Search and filter | List pages should support keyword search, status filter, owner filter, and date range filter where applicable. | Medium |
| Audit visibility | Details page must show action time, actor, action, comments, and resulting status. | High |
| Empty / error states | Pages must provide clear empty, loading, and error states. | Medium |

### 8.2 Diagram / Illustration

[Insert page wireframes, screenshots, or process diagrams after the relevant page requirements. Label each image with the page name and version.]

## 9. Permissions and Controls

| Function | Requester | Reviewer | Approver | Admin | Security |
| --- | --- | --- | --- | --- | --- |
| Create request | Create | View | View | View | View |
| Submit request | Submit own | No | No | No | No |
| Review request | View own | Review | Approve / Reject | View | View |
| Edit configuration | No | No | No | Edit | View |
| Manage permissions | No | No | No | View | Edit |
| Export data | [Confirm] | [Confirm] | [Confirm] | [Confirm] | [Confirm] |

## 10. Audit and Compliance Requirements

- Record every workflow action with actor, timestamp, original status, new status, comments, and source page.
- Restrict sensitive data by role and data scope.
- Define retention period and archival approach before go-live.
- Confirm whether data export requires approval, masking, or watermarking.

## 11. Development Requirements

### 11.1 Technical Specifications

[If this template's default stack is applicable, develop with HTML, Bootstrap, JavaScript, and jQuery. Code should be clean, structured, commented where useful, responsive, and easy for secondary development. Use lightweight hover, fade, and sticky interactions only where they improve usability; avoid complex plugins unless explicitly approved.]

If the project specifies a different stack, follow the confirmed stack and preserve the functional, UI, permission, audit, and acceptance requirements.

### 11.2 Color System

| Token | Value | Usage |
| --- | --- | --- |
| Background | #f6f8fb / #f3f5f7 | Application background surfaces. |
| Panel | #ffffff | Cards, panels, and form containers. |
| Hover surface | #eef2f4 | Hover and secondary interaction states. |
| Soft blue panel | #f0f6ff | Subtle informational panels. |
| Primary text | #111315 | Main body and labels. |
| KMS text | #17202a | KMS-aligned emphasis text. |
| Secondary text | #424a55 / #647280 | Helper text, metadata, and muted labels. |
| Border | #d9e1e7 / rgba(17,19,21,0.17) | Default borders and separators. |
| Active border | rgba(17,19,21,0.28) | Focused and selected states. |
| Primary blue | #2563eb | Primary actions and active indicators. |
| Primary hover | #1d4ed8 | Primary action hover state. |
| Primary soft BG | #e8f1ff | Subtle selected/active backgrounds. |
| Accent blue | #60a5fa | Accent highlights. |
| Danger / error | #c2413b / #b43636 | Danger actions and error messages. |
| Warning | #a56313 | Warning messages and pending states. |
| Shadow | 0 14px 34px rgba(38, 55, 70, 0.1) | Soft elevation only. |

## 12. Integration and Interface Requirements

| Interface | Direction | Data / payload | Frequency | Failure handling | Owner |
| --- | --- | --- | --- | --- | --- |
| [Suggested API / table] | Inbound / Outbound | [Payload] | [Frequency] | Retry / alert / manual correction | [Owner] |
| Authentication / SSO | Inbound | User identity and role attributes | At login | Deny access and show authorization message. | IT / Security |
| Notification service | Outbound | Task assignment, approval result, rejection comments | Event-based | Log failure and allow resend. | IT |

## 13. Non-Functional Requirements

| Category | Requirement | Target / measure | Priority |
| --- | --- | --- | --- |
| Performance | List and detail pages should load within an agreed response time under normal business volume. | [e.g., <= 3 seconds] | High |
| Availability | System should be available during defined business hours and planned maintenance windows. | [To be completed] | High |
| Security | Access must be role-based and aligned with permission matrix. | No unauthorized access in testing. | High |
| Usability | Users should complete the standard submit/review flow without manual data re-entry. | Validated in UAT. | Medium |
| Maintainability | Configuration values should be maintainable without code changes where practical. | Admin-configurable. | Medium |

## 14. Acceptance Criteria and Testing

| AC ID | Acceptance criteria | Test method | Owner | Status |
| --- | --- | --- | --- | --- |
| AC-01 | A requester can create, save, submit, and view a process request with all required fields validated. | Functional test / UAT | QA / Business | Not Started |
| AC-02 | Approvers can approve or reject requests, and comments are saved in the audit history. | Functional test / UAT | QA / Business | Not Started |
| AC-03 | Permission rules prevent unauthorized users from accessing restricted functions. | Security test | QA / Security | Not Started |
| AC-04 | Data source fields and validation logic match the approved data dictionary. | Data validation test | QA / Data owner | Not Started |
| AC-05 | Pages follow the approved technical specifications and color system. | UI review | QA / IT | Not Started |
| AC-06 | [Suggested acceptance criterion] | [Test method] | [Owner] | Not Started |

### 14.1 UAT Sign-Off

| Role | Name | Sign-off decision | Date | Comments |
| --- | --- | --- | --- | --- |
| Business owner | [Name] | Approved / Approved with Issues / Rejected | [Date] | [Comments] |
| IT owner | [Name] | Approved / Approved with Issues / Rejected | [Date] | [Comments] |
| Security / compliance | [Name] | Approved / Approved with Issues / Rejected | [Date] | [Comments] |

## 15. Risks, Dependencies, and Open Questions

### 15.1 Risks and Dependencies

| ID | Type | Description | Impact | Mitigation / next action | Owner |
| --- | --- | --- | --- | --- | --- |
| R-01 | Requirement | Business rules are not fully confirmed before development starts. | Rework and UAT delay. | Complete stakeholder review and sign-off. | Business owner |
| D-01 | Dependency | Actual source table and field definitions are pending confirmation. | Data mapping cannot be finalized. | Confirm source owner and field dictionary. | Data owner |
| R-02 | Security | Permission matrix is incomplete. | Access control defects. | Review roles with Security before build. | Security |
| [ID] | Risk / Dependency | [Description] | [Impact] | [Action] | [Owner] |

### 15.2 Open Questions

| Question ID | Question | Owner | Target date | Resolution |
| --- | --- | --- | --- | --- |
| Q-01 | What is the confirmed process owner and final approval authority? | [Owner] | [Date] | [Resolution] |
| Q-02 | What are the final source tables, key fields, and refresh frequency? | [Owner] | [Date] | [Resolution] |
| Q-03 | Which statuses and transitions are allowed in the workflow? | [Owner] | [Date] | [Resolution] |
| Q-04 | Which functions require export, notification, or reporting support? | [Owner] | [Date] | [Resolution] |
| Q-05 | Are there audit, retention, masking, or compliance requirements beyond standard role-based access? | [Owner] | [Date] | [Resolution] |

## 16. Suggested Completion Checklist

| Item | Completion check | Status |
| --- | --- | --- |
| Document information | Document owner, author, version, status, and approvers are completed. | Open |
| Scope | In-scope and out-of-scope items are agreed. | Open |
| Data | Source tables, field dictionary, and data rules are confirmed. | Open |
| Workflow | Flowchart, step matrix, statuses, and exception paths are confirmed. | Open |
| Pages | Page list, actions, wireframes, and role access are confirmed. | Open |
| Development | Technical stack, color system, integration, and non-functional requirements are confirmed. | Open |
| Testing | Acceptance criteria and UAT sign-off owners are confirmed. | Open |
