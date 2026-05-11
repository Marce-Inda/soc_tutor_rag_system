# Constraints: SOC Tutor Frontend

## Technical Constraints
1. **Zero-Cost Infrastructure**: Must use free services (GitHub Pages, Vercel, Netlify free tiers).
2. **Low Latency vs. LLM Lag**: LLM calls take time; the UI must handle long wait times with engaging "thought" visualizations.
3. **Backend Communication**: Since the current system is Python, we need a way to connect the JS frontend (Vite/NextJS) with the Python logic.
   - Option A: FastAPI on Render/HuggingFace Spaces (Free).
   - Option B: Static mock-up for the demo if server uptime is risky (Not ideal).

## UI/UX Constraints
1. **Accessibility**: High contrast (typical for SOC themes) but legible fonts.
2. **Mobile-Responsive**: The jury might view it on a phone or tablet.
3. **Information Density**: Cybersecurity dashboards are dense; we must avoid clutter while showing technical data.

## Strategic Restrictions
- **"Manager of Drafts" Paradigm**: The UI cannot allow the user to just "click through". It must encourage critical thinking.
