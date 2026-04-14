# Strategy Blueprint: SOC Tutor Frontend Architecture

## Mission
Create a visually stunning, pedagogically effective, and technically sound frontend that showcases the SOC Tutor multi-agent reasoning capabilities to a professional jury.

## Agent Representation in UX
- **Analyst AI**: Represented as a "Search & Discovery" node. Shows MITRE/NIST lookups.
- **Governance AI**: Represented as a "Policy Guard" node. Shows compliance checks.
- **Explainer AI**: Represented as the "Teacher Console". Provides the human-readable narrative.
- **Validator AI**: Represented as a "Quality Seal". Animates the rejection/approval of drafts.

## Topología de UX (Interaction Flow)
1. **The Briefing (Intro)**: Cinematic introduction to the incident.
2. **The Command Center (Main)**: 
   - Left Sidebar: Tactical Feed (Real-time logs from agents).
   - Center: Canonical Incident Object (CIO) visualization.
   - Right Sidebar: Action Console & Draft Panel.
3. **The Debriefing (Results Screen)**:
    - **6D Radar Chart**: Un gráfico radial que muestra el desempeño en las 6 dimensiones (Técnica, Estratégica, Ética, Comunicativa, Resiliencia y Aprendizaje).
    - **Progression Report**: Un análisis de cómo el jugador mejoró (o falló) a través de las fases del escenario.
    - **Jury Export**: Opción de generar un resumen de la sesión para que el jurado vea el "pedigree" del estudiante.

## Roadmap Strategic
1. **Alpha**: Static mockups to finalize the aesthetic (Neon/Dark SOC).
2. **Beta**: Interactive Vite app using local state (Simulated scenario).
3. **v1.0**: API integration with the Python backend.
