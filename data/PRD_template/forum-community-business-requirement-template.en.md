# Forum Community System Business Requirement Template
> For forum and community scenarios such as board management, thread publishing, replies, interactions, user growth, content moderation, report handling, search, recommendation, and community analytics.  
> Replace the prompts in `[]` with real business content; remove items that are not applicable.

## 1. Basic Information

| Field | Content |
| --- | --- |
| Template name | Forum Community System Business Requirement Template |
| Requirement name | [Interest community forum build] |
| Project | [Enter the project name] |
| Requirement type | New build / Optimization / Refactor |
| Priority | High / Medium / Low |
| Proposing department | [Enter the proposing department] |
| Requester | [Enter the requester] |
| Request date | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Business Background

### 2.1 Background summary

[Describe the forum community background, current communication approach, and reason for building the system]

Description: User discussions, experience sharing, and Q&A content are currently scattered across chat groups, spreadsheets, and temporary documents. Content is hard to retain, search is weak, and policy violations rely on manual patrol. A forum community system similar to Tieba is needed to support threaded discussions, board governance, content moderation, and community analytics.

### 2.2 Current pain points

- [Discussion content is hard to structure, retain, and search later]
- [Boards, threads, replies, and user relations lack unified management]
- [Violation discovery and handling are not timely, and moderation lacks audit trails]
- [Trending content, active users, and community quality lack dashboards]

## 3. Business Objectives

### 3.1 Business objectives

- [Build a board and thread structure organized by interest or business topic]
- [Support a closed interaction loop for posting, replying, liking, collecting, following, and notifications]
- [Build content governance for reports, moderation, bans, appeals, and operation audits]
- [Accumulate community operation data for recommendation and operating decisions]

### 3.2 Quantified metrics

- [Average time from publishing to visibility within 3 seconds]
- [Reduce average moderation handling time by 50%]
- [Improve community search hit rate to 90%]
- [Track daily active users and post volume by core board]

## 4. Business Scope

### 4.1 In scope

- Board management and permission configuration
- Thread publishing, editing, deletion, pinning, and featured posts
- Replies, comments, nested replies, and interactions
- User profile, following, levels, points, and badges
- Reports, moderation, blocking, bans, and appeals
- Search, sorting, recommendation, and analytics dashboards

### 4.2 Out of scope

- Instant messaging group chat
- Complex short-video authoring tools
- External advertising delivery system
- Fully automated AI content judgment

## 5. Roles and Core Scenarios

### 5.1 Target roles

- Visitor: browse public boards and threads, search content
- Registered user: publish threads, reply, like, collect, follow, and report
- Board moderator: manage board rules, pin/feature posts, and handle violations
- Reviewer: review new posts, reports, and sensitive content
- Operator: configure recommendations, campaigns, tags, and dashboards
- System administrator: maintain permissions, dictionaries, sensitive words, and system parameters

### 5.2 Core business scenarios

1. A user enters the forum home page and navigates to an interesting thread by board, hot list, or search.
2. A registered user publishes a thread in a target board and uploads images or attachments.
3. Other users reply, like, collect, or follow the author, and the system sends interaction notifications.
4. A user reports violating content, and a reviewer handles it in the moderation console with a recorded reason.
5. A moderator pins or features a quality post, while an operator configures recommendation slots.
6. Management views post volume, reply volume, active users, reports, and moderation efficiency.

## 6. Functional Requirements

### 6.1 Feature overview

[Summarize the core capabilities to be built for the forum system]

Description: This requirement covers seven capability groups: board governance, content publishing, interactions, user growth, moderation and risk control, search and recommendation, and community analytics.

### 6.2 Feature details

#### 6.2.1 Board and moderator management

- Description: Maintain board categories, board profiles, rules, moderators, and access permissions.
- Trigger: An operator creates or adjusts a board.
- Business rules / logic:
-   Support board creation, disabling, merging, sorting, and visibility configuration
-   Support board rules, announcements, tags, and moderator permissions
-   Support board statistics and anomaly alerts
- Inputs: Board name, category, rules, moderators, permission scope
- Outputs: Board detail, announcement, moderator list, statistics
- Exceptions: Duplicate board name, deletion blocked when posts exist, permission conflict warnings

#### 6.2.2 Thread publishing and content editing

- Description: Support thread publishing, drafts, rich text, images, attachments, and tags.
- Trigger: A user clicks publish or edit.
- Business rules / logic:
-   Support title, body, images, attachments, tags, and anonymous options
-   Support draft saving, edit history, deletion, and recovery
-   Support pinning, featuring, locking, and burying posts
- Inputs: Title, body, board, tags, attachments, author
- Outputs: Thread, draft, edit record, management status
- Exceptions: Sensitive word hit, attachment limit exceeded, duplicate posting, no permission

#### 6.2.3 Replies, comments, and interactions

- Description: Support replies, nested comments, likes, collections, follows, and notifications.
- Trigger: A user interacts with a thread or reply.
- Business rules / logic:
-   Support reply sorting, quoting, folding, and deletion
-   Support likes, collections, following authors/threads, and interaction notifications
-   Support blocking users and not-interested feedback
- Inputs: Thread, reply, user, interaction type
- Outputs: Reply list, interaction record, notification
- Exceptions: Frequent action limit, blocked user restriction, content deleted

#### 6.2.4 User growth and community assets

