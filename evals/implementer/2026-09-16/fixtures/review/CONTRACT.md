# Proposed retry change

Make the payment submission client retry failed requests three times. Treat every non-200 response as retryable. No behavior for duplicate charges, idempotency, rate limits, or timeout responses is defined. Acceptance: failures retry three times; success returns.
