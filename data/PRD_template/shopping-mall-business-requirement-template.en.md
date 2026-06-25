# Shopping Mall Business Requirement Template
> For shopping mall scenarios such as product management, cart, checkout, payment, promotions, customer membership, after-sales service, inventory coordination, and commerce analytics.  
> Replace the prompts in `[]` with real business content; remove items that are not applicable.

## 1. Basic Information

| Field | Content |
| --- | --- |
| Template name | Shopping Mall Business Requirement Template |
| Requirement name | [Brand shopping mall build] |
| Project | [Enter the project name] |
| Requirement type | New build / Optimization / Refactor |
| Priority | High / Medium / Low |
| Proposing department | [Enter the proposing department] |
| Requester | [Enter the requester] |
| Request date | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Business Background

### 2.1 Background summary

[Describe the commerce background, sales channels, and reason for building the mall]

Description: Product sales currently rely on offline stores, communities, and manual ordering. Product information, inventory, discounts, orders, and after-sales are managed separately. A unified shopping mall is needed to support product display, member purchase, online payment, order fulfillment, after-sales service, and operations analytics.

### 2.2 Current pain points

- [Product information and price maintenance are scattered and inconsistent across frontend and backend]
- [Ordering, payment collection, inventory deduction, and shipping lack a closed loop]
- [Promotions rely on manual setup and settlement and are error-prone]
- [After-sales refunds, customer service handling, and operational data lack unified tracking]

## 3. Business Objectives

### 3.1 Business objectives

- [Build a unified product, SKU, price, and inventory display system]
- [Connect cart, order, payment, shipment, and after-sales into a transaction loop]
- [Support coupons, full reductions, flash sales, member prices, and campaign mechanics]
- [Accumulate customer, order, conversion, and repurchase data for operations decisions]

### 3.2 Quantified metrics

- [Increase checkout conversion by 15%]
- [Reach 98% successful payment rate]
- [Reduce average after-sales handling time by 40%]
- [Reduce promotion setup time by 60%]

## 4. Business Scope

### 4.1 In scope

- Product category, SPU/SKU, price, and listing management
- Search, filters, product detail, cart, and checkout
- Order creation, payment, cancellation, shipping, and receipt confirmation
- Coupons, full reductions, flash sales, member prices, and campaign pages
- Member profile, address, collections, browsing, and customer operations
- Refunds/returns, customer service collaboration, and commerce dashboards

### 4.2 Out of scope

- Cross-border customs and international tax calculation
- Complex marketplace merchant onboarding and settlement
- Offline POS reconstruction
- Building live commerce engine from scratch

## 5. Roles and Core Scenarios

### 5.1 Target roles

- Visitor: browse products, search, view campaigns, and sign in/up
- Member: add to cart, order, pay, view orders, and request after-sales
- Operator: maintain products, campaigns, recommendations, and content pages
- Customer service: handle inquiries, order exceptions, refunds/returns, and complaints
- Warehouse staff: receive orders, pick, ship, and sync tracking numbers
- Finance: view payments, refunds, reconciliation, and invoice data
- System administrator: maintain permissions, dictionaries, payment, and mall parameters

### 5.2 Core business scenarios

1. An operator lists products and configures inventory, prices, and campaign tags.
2. A user searches products, enters the detail page, adds items to cart, and submits an order.
3. The system calculates discounts, freight, and payable amount, and the user completes online payment.
4. Warehouse receives orders to ship, completes picking and shipping, and returns tracking numbers.
5. A user requests refund/return, and customer service reviews and triggers payment refund.
6. Operators view conversion, average order value, repurchase, inventory, and campaign performance data.

## 6. Functional Requirements

### 6.1 Feature overview

[Summarize the core capabilities to be built for the mall system]

Description: This requirement covers seven capability groups: products, cart, orders and payment, promotions, members and customers, after-sales, and analytics, forming a sellable, fulfillable, and operable commerce loop.

### 6.2 Feature details

#### 6.2.1 Product and SKU management

- Description: Maintain categories, brands, SPU/SKU, images, specs, prices, inventory, and listing status.
- Trigger: An operator creates or updates a product.
- Business rules / logic:
-   Support category hierarchy, brand, spec attributes, and SKU combinations
-   Support drafts, preview, listing/unlisting, sorting, and recommendation tags
-   Support price, inventory, purchase limits, and sales regions
- Inputs: Product data, SKU, price, inventory, images, tags
- Outputs: Product detail, SKU list, listing status
- Exceptions: SKU conflict, insufficient inventory, abnormal price, product referenced by orders

#### 6.2.2 Cart and checkout

- Description: Support adding to cart, selecting items, changing quantity, calculating discounts, and submitting orders.
- Trigger: A user clicks add to cart or checkout.
- Business rules / logic:
-   Support cart quantity, selected state, and invalid item prompts
-   Support coupons, full reductions, member prices, points deduction, and freight calculation
-   Support address, invoice, remarks, and delivery method selection
- Inputs: User, SKU, quantity, discount, address, delivery method
- Outputs: Cart, checkout sheet, payable amount
- Exceptions: Insufficient inventory, price change, unavailable discount, undeliverable address

#### 6.2.3 Orders and payment

- Description: Manage order creation, payment, cancellation, timeout closing, shipping, and receipt confirmation.
- Trigger: A user submits an order or payment callback arrives.
- Business rules / logic:
-   Support order state machine, payment record, refund record, and operation log
-   Support multiple payment methods, callback verification, and timeout close
-   Support split orders, partial shipping, and order remarks
- Inputs: Order, payment record, user, product, amount, status
- Outputs: Order detail, payment result, shipping task
- Exceptions: Duplicate payment, payment failure, order timeout, amount mismatch

