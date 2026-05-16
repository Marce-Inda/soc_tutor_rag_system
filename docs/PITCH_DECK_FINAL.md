# Presentación Final: SOC Tutor RAG System

## Título y Presentación
```text
┌─────────────────────────────────────────────────────────┐
│  SOC TUTOR RAG SYSTEM                                   │
│  Simulador Multiagente para Entrenamiento de Analistas  │
│                                                         │
│  Bootcamp AI Engineer con Python                        │
│  Marcela Rosana Inda                                    │
│  Abril/Mayo 2026                                        │
└─────────────────────────────────────────────────────────┘
```

> **Objetivo Principal:** Demostrar el valor de negocio y la robustez de la arquitectura de IA frente al jurado.

---

## El Problema (El "Abismo" en la Educación SOC)
- **Simuladores estáticos:** No proporcionan feedback personalizado.
- **Alucinación Técnica (IA):** Los LLMs genéricos inventan logs y citan marcos normativos inexistentes.
- **Complacencia Pedagógica:** La IA convencional suele decir que "todo está bien" para evitar fricciones.
- **Fragilidad de Infraestructura:** Depender de un único proveedor de IA es un riesgo inaceptable para producción.

---

## La Solución (Ingeniería de IA)
**Un Motor Cognitivo Multi-Agente que:**
1. Evalúa decisiones contra documentación real (MITRE, NIST).
2. Usa herramientas reales (SIEM, EDR) para leer datos deterministas.
3. Adapta el feedback al nivel del jugador (Junior → Experto).
4. Es indestructible ante caídas de proveedores (Resiliencia Multi-Capa).

---

## Arquitectura del Sistema (Manager of Drafts)
No es un simple LLM. Son 5 agentes especializados con roles asimétricos:

| Agente | Función | Patrón de IA |
|--------|---------|--------------|
| **Guard (L1/L2)** | Filtra inyecciones maliciosas de prompt | Regex + Clasificador LLM |
| **Analista** | Investiga los logs reales (SIEM) | Ciclo ReAct (Thinking/Acting) |
| **Gobernanza** | Audita cumplimiento (GDPR, Ética) | Búsqueda RAG de Normativa |
| **Explicador** | Traduce técnica a pedagogía | Localización Dinámica |
| **Validador** | Juez de calidad (Anti-alucinación)| Juez Asimétrico + Criptografía |

---

## RAG y MCP (El Diferenciador Técnico)
Separamos el conocimiento teórico de la realidad del simulador:
- **Teoría (Cognitive RAG):** ChromaDB con MITRE ATT&CK y manuales NIST.
- **Realidad (Protocolo MCP):** El agente usa el Model Context Protocol para ejecutar herramientas reales (aislar un host, leer logs). 
- **Resultado:** *Zero-Hallucination.* El sistema lee evidencia forense real, no la inventa.

---

## Resiliencia Blindada (Cascada de 3 Niveles)
Si OpenAI o Google se caen, el entrenamiento continúa.
1. **Nivel Primario:** Google Gemini (Velocidad óptima).
2. **Nivel Respaldo:** Groq / Llama-3 (Latencia extrema).
3. **Validador Supremo:** NVIDIA NIM / Llama-3.3-70B (Alta precisión lógica).

- **Fail-Safe:** Incluso si todos fallan, se inyecta un *Emergency JSON* para no romper la experiencia del jugador.

---

## Desempeño y Métricas Financieras

| Métrica | Resultado | Valor para el Negocio |
|---------|-----------|-----------------------|
| **Fidelidad (Citas)** | 99.5% | Garantiza feedback veraz. Citas SHA-256. |
| **Costo por Turno** | ~$0.003 USD | Operación escalable y de bajo costo. |
| **Validez Estructural**| 100% | Sin caídas del Frontend gracias a Pydantic.|
| **Ahorro de Tokens** | 25% - 30% | Logrado razonando internamente en Inglés. |

---

## Demo en Vivo (Workstation)
*(Cambio a la pantalla del navegador)*
- **Demostrar:** Interfaz Next.js (Vercel).
- **Acción:** Ejecutar "Aislar Host" con un jugador Nivel 1.
- **Mostrar:** La consola de razonamiento (pensamiento del agente en vivo) y el reporte final validado.

---

## Conclusiones
- SOC Tutor transforma una IA estocástica en un entorno de aprendizaje **determinista y auditable**.
- Implementa estándares empresariales (MCP, Observabilidad, Caché Semántico).
- Listo para integración con simuladores mayores (The Responder).

**¡Gracias!**
*(Espacio para preguntas técnicas de la arquitectura).*
