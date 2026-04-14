# PRD: SOC Tutor Frontend "Analyst Workstation"

> Status: DRAFT
> Last updated: 2026-04-13

## Problem Statement
The SOC Tutor multi-agent engine needs a professional, visually impactful interface that allows a player to assume the role of a SOC Analyst, use investigation/containment tools, and receive AI-powered pedagogical feedback in a structured, game-like experience for an academic jury.

## Goals
- **Wow Factor**: Create a premium visual impression using a "Cyber-SOC" aesthetic.
- **Role Accuracy**: Match the tools and metrics of the "Technical Analyst" role from "The Responder".
- **Pedagogical Effectiveness**: Ensure the Tutor's feedback is the central anchor of the experience.
- **Deployment Ease**: Fully compatible with free-tier cloud hosting (Vercel/HuggingFace).

## User Flows

1. **Selection Screen**:
   - Player chooses one of the 3 scenarios. Level 1 starts automatically.
   - **Skip Stage Logic**: A global navigator allows jumping to Level 2 or 3 at any time to facilitate jury testing.
2. **Mission Briefing**:
   - High-impact mission objective presentation by the AI Mentor.
3. **Gameplay (Workstation)**:
   - Left Sidebar: Tool selection and inventory (NETSCAN, ISOLATE_HOST, etc).
   - Central Pane: Visual representation of the case (nodos/nube).
   - Bottom Console: Tactical execution output.
   - **Right Sidebar (The Mentor)**: Contextual, reactionary pedagogical feedback. Not a chat-bot, but an active advisor that evaluates each player decision.
4. **Results Screen**:
   - Breakdown of scores (Technical, Governance, Methodology).
   - Final debriefing.

## Functional Requirements
- **Scenario Sequencing**: Logic to handle 3 levels with progression.
- **Toolbox Interaction**: Ability to select and "execute" a tool on a target.
- **Asynchronous Feedback**: Loading states that simulate agent "thinking" or "reasoning".
- **Progress Tracking**: Points system with penalties for high-risk actions or methodology errors.
- **Evidence Management**: A "bag" to store discovered IOCs.

## Non-Functional Requirements
- **Zero-Latency Feel**: Animations hiding LLM latency.
- **Performance**: Lighthouse score > 90.
- **Aesthetics**: High contrast, neon accents, dark mode.