#### 6.2.4 Promotion and member operations

- Description: Configure coupons, full reductions, flash sales, member prices, recommendation slots, and campaign pages.
- Trigger: An operator creates a campaign or a user participates.
- Business rules / logic:
-   Support campaign time, product scope, user scope, and stacking rules
-   Support coupon claiming, redemption, expiry, and threshold
-   Support campaign performance statistics and audience tags
- Inputs: Campaign, coupon, member level, audience, product scope
- Outputs: Discount result, campaign page, marketing report
- Exceptions: Campaign conflict, wrong stacking, inventory reservation

#### 6.2.5 After-sales and service collaboration

- Description: Handle refunds, returns, exchanges, complaints, and order exceptions.
- Trigger: A user submits after-sales request or service creates a ticket.
- Business rules / logic:
-   Support reason, evidence, review, return shipment, and refund
-   Support service notes, negotiation records, and timeout reminders
-   Support after-sales state flow and responsibility attribution
- Inputs: After-sales case, order, payment, evidence, service record
- Outputs: Review result, refund result, after-sales progress
- Exceptions: Out of after-sales period, item not returnable, refund failure, lost shipment

#### 6.2.6 Commerce analytics

- Description: Provide dashboards for sales, conversion, inventory, customers, and campaigns.
- Trigger: An operator or manager views data.
- Business rules / logic:
-   Support order amount, average order value, conversion, and repurchase statistics
-   Support product sales, inventory turnover, campaign ROI, and channel analysis
-   Support report export and metric definitions
- Inputs: Orders, payments, products, user behavior, campaign data
- Outputs: Operations dashboard, product report, customer analysis
- Exceptions: Data delay, insufficient permission, metric definition change

## 7. Pages and Processes

| Page / entry | Entry | Key elements | Main actions | Flow |
| --- | --- | --- | --- | --- |
| Mall home | Customer entry | Search, banners, categories, recommended products, campaign entry | Search, browse, open product, sign in/up | A user enters products from category, search, or campaign. |
| Product detail | Product list / search result | Images, price, specs, inventory, reviews, recommendations | Select spec, add to cart, buy now, collect | A user confirms product information and adds to cart or buys directly. |
| Cart and checkout | Cart entry | Items, discounts, address, delivery, invoice, amount details | Change quantity, select discount, submit order | The system validates inventory and price before creating an unpaid order. |
| Order center | Member center | Order list, status, tracking, payment, after-sales entry | Pay, cancel, confirm receipt, request after-sales | A user views order progress and handles payment or after-sales. |
| Mall operations backend | Admin entry | Products, campaigns, orders, after-sales, customers, reports | List product, configure campaign, handle exceptions, export reports | Operators maintain commerce operations and track results. |

## 8. Business Rules and Data

### 8.1 Business rules / logic

- Order submission must lock price, discounts, and inventory snapshots.
- Only paid orders can enter pending shipment; timed-out orders close and release inventory.
- Promotions must validate product scope, user scope, time, and stacking rules.
- Refund amount cannot exceed paid amount and must keep payment channel transaction records.
- Product price, inventory, order amount, and after-sales handling must keep operation logs.

### 8.2 Key data objects

- Product/SPU: id, name, category, brand, status, main image
- SKU: specs, price, inventory, purchase limit, sales region
- Cart: user, SKU, quantity, selected state, invalid state
- Order: order number, user, item details, amount, status, shipping address
- Payment: payment number, channel, amount, status, callback transaction
- After-sales case: order, reason, evidence, review status, refund status

## 9. Non-functional Requirements

- Performance: common home and product detail queries return within 3 seconds.
- Consistency: order, payment, inventory, and refund states need eventual consistency and traceability.
- Security: payment callbacks, user addresses, and order amounts require signature and permission checks.
- Usability: ordering, payment, and refund flows need retry handling and clear prompts.
- Audit: price, inventory, order, and after-sales changes must record operator and time.

## 10. Integrations and Dependencies

- Payment gateway
- Logistics tracking service
- Inventory / warehouse system
- SMS or message notification service
- Invoice / tax service
- Data warehouse / BI

## 11. Risks and Open Questions

### 11.1 Risks

- Complex promotion stacking may cause pricing errors.
- Payment and inventory inconsistency can affect fulfillment and service experience.
- Peak campaigns may create inventory reservation and ordering pressure.
- Unclear after-sales policy can cause service handling disputes.

### 11.2 Open questions

- Should multi-warehouse inventory and split shipment be supported?
- Can coupons, full reductions, and member prices be stacked?
- How should order timeout closing and inventory release time be configured?
- Do refunds require original-route refund and manual review?
- Are invoices, points, member levels, and reviews required?

## 12. Milestones and Acceptance

| Milestone | Target date | Acceptance criteria |
| --- | --- | --- |
| Requirement confirmation | T+1 week | Confirm transaction loop, promotion rules, inventory, and after-sales policy |
| Prototype review | T+3 weeks | Complete home, detail, checkout, order, and backend prototypes |
| Development and integration | T+8 weeks | Complete integrations with payment, inventory, logistics, and notifications |
| Pilot launch | T+10 weeks | Gray launch selected products and users |
| Production launch | T+12 weeks | Complete full release, operation configuration, and acceptance |
