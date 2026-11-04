# Verification record

Executed on 4 November 2026 on this Windows laptop, against MySQL Community Server 8.4.13 on loopback port 3307. No SQLite or mocked database was used.

## Automated integration tests

Command: `.\.venv\Scripts\python.exe -m pytest tests -q`

**Result: 6 passed in 2.67 seconds.** One non-failing dependency warning: Starlette reports that its httpx TestClient adapter is deprecated in favor of httpx2. Tests continue to run successfully with the pinned dependencies.

| Test group | Verified behavior |
|---|---|
| Registration and login | Registration, Argon2 hash storage, user login, invalid-password rejection, duplicate-email rejection |
| Permissions and ownership | Admin login, anonymous rejection, regular-user admin-route rejection, own-request isolation, denied access/deletion of another user's request |
| Complete workflow | Two item rows, persisted request, initial history, invalid transition rejection, past-date rejection, centre assignment, scheduling, weight completeness, collected/recycled changes, full history, live dashboard and centre aggregates |
| Integrity and rollback | Foreign-key rejection, quantity CHECK rejection, injected commit failure, rollback of both status and history |
| Centres and delete | Centre creation/edit/deactivation, inactive-centre scheduling rejection, pending-request deletion with item cleanup |
| Validation and health | MySQL health endpoint, negative weight, invalid category, empty items, parameterized search handling |

The first run exposed a test expectation mismatch: MySQL/PyMySQL reports CHECK violations as OperationalError (3819), rather than IntegrityError. The assertion was corrected and the API now maps that code to 422 instead of a database-unavailable response. The suite was rerun successfully. Test transactions preserve seeded rows, but auto-increment gaps are expected.

## Live application and browser checks

- Windows startup script successfully returned readiness for the frontend and MySQL-backed API.
- Admin login succeeded through the browser.
- Created request EC-0027 with two items through the UI, assigned GreenLoop Recycling, and scheduled pickup.
- Recorded actual weights of 2.30 kg and 0.45 kg and advanced to Recycled through the UI.
- A separate Python process/database session retrieved the persisted request, two items, four history entries, and 2.75 kg total actual weight.
- Dashboard/report total changed from 18 to 19 requests and 62.28 to 65.03 kg. Recycled count changed from 4 to 5.
- CSV downloaded through the actual Export CSV button; its contents contained 19 requests and 65.03 kg.
- Viewed recycling-centre cards and their assigned request counts.
- Desktop layout inspected at 1440 × 1000; mobile at 390 × 844. Fixed chart-label overlap and a screen-reader label causing horizontal page overflow. Tables retain intentional internal horizontal scrolling on mobile.
- Mobile navigation opened and navigated to the request list. Request search/status filtering checked against EC-0027.
- Screenshots are actual browser captures in `docs/screenshots/`.

The browser-created request is retained as an additional fictional demonstration record. Tests account for the ID gaps; these do not indicate missing application data.

## Build

`pnpm run build` successfully compiled the React production bundle. Vite reported a non-blocking JavaScript chunk-size advisory; it does not prevent startup or use. No external font or CDN request is required at runtime.

## Scope and limits

The seven-page PDF report was rendered and every page visually inspected for text, tables and screenshot layout.

- No load, penetration, power-loss recovery or concurrent-administrator stress test was performed.
- No Linux execution or fresh-laptop installation was tested; instructions are supplied.
- User registration and centre CRUD were verified by API integration tests; not every variant of these forms was submitted through the browser.
- No formal screen-reader audit was performed.
- The app is for local demonstration, not public production deployment.

## Reproduce

Start MySQL, configure `.env`, initialize/seed as needed, then run the commands in README.md. Integration fixtures use savepoints inside an outer rollback transaction and operate on the configured development database. Never point them at a production database.
