# Parcel interchange protocol P3

This is the normative format for the fictional project.

- The CSV header and every row must use the positional order `parcel_id,destination,weight_g`. Consumers interpret column positions rather than discovering them from labels.
- `parcel_id` must be nonempty and unique within a batch. A repeated identifier rejects the entire batch before any output is published. Replacing an earlier row is forbidden.
- `destination` is a nonempty routing code. `weight_g` is a positive integer.
- This change retains protocol P3. Format changes need a separately authorized protocol revision.
