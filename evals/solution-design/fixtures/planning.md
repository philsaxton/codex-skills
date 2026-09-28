# Request

Help plan a migration runner for our service. We were thinking of writing a Python executor with its own history table. Give us a recommended approach and enough of an outline to hand to the contract author. This is planning only.

## Project requirements

The deployment owner requires ordered migrations, durable migration history, stopping on failure, and a distinct database login for each migration. The deployment environment already has IPv4 database connectivity. Nine migrations require the schema-owner login and one requires the administrator login. The migration bodies use RESET ROLE, which returns to the connection's login role. No production experiment or dependency installation is authorized.

The implementation notes say to keep SQL files unchanged. That note came from the previous author to make review easier; the deployment owner has not made it a requirement. No tool or runner has been selected by the owner.

## Existing project capability

The repository pins MigrateKit 3.2 for local development. Its maintained distribution and license are already accepted for the deployment environment. No custom migration history implementation exists.

## MigrateKit 3.2 manual supplied by the project

This is fictional, authoritative fixture documentation, not a claim about a real product.

- The apply command reads ordered SQL migration files and tracks successful application in a durable history table.
- Its manifest can specify a connection credential reference per file. Each file runs in a fresh connection authenticated as that login. It does not implement this setting with SET ROLE in a shared connection.
- The history table is managed through a separate deployment connection. Migration logins need no write privilege on that table.
- Apply stops at the first failure and records only completed migrations. Transaction and rollback behavior follow each migration's declared transaction setting.
- Credential references resolve from the deployment platform's existing secret store. Credentials do not belong in the manifest.

No hosted feasibility run has occurred. The provided documentation is the complete available tool reference for this exercise; use it without web research.
