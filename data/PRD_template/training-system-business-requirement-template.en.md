# Training System Business Requirement Template
> For training system scenarios such as course management, training plans, enrollment approval, online learning, exams, certificates, learning profiles, and analytics.  
> Replace the prompts in `[]` with real business content; remove items that are not applicable.

## 1. Basic Information

| Field | Content |
| --- | --- |
| Template name | Training System Business Requirement Template |
| Requirement name | [Enterprise training platform build] |
| Project | [Enter the project name] |
| Requirement type | New build / Optimization / Refactor |
| Priority | High / Medium / Low |
| Proposing department | [Enter the proposing department] |
| Requester | [Enter the requester] |
| Request date | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Business Background

### 2.1 Background summary

[Describe the training business background, existing process, and reason for building the system]

Description: Training plans, course enrollment, learning records, exam results, and certificates are currently scattered across email, spreadsheets, and several platforms. Training admins struggle to track execution, learners lack one learning entry point, and management lacks analyzable training effectiveness data.

### 2.2 Current pain points

- [Training plan publishing and enrollment rely on manual notifications]
- [Course resources are scattered and learning progress is hard to track consistently]
- [Exam results, certificates, and learning profiles are not archived automatically]
- [Training data definitions are inconsistent and reporting takes too much manual work]

## 3. Business Objectives

### 3.1 Business objectives

- [Create one entry point for training plans, courses, and learning]
- [Support closed-loop management of enrollment, learning, exams, and certificates]
- [Improve training execution efficiency and learning record accuracy]
- [Build analyzable training data for talent development decisions]

### 3.2 Quantified metrics

- [Reduce course enrollment processing time by 50%]
- [Reach 98% accuracy for completion statistics]
- [Automatically generate and archive 90% of certificates]
- [Reduce manual training report preparation by 60%]

## 4. Business Scope

### 4.1 In scope

- Course and content management
- Training plan publishing
- Learner enrollment and approval
- Online learning and progress tracking
- Exams, assessments, and score management
- Certificates and learning profiles
- Training reports and analytics

### 4.2 Out of scope

- Building the underlying live classroom engine from scratch
- Complex LMS marketplace transactions
- Deep content procurement from external university platforms
- AI personalized learning path recommendation

## 5. Roles and Core Scenarios

### 5.1 Target roles

- Learner: browse courses, enroll in training, study content, take exams, and view certificates
- Instructor: maintain teaching materials, view learner lists, and review feedback
- Training administrator: create plans, manage enrollment, configure exams and certificates
- Department owner: approve team enrollment and view team learning progress
- Management: view coverage, completion, pass rate, and training effectiveness metrics
- System administrator: maintain permissions, categories, dictionaries, and base configuration

### 5.2 Core business scenarios

1. A training administrator publishes a training plan and opens enrollment to the target audience.
2. A learner selects a course in the training portal, submits enrollment, and receives notifications.
3. A department owner approves team member enrollment, and the system updates enrollment status.
4. A learner completes online learning and takes an assessment.
5. The system generates a certificate based on completion rules and stores the learning profile.
6. Management reviews completion rate, exam pass rate, and course feedback.

## 6. Functional Requirements

### 6.1 Feature overview

[Summarize the core capabilities to be built for the training system]

Description: This requirement covers seven capability groups: course resources, training plans, enrollment approval, learning progress, exams and assessments, certificates and learning profiles, and analytics.

### 6.2 Feature details

#### 6.2.1 Course and content management

- Description: Maintain course categories, course information, content materials, instructors, and target audiences.
- Trigger: A training administrator creates or updates a course.
- Business rules / logic:
-   Support course publishing, unpublishing, categories, tags, and target role maintenance
-   Support videos, documents, assignments, and other content attachments
-   Support course versions and update history
- Inputs: Course name, category, instructor, content, target audience
- Outputs: Course detail, catalog, content list
- Exceptions: Duplicate courses, missing content, deletion blocked when referenced by a plan

#### 6.2.2 Training plans and enrollment approval

- Description: Publish training plans and manage enrollment, approval, quotas, and notifications.
- Trigger: A plan is created or an enrollment is submitted.
- Business rules / logic:
-   Support enrollment by organization, role, or named people
-   Support quota control, waitlists, cancellation, and approval flows
-   Support enrollment, approval, and class-start notifications
- Inputs: Plan name, course, schedule, quota, audience, approver
- Outputs: Training plan, enrollment list, approval result
- Exceptions: Quota full, deadline passed, duplicate enrollment, approval timeout

#### 6.2.3 Online learning and progress tracking

- Description: Provide one learning entry point and record learning progress.
- Trigger: A learner starts course learning.
- Business rules / logic:
-   Support course catalog, learning progress, duration, and completion status
-   Support resume learning, mandatory/elective markers, and reminders
-   Support overdue learning reminders
- Inputs: Learner, course, content, duration, completion status
- Outputs: Learning record, progress statistics, completion proof
- Exceptions: Content playback failure, progress reporting failure, duplicate record merge

#### 6.2.4 Exams, assessments, and score management

