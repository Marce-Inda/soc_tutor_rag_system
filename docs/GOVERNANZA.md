# GOVERNANZA Y ÉTICA - SOC-Tutor-RAG

## 1. Protección de Datos (LGPD/GDPR)
- **Anonimización**: Todas las IPs y hostnames en la simulación son ficticios.
- **Privacidad**: No se almacenan datos personales de los jugadores, solo sus perfiles de nivel técnico.
- **Tratamiento de Logs**: Los logs de depuración se limpian cada 30 días.

## 2. Ética de la IA
- **Grounding**: El sistema tiene prohibido generar feedback sin una fuente técnica citada.
- **Tono**: El feedback debe ser estrictamente constructivo.
- **Alucinaciones**: El Agente Validador actúa como guardián final contra información técnica falsa.

## 3. Determinismo
- **Semillas (Seeds)**: Para entornos de evaluación, se debe fijar la semilla `random.seed(42)` para garantizar resultados consistentes.
- **Control de Temperatura**: El LLM opera con `temperature=0.1` para minimizar la variabilidad técnica.

## 4. Gobernanza del Conocimiento
- **Fuentes**: Solo se permiten documentos de fuentes oficiales (NIST, MITRE, CISA, OWASP).
- **Actualización**: La base vectorial se debe re-indexar trimestralmente.