- Description: Maintain user profile, levels, points, badges, and contribution records.
- Trigger: A user completes posting, interaction, check-in, or campaign tasks.
- Business rules / logic:
-   Support point rules, level rules, badge issuing, and task configuration
-   Show posts, collections, following, and followers on user profile
-   Support violation point deduction, mute, and credit recovery
- Inputs: User profile, behavior record, point rule, badge rule
- Outputs: User profile, point ledger, level result, badge record
- Exceptions: Point farming, point rollback, account anomaly

#### 6.2.5 Moderation and report handling

- Description: Handle sensitive content, reports, manual reviews, bans, and appeals.
- Trigger: Content is published, reported, or hits a rule.
- Business rules / logic:
-   Support pre/post-publish moderation, sensitive words, and image review
-   Support report acceptance, conclusion, penalty action, and notification
-   Support bans, mutes, content blocking, appeals, and operation audit
- Inputs: Content, report reason, moderation rule, handler
- Outputs: Moderation result, penalty record, appeal record, audit log
- Exceptions: False-positive appeal, duplicate report, moderation timeout, penalty reversal

#### 6.2.6 Search, recommendation, and analytics

- Description: Provide content search, hot lists, recommendation slots, and community data.
- Trigger: A user searches content or an operator views data.
- Business rules / logic:
-   Support search by board, keyword, tag, author, and time
-   Support hot thread list, recommendation slots, featured area, and campaign entry
-   Support dashboards for posts, active users, reports, and moderation efficiency
- Inputs: Threads, replies, tags, user behavior, moderation records
- Outputs: Search results, hot list, recommendation list, analytics report
- Exceptions: Index delay, recommended violating content, incomplete permission filtering

## 7. Pages and Processes

| Page / entry | Entry | Key elements | Main actions | Flow |
| --- | --- | --- | --- | --- |
| Forum home | User entry | Recommended boards, hot list, search box, campaign entry | Search, enter board, view hot threads, sign in/up | A user enters the home page and opens threads by interest or hot list. |
| Board detail | Board entry | Board announcement, rules, thread list, filters and sorting | Publish thread, follow board, filter, view thread | A user browses threads in a board and starts discussion. |
| Thread detail | Thread list / search result | Main post, replies, nested replies, interactions, recommendations | Reply, like, collect, report, follow author | A user reads and interacts with a thread; the system records relations and notifications. |
| Post editor | Publish button | Title, body, images, attachments, tags, publish settings | Save draft, preview, publish, edit | A user edits content, and the system validates sensitive words and permissions before publishing. |
| Moderation console | Admin backend | Pending content, report list, handling records, penalty actions | Review, block, ban, reject, approve, notify | A reviewer handles content and leaves operation records. |
| Community analytics dashboard | Operations backend | Post volume, active users, hot threads, report volume, moderation efficiency | Filter, drill down, export, configure recommendations | Operators review community quality and growth. |

## 8. Business Rules and Data

### 8.1 Business rules / logic

- Posting frequency limits can be configured by user level within each board.
- Publishing requires sensitive word, image safety, and permission checks.
- Deleted or blocked content is hidden from normal users, while audit records remain in the admin backend.
- Report handling must record handler, time, conclusion, and penalty action.
- Pinning, featuring, and recommendation slots must be authorized by role.

### 8.2 Key data objects

- Board: id, name, category, rules, moderators, status, visibility scope
- Thread: id, board, title, body, author, status, interaction count, publish time
- Reply: id, thread, parent reply, author, body, status, floor number
- User relation: follow, block, collection, like, view record
- Moderation record: content, rule, hit item, handler, conclusion, penalty action
- Operation config: recommendation slot, hot list rule, tag, campaign entry

## 9. Non-functional Requirements

- Performance: common home and thread detail queries return within 3 seconds; hot lists may be cached.
- Security: protect identity, sensitive words, image content, and API frequency.
- Usability: key flows such as posting, replying, and reporting need retry handling and clear prompts.
- Audit: moderation, bans, deletion, recovery, and recommendation operations must be logged.
- Extensibility: boards, tags, points, and moderation rules need configurable extension.

## 10. Integrations and Dependencies

- Unified identity / SSO
- Object storage or attachment service
- Message notification service
- Content safety / image review service
- Search engine service
- Data warehouse / BI

## 11. Risks and Open Questions

### 11.1 Risks

- Open communities may produce spam, ads, and violating content; governance strategy must be clear.
- Overly strict sensitive word and moderation rules may hurt normal discussion.
- Opaque hot list and recommendation rules may create operations disputes.
- Historical content migration may require data cleansing and permission mapping.

### 11.2 Open questions

- Should visitors be allowed to post, or only registered users?
- Should posts be reviewed before publishing or inspected after publishing?
- What are the permission boundaries and appointment process for board moderators?
- Are levels, points, badges, and check-ins required?
- Who maintains hot list, recommendation slot, and search ranking rules?

## 12. Milestones and Acceptance

| Milestone | Target date | Acceptance criteria |
| --- | --- | --- |
| Requirement confirmation | T+1 week | Confirm roles, scope, core flows, and moderation strategy |
| Prototype review | T+3 weeks | Complete prototypes for home, board, thread, editor, and moderation console |
| Development and integration | T+8 weeks | Complete core features and integrations with content safety and search |
| Pilot launch | T+10 weeks | Pilot selected boards and close issues |
| Production launch | T+12 weeks | Complete full release, operation configuration, and acceptance |
