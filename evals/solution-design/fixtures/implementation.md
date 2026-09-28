# Request

Implementation has hit the facts below. Use a design consultation to recommend how to continue, identify any required contract change, and separate work that can continue now from work waiting on a decision. Do not edit code or contact the contract owner.

## Current approved contract

An offline embedded device must decode four fixed binary record types from a documented wire format. It must reject invalid checksums and unknown type identifiers. The decoder has a 64 KB memory budget and must run without child processes or network access. Wire compatibility, the memory limit, and the execution restrictions are protected requirements.

The contract specifically selects ParseFrame 2.4 with a small stateless adapter. The project requires independent review and owner acceptance of semantic contract changes. The implementation team can repair defects within the accepted contract, build wire-format test fixtures, and inspect candidate designs locally.

## Implementation evidence

The adapter passes the first two record types. For the remaining two, ParseFrame rejects variable-length payloads before invoking adapter callbacks. A local reproduction with each of the four records confirms the rejection. The contract assumed callbacks saw the original bytes.

## Available alternatives and references

These are fictional authoritative fixture references, not claims about real products. They are the complete available references for this exercise; use them without web research.

- ParseFrame 2.4 manual: callbacks receive decoded fixed-width fields; variable-length records are unsupported. Extending the parser requires replacing its core buffering engine; there is no raw-record callback. A fork would take on the full parser and its 400 KB buffer allocation. The accepted contract's memory budget cannot be met by that fork.
- StreamParse 8 manual and project measurement: supports all four record types but has a minimum 256 KB working buffer. Its documented settings do not reduce this minimum.
- WireBridge 1 manual: supports the format through a helper daemon; no in-process interface exists.
- The project's wire-format specification defines exactly four record layouts with a two-byte type, a two-byte payload length, a bounded payload, and a fixed checksum algorithm. The largest complete record is 8 KB. Existing project code already supplies the checksum routine. General grammar support and streaming records larger than 8 KB are out of scope.

No alternative has been accepted and no production deployment or new installation is authorized.
