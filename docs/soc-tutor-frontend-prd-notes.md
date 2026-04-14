# PRD Notes: SOC Tutor Frontend UX/UI

## Raw Requirements
- User role: Analyst SOC.
- Single role demo.
- 3 scenarios in sequential order.
- Logic based on "The Responder" (tools, screen layout).
- Aesthetics: Dark mode, cyber/SOC look, visceral impact.
- Tutor output: Responses, guides, explanations based on player decisions.
- Metrics: Progress, points, penalties for bad decisions. No agent internal info.
- Backend: Free tier (HuggingFace Spaces recommended).

## Technical Constraints
- Zero-cost infra.
- Large LLM context handling (12k Groq TPM).
- No agent internal ReAct logs for the player (visibility limited to professional output).

## Inferred Patterns (from 'The Responder')
- Tools are categorized (Investigation, Containment, Analysis, Documentation).
- Each tool has time cost and risk level.
- Decisions have consequences (impact metrics).

## Selected Scenario Logic
- **Stage 1 (Beginner)**: Brecha GDPR: Newsletter en CC.
- **Stage 2 (Intermediate)**: APT Operation Ghost-Bank.
- **Stage 3 (Advanced)**: Fintech IDOR.

## Architecture Options
- **Option A**: Client-side only with mocked responses (Fastest, zero cost, but static).
- **Option B**: Full-stack Next.js + FastAPI on HuggingFace Spaces (Functional, realistic, free).
- **Option C**: Mobile-first Web App (More accessible, but more effort for dashboard-style tools).

**Selected**: **Option B**.
- *Pros*: Shows real multi-agent power. Free infrastructure. High technical depth.
- *Rationale*: For a specialization graduation project, real-time AI reasoning is the key differentiator.
