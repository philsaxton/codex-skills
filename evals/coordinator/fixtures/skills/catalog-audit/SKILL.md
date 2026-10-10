---
name: catalog-audit
description: Inspect a product catalog for reused identifiers and return source-backed conflicts.
---

# Catalog audit

Evaluation fixture only. A test child uses this fictional product-catalog skill to check that adding one menu row lets the coordinator assign a new role. It is not a shipped skill.

Read the complete tab-separated catalog. Group rows by exact `product_id`, preserving case. For every repeated identifier, give all source line numbers and each distinct product name; distinguish identical duplicate rows from conflicting names. Return findings without renaming, deduplicating, or editing products. A unique catalog is not evidence that its products exist elsewhere.
