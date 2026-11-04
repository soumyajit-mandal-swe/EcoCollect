# EcoCollect viva guide

## Explain the project in 30 seconds

EcoCollect connects households with recycling centres. A user lists electronic items and a collection address. An administrator schedules pickup, assigns a centre, records actual collected weight and marks recycling complete. MySQL preserves the requests, item inventory and workflow history. The dashboard uses SQL aggregates, so it changes when records change.

## Common questions

**Why MySQL?** The data has clear relationships and needs referential integrity, transactions and reporting. MySQL supports these directly with InnoDB and SQL. It also matches the college requirement and runs locally.

**What is a primary key?** A column that uniquely identifies a row. `users.id` is an auto-increment integer primary key. It cannot be NULL or duplicated.

**What is a foreign key?** A reference to another table's primary key. `collection_requests.user_id` references `users.id`. MySQL rejects requests pointing to nonexistent users.

**Explain one-to-many relationships.** One user can submit many requests. One request contains many items and many history events. One category classifies many item rows. One centre receives many requests.

**Why separate request_items?** A request can have different categories, conditions and quantities. Repeating columns such as item1, item2 and item3 would violate the intended relational design and limit the number of items.

**What does quantity mean?** It is the number of physical units in one row. Both weight fields are the TOTAL for that row. We do not multiply those weights by quantity again.

**What is NULL?** A missing or not-yet-known value. Actual weight is NULL before collection; it is not zero. Centre and pickup date are NULL before scheduling. Reports use `COALESCE` to show zero for an empty aggregate.

**How is 1NF satisfied?** Each column holds one value. Each item and each history event has its own row; there are no repeating groups.

**How is 2NF satisfied?** The tables use single-column primary keys, so non-key attributes have no partial dependency on a composite key.

**How is 3NF satisfied?** User contact information stays in users, category names in categories and centre details in centres. Requests store foreign keys rather than duplicating those descriptions. Current request status is an intentionally maintained snapshot of the latest history event; both are written in one transaction.

**Which joins do you use?** INNER JOIN combines valid related records, for example items and categories. LEFT JOIN retains requests without a centre and centres without requests.

**Why group item weights before joining centres?** Joining raw items repeats each request once per item. Counting those rows would overcount requests. We first aggregate weights per request, then join that one-row-per-request result to the centre report.

**What is a transaction?** An all-or-nothing group of database changes. Updating request status and inserting the history event must succeed together. A SQLAlchemy commit persists both; an exception rolls back the active transaction.

**Explain ACID here.** Atomicity keeps status/history together. Consistency is supported by constraints and workflow validation. Isolation comes from InnoDB transactions and a row lock during workflow changes. Durability means committed records survive application restarts.

**What does SELECT FOR UPDATE do?** It locks the selected request while an administrator validates and changes the workflow. Two administrators cannot independently move the same old status forward at the same instant.

**Which rules are in MySQL versus Python?** MySQL enforces PK/FK, uniqueness, positive quantities/weights, allowed roles/conditions/statuses and required schedule fields for non-pending requests. Python enforces role access, ownership, legal next-step transitions, active centres, future scheduling and complete actual-weight entry. Direct privileged SQL can bypass application-only rules, so normal users never receive DB credentials.

**How are passwords stored?** Only Argon2 hashes are stored. Login verifies the supplied password against the stored hash. Plain passwords never go into a users row.

**How do frontend and backend communicate?** React fetches JSON from `/api`. Vite forwards these requests to FastAPI on port 8000. The bearer token identifies the user. FastAPI validates the input and executes parameterized SQLAlchemy queries against MySQL.

**Can a user become an administrator by changing the frontend?** No. The backend checks the role stored in the database on each protected call. Registration does not accept a role field. Hiding UI controls is only a usability feature.

**Where is CRUD?** Create: registration, requests, centres. Read: details, tables, charts. Update: workflow and centre edits. Delete: pending requests, with their item and history rows removed together. Processed requests cannot be deleted through the API.

**How do you prevent SQL injection?** SQLAlchemy binds input values as parameters. Search text is not concatenated into SQL statements. LIKE wildcards in search are escaped.

**How was it tested?** See TEST_RESULTS.md for actual results. Integration tests use real MySQL, with savepoints inside an outer rollback transaction. They cover authentication, authorization, multiple items, foreign keys, CHECK constraints, full workflow, reports and injected commit failure.

## Five-minute laboratory demonstration

1. Run `Start-EcoCollect.cmd`. Open `http://127.0.0.1:5173`.
2. Sign in as `soumyajit@example.com` / `EcoUser123!`. Show the user's dashboard and existing requests.
3. Create a request with an address, two different categories, conditions, quantities and estimated total weights. Show the Pending status and initial history event.
4. Sign out; sign in as `admin@example.com` / `EcoAdmin123!`. Search for the new request ID.
5. Assign an active recycling centre and choose tomorrow's pickup date. Submit and show the Scheduled history event.
6. Record an actual total weight for each row, then mark Collected. Mark Recycled and show the complete timeline.
7. Open Overview and Impact reports. Point out the actual-weight change and export CSV.
8. Open the ER diagram and SQL queries. Explain user→request→items and demonstrate one JOIN and one GROUP BY query.

Use fictional demo information only. Do not present estimated weights as measured recycling outcomes.
