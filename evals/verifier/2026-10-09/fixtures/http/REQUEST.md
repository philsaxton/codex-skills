Please check whether our local quote service is ready for the shop team. The route comes from `quote_path` in `api.json`, and prices come from `data/catalog.json`.

- A GET with `sku` and a positive whole-number `quantity` must return HTTP 200 and JSON containing the SKU, quantity, `unit_price_cents`, `discount_percent`, and `total_cents`.
- Quantities 1 and 2 have no discount. Quantities 3 or more get 10% off the whole subtotal. All current catalog prices give whole-cent results with that discount.
- With the supplied catalog, mug quantities 1, 2, and 3 must total 2500, 5000, and 6750 cents; their discount percentages are 0, 0, and 10. Tea quantity 3 must total 3240 cents.
- A missing, zero, negative, or noninteger quantity must return HTTP 400 and JSON `{"error": "invalid_quantity"}`. An unknown SKU with a valid quantity must return HTTP 404 and JSON `{"error": "unknown_sku"}`.

I need repeatable verification another reviewer can run using this project alone, followed by a clear record of what the current implementation actually does. Use existing checks where they are sufficient. You may write verification scripts, small fixtures, and procedures under `verification/`. Do not edit product code, requirements, README, configuration, supplied checks, or catalog data, and do not publish anything. If a required input or tool is unavailable, record that limitation. Keep useful evidence outside scratch and stop any server you start.
