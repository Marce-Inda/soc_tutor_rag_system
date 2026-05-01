# ISO/IEC 27037:2012 - Digital Evidence Guidelines

## Scope
Provides guidelines for the specific activities in the handling of digital evidence: **Identification, Collection, Acquisition, and Preservation**.

## Fundamental Principles
1. **Integrity**: Evidence must not be altered during the forensic process.
2. **Authenticity**: Evidence must be what it purports to be.
3. **Reliability**: The methods used must be proven and verifiable.
4. **Auditability**: Every action must be documented (Chain of Custody).

## Key Processes
- **Identification**: Prioritizing evidence based on volatility (RFC 3227 - Order of Volatility). Recognition of devices like RAM (most volatile) to Hard Drives (least volatile).
- **Collection**: Physical gathering of devices or remote data collection.
- **Acquisition**: Creating forensic copies (images) using write blockers to prevent any modification to the original source.
- **Preservation**: Ensuring evidence remains unchanged in storage and maintaining the log of who handled it.

## Best Practices for Analysts
- **Chain of Custody**: Mandatory log of every person who handles the evidence and for what purpose.
- **Avoid Over-analysis**: Only perform analysis on the forensic copy, never the original.
- **Write Blocking**: Always use hardware or software write-blockers during acquisition.
