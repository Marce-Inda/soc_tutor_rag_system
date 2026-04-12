# MITRE ATT&CK v15: Key Updates for Cloud and Identity

## Overview
MITRE ATT&CK v15 (April 2024) enhances visibility into Cloud, Identity, and ICS tactics, emphasizing Actionable Detection Analytics.

## Key Expansions
1. **Cloud & Identity**:
    - Focus on **Token Protection** and CI/CD pipeline security.
    - Expansion of technique **T1072 (Software Deployment Tools)** to include **T1651 (Cloud Administration Command)** as a primary propagation method.
    - Improved data sources for identity providers (e.g., Okta logs).
2. **Generative AI**:
    - **T1588.007 (Obtain Capabilities: Artificial Intelligence)**: Tracking how adversaries use LLMs to develop malware or phishing content.
3. **Detection Engineering**:
    - Shift from pseudo-code to **Vendor-Specific Query Languages** (SPL, KQL) in technique pages.
    - Focus on detection within the **Execution** tactic.

## Critical Techniques for Analysts
- **T1651 (Cloud Administration Command)**: Using native cloud tools (AWS SSM, Azure Run Command) for lateral movement.
- **T1550.001 (Steal or Forge Kerberos Tickets)**: Focus on Identity persistence.
- **T1548.006 (Abuse Elevation Control Mechanism: Sudo and Sudo Caching)**: Privilege escalation tracking.
