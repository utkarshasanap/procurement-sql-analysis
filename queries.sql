-- Q1. Total spend per category (PO value)
SELECT s.category, COUNT(p.po_id) AS po_count, ROUND(SUM(p.po_amount),2) AS total_spend
FROM purchase_orders p JOIN suppliers_legacy s ON p.supplier_id = s.supplier_id
GROUP BY s.category ORDER BY total_spend DESC;

-- Q2. Top 5 suppliers by spend
SELECT s.supplier_name, ROUND(SUM(p.po_amount),2) AS total_spend
FROM purchase_orders p JOIN suppliers_legacy s ON p.supplier_id = s.supplier_id
GROUP BY s.supplier_id, s.supplier_name ORDER BY total_spend DESC LIMIT 5;

-- Q3. Duplicate suppliers (same name more than once)
SELECT supplier_name, COUNT(*) AS occurrences FROM suppliers_legacy
GROUP BY supplier_name HAVING COUNT(*) > 1;

-- Q4. Missing values (data validation)
SELECT SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS missing_email,
       SUM(CASE WHEN payment_terms IS NULL THEN 1 ELSE 0 END) AS missing_payment_terms
FROM suppliers_legacy;

-- Q5. Migration check: row counts
SELECT (SELECT COUNT(*) FROM suppliers_legacy) AS legacy_count,
       (SELECT COUNT(*) FROM suppliers_new)    AS new_count;

-- Q6. Migration check: records in legacy but missing in new
SELECT COUNT(*) AS missing_in_new FROM suppliers_legacy l
LEFT JOIN suppliers_new n ON l.supplier_id = n.supplier_id WHERE n.supplier_id IS NULL;

-- Q7. Migration check: records present in both but with field mismatches
SELECT COUNT(*) AS mismatched_records FROM suppliers_legacy l
JOIN suppliers_new n ON l.supplier_id = n.supplier_id
WHERE l.country <> n.country OR IFNULL(l.payment_terms,'') <> IFNULL(n.payment_terms,'');

-- Q8. POs with no invoice
SELECT COUNT(*) AS pos_without_invoice FROM purchase_orders p
LEFT JOIN invoices i ON p.po_id = i.po_id WHERE i.invoice_id IS NULL;

-- Q9. PO vs invoice amount mismatch
SELECT COUNT(*) AS amount_mismatches FROM purchase_orders p
JOIN invoices i ON p.po_id = i.po_id WHERE ROUND(p.po_amount,2) <> ROUND(i.invoice_amount,2);