- Description: Configure question banks, papers, exam sessions, grading, and score statistics.
- Trigger: A plan requires an exam or an admin publishes one.
- Business rules / logic:
-   Support question bank, paper, exam time, and pass score settings
-   Support automatic grading, manual grading, and retakes
-   Support score lookup, pass-rate statistics, and export
- Inputs: Questions, paper, exam setup, answer records
- Outputs: Score sheet, pass status, exam statistics
- Exceptions: Exam timeout, duplicate submission, cheating flag, insufficient retake eligibility

#### 6.2.5 Certificates and learning profiles

- Description: Generate certificates based on completion and exam results, and build employee learning profiles.
- Trigger: A learner meets certificate issuance conditions.
- Business rules / logic:
-   Support certificate templates, number rules, and validity periods
-   Support certificate generation, download, revocation, and expiry reminders
-   Aggregate learning and certificate records by employee
- Inputs: Completion record, score, certificate template, employee data
- Outputs: Certificate, learning profile, certificate ledger
- Exceptions: Certificate generation failure, expiry, revocation audit trail

#### 6.2.6 Training reports and analytics

- Description: Provide statistics on training execution, learning effectiveness, and resource usage.
- Trigger: A manager or training admin views reports.
- Business rules / logic:
-   Support coverage and completion statistics by organization, course, time, and role
-   Support pass rate, course rating, and feedback summary
-   Support report export and scheduled delivery
- Inputs: Enrollment records, learning records, scores, feedback
- Outputs: Training dashboard, statistical report, export file
- Exceptions: Data delay, insufficient permission, definition change reminder

## 7. Pages and Processes

| Page / entry | Entry | Key elements | Main actions | Flow |
| --- | --- | --- | --- | --- |
| Training portal home | Learner entry | Recommended courses, pending tasks, certificates, notifications | Search courses, enroll, continue learning, view certificates | A learner logs in, reviews tasks, and enters a course. |
| Course management | Training admin console | Course list, course detail, content, instructors, target audience | Create course, edit content, publish/unpublish, copy course | An admin maintains a course and publishes it to the visible audience. |
| Training plan management | Training admin console | Plan list, enrollment list, approval status, notifications | Publish plan, adjust quota, view enrollment, export list | An admin creates a plan, and the system opens enrollment by audience and sends notices. |
| Exam and certificate management | Training admin console | Question bank, paper, exam setup, scores, certificate templates | Configure exam, grade, generate certificate, revoke certificate | After an exam ends, the system summarizes scores and generates certificates by rule. |
| Training analytics dashboard | Management entry | Coverage, completion, pass rate, course rating, trends | Filter, drill down, export, subscribe | Management reviews training effectiveness by organization and time. |

## 8. Business Rules and Data

### 8.1 Business rules / logic

- Enrollment is closed after the deadline by default; admins may add records with permission.
- One learner can have only one active enrollment record for the same training plan.
- Course completion can depend on progress, duration, assignment submission, and exam pass status.
- Certificate numbers must be globally unique and cannot be reused after revocation.
- Changes to scores and certificates must keep an audit trail.

### 8.2 Key data objects

- Course: code, name, category, instructor, content, target audience, status
- Training plan: code, course, schedule, quota, audience, approval rules
- Enrollment record: learner, plan, status, approver, approval time
- Learning record: learner, course, progress, duration, completion status, completion time
- Exam score: exam, learner, score, pass status, grading status
- Certificate: number, learner, course/plan, issue time, validity period, status

## 9. Non-functional Requirements

- Access control: visibility and operations controlled by role, organization, and data scope.
- Performance: common list queries return within 3 seconds; reports may be generated asynchronously.
- Usability: key enrollment and learning flows need retry handling and clear error messages.
- Audit: enrollment approval, score edits, and certificate generation/revocation must be logged.
- Security: exam answers, scores, and certificate data must be managed as sensitive data.

## 10. Integrations and Dependencies

- Organization and employee master data
- Unified identity / SSO
- Message notification service
- Electronic seal or certificate service
- Enterprise data warehouse / BI

## 11. Risks and Open Questions

### 11.1 Risks

- Inconsistent historical training data definitions may affect migration quality.
- Different content formats and playback capabilities may affect learning experience.
- Exam anti-cheating and certificate compliance requirements need early confirmation.
- Unclear multi-organization permission boundaries may affect data isolation.

### 11.2 Open questions

- Should training plans support cross-company or external learner enrollment?
- Should course completion rules vary by course, plan, or role?
- Do certificates require electronic seals, QR verification, or validity periods?
- Do exams require time limits, random papers, anti-cheating, and retake rules?
- Which training modules need independent pages in the final product?

## 12. Milestones and Acceptance

| Milestone | Target date | Acceptance criteria |
| --- | --- | --- |
| Requirement confirmation | T+1 week | Confirm scope, roles, core flows, and reporting definitions |
| Prototype review | T+3 weeks | Complete main page prototypes and process review |
| Development and integration | T+8 weeks | Complete core feature development and external integrations |
| Pilot launch | T+10 weeks | Launch pilot organization and close pilot issues |
| Production launch | T+12 weeks | Complete full release, training, and acceptance |
