# Brainstorm: Universal Agent Harness Skill

## Visión
Crear una "Skill" reutilizable (o librería interna) que implemente los 5 pilares de la Ingeniería de Arneses para cualquier proyecto de agentes IA, permitiendo que pasen de ser "chatbots con herramientas" a "sistemas operativos de agentes".

## Componentes Clave
1. **Detección de Bucles (MD5)**: 
   - Lógica de hashing para (tool_name + arguments).
   - Hook de interrupción (Circuit Breaker).
   - Inyección de advertencia sistémica.

2. **Artifact Index (Ground Truth Manager)**:
   - Base de datos de "hechos confirmados" durante la sesión.
   - Mecanismo de persistencia (JSON/SQLite).
   - Re-inyección automática en el System Prompt.

3. **Strategic Thinking Wrapper**:
   - Fase de deliberación previa obligatoria.
   - Evaluación de "Confianza de Plan" (Confidence Score).
   - Separación de hilos de "Planificación" vs "Ejecución".

4. **Context Compactor (ACC)**:
   - Algoritmo de resumen adaptativo basado en umbrales de turnos/tokens.
   - "Masking" de información técnica redundante.

5. **Observabilidad UEFS**:
   - Trazabilidad de cada paso del arnés (no solo del agente).
   - Métricas de "Ahorro de Tokens" por detección de bucles.

## Casos de Uso
- **Coding Agents**: Evitar que el agente intente arreglar el mismo bug 10 veces con la misma técnica.
- **Research Agents**: Mantener un índice de URLs ya visitadas y hallazgos clave.
- **Executive Assistants**: Recordar preferencias confirmadas durante la conversación para no volver a preguntar.

## Ventajas
- **Portabilidad**: Se puede mover de un proyecto a otro.
- **Estandarización**: Todos los agentes de la organización siguen el mismo rigor.
- **Ahorro Directo**: Menos loops = menos factura de API.
