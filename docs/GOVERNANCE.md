# GOVERNANCE AND ETHICS - SOC-Tutor-RAG

## 1. Data Protection (GDPR)
- **Anonymization**: All IPs and hostnames in the simulation are fictitious.
- **Privacy**: No personal data of the players is stored, only their technical skill level profiles.
- **Log Handling**: Debug logs are cleared every 30 days.

## 2. AI Ethics
- **Grounding**: The system is prohibited from generating feedback without a cited technical source.
- **Tone**: Feedback must be strictly constructive.
- **Hallucinations**: The Validator Agent acts as the final guardian against false technical information.

## 3. Determinism
- **Seeds**: For evaluation environments, the seed `random.seed(42)` must be set to ensure consistent results.
- **Temperature Control**: The LLM operates with `temperature=0.1` to minimize technical variability.

## 4. Knowledge Governance
- **Sources**: Only documentation from official sources (NIST, MITRE, CISA, OWASP) is allowed.
- **Updates**: The vector base must be re-indexed quarterly.
