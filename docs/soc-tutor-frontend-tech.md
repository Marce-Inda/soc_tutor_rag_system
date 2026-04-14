# Technical Design: SOC Tutor Frontend

> Status: DRAFT
> Last updated: 2026-04-13

## Overview
A Next.js 14 application that communicates with a FastAPI (Python) backend. The frontend handles the game state, UI rendering, and user interactions, while the backend orchestrates the multi-agent reasoning and RAG lookups.

## Key Components

1. **Dashboard Shell**: The main layout using CSS Grid for the 3-column workstation architecture.
2. **Game Engine Controller**: A React context/store (Zustand) that manages scenario state, player metrics, and session history.
3. **Agent Bridge**: An API wrapper that sends player decisions to the orchestrator and parses the pedagogical response.
4. **Visualizer**: A node-graph component (React Flow) that renders the network/incident topology.
5. **Tactical Console**: A terminal-like component that renders technical logs and tool outputs.

## API Contracts

### Decision Submission
`POST /api/evaluate`
- **Request**:
  ```json
  {
    "scenario_id": "ghost-bank",
    "phase": "containment",
    "action": "ISOLATE_HOST",
    "target": "SRV-SWIFT-01",
    "metadata": { "tool_used": "ISOLATE_HOST" }
  }
  ```
- **Response**:
  ```json
  {
    "evaluación": "...",
    "explicación": "...",
    "mejor_páctica": "...",
    "puntos_delta": 25,
    "metrics": { "technical": 85, "methodology": 90 }
  }
  ```

## Data Flow
1. User selects a tool in the **Tactical Sidebar**.
2. Frontend sends action to **FastAPI Backend (HuggingFace)**.
3. Backend runs **UEFSOrchestrator** (Multi-agent ReAct + RAG).
4. Backend returns a **Clean Pedagogical Package**.
5. Frontend updates **Progress Bar** and renders the **Mentor Feedback**.

## Technical Implementation Details
- **Styling**: Tailwind CSS with custom themes.
- **Animations**: Framer Motion for "staggered" appearance of agents' feedback.
- **RAG Latency Mitigation**: Optimistic UI updates and "Agent Thinking" progress bars.
- **Deployment**: Vercel for Frontend, HuggingFace Spaces for Backend.
