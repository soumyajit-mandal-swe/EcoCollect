-- 1. Requests with their contributors and optional assigned centre.
SELECT r.id, u.name AS contributor, r.status, r.pickup_date, c.name AS centre
FROM collection_requests r JOIN users u ON r.user_id = u.id
LEFT JOIN recycling_centres c ON r.centre_id = c.id ORDER BY r.created_at DESC;

-- 2. Workflow distribution.
SELECT status, COUNT(*) AS requests FROM collection_requests GROUP BY status;

-- 3. Category inventory: quantities and weights (weights are totals per row).
SELECT c.name, SUM(i.quantity) AS units, SUM(i.estimated_weight) AS estimated_kg,
COALESCE(SUM(i.actual_weight), 0) AS actual_kg
FROM ewaste_categories c JOIN request_items i ON i.category_id = c.id GROUP BY c.id, c.name;

-- 4. Centre report. Pre-aggregate items to avoid double-counting requests.
SELECT c.name, COUNT(r.id) AS requests, COALESCE(SUM(w.actual_kg), 0) AS actual_kg
FROM recycling_centres c LEFT JOIN collection_requests r ON r.centre_id = c.id
LEFT JOIN (SELECT request_id, SUM(actual_weight) AS actual_kg FROM request_items GROUP BY request_id) w
ON w.request_id = r.id GROUP BY c.id, c.name;

-- 5. History and the person responsible for each change.
SELECT h.request_id, h.status, h.changed_at, u.name, h.note
FROM status_history h JOIN users u ON h.changed_by = u.id ORDER BY h.request_id, h.id;

-- 6. Pending requests with multiple item rows (HAVING after grouping).
SELECT r.id, COUNT(i.id) AS item_rows FROM collection_requests r
JOIN request_items i ON i.request_id = r.id WHERE r.status = 'Pending'
GROUP BY r.id HAVING COUNT(i.id) > 1;

-- 7. Users who have submitted a collection request (EXISTS).
SELECT u.id, u.name FROM users u WHERE EXISTS
(SELECT 1 FROM collection_requests r WHERE r.user_id = u.id);

-- 8. Transaction demonstration; use valid IDs and a future date in a scratch database.
-- START TRANSACTION;
-- SELECT status FROM collection_requests WHERE id = 1 FOR UPDATE;
-- UPDATE collection_requests SET status='Scheduled', centre_id=1, pickup_date='2027-01-01' WHERE id=1 AND status='Pending';
-- INSERT INTO status_history(request_id,status,changed_by,changed_at,note)
-- VALUES(1,'Scheduled',1,UTC_TIMESTAMP(),'Pickup scheduled');
-- COMMIT; -- Use ROLLBACK instead to discard both changes.
