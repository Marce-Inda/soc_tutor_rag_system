# 🛡️ Blueprint de Evaluación para Agentes de IA Multiagente

Esta plantilla define el estándar de oro para evaluar sistemas multiagente de IA (MAS), pasando de pruebas anecdóticas a un pipeline de ingeniería repetible.

---

## 📋 Los 5 Niveles de Evaluación

### 1. Nivel de Contratos (Estructura)
**Objetivo:** Garantizar que los componentes no se rompan por errores de formato.
*   **Validación de Schema:** Uso de Pydantic o JSON Schema para cada agente.
*   **Fail-Closed Logic:** Si la estructura es inválida, el sistema debe capturar el error antes de entregarlo al usuario.

### 2. Nivel Golden Tests (Sustancia Semántica)
**Objetivo:** Medir si la IA "sabe de lo que habla".
*   **Keyword Match (Cobertura):** Definir un set de términos técnicos obligatorios (`expected_concepts`) por caso.
*   **Embedding Similarity:** Comparar la respuesta del agente contra una respuesta "maestra" humana usando similitud de coseno (> 0.75).

### 3. Nivel de Trazas (Comportamiento y Lógica)
**Objetivo:** Verificar que el razonamiento sigue el flujo esperado.
*   **Tool Consistency:** ¿Invocó el agente las herramientas necesarias (`expected_tools`)?
*   **Step Analysis:** Validar que los pasos intermedios (*Thought/Reasoning*) sean coherentes con la observación anterior.

### 4. Métricas de Interacción (Calidad de Agentes)
**Objetivo:** Evaluar la fidelidad y la orquestación.
*   **Faithfulness (Fidelidad RAG):** ¿La respuesta final está respaldada por documentos reales o es una alucinación?
*   **Validator Effectiveness:** Tasa de aprobación/rechazo del agente supervisor.

### 5. Análisis de Regresión (Garantía de Estabilidad)
**Objetivo:** Detectar degradación al cambiar prompts o modelos.
*   **Baseline Comparison:** Guardar un archivo de referencia (`eval_baseline.json`).
*   **Delta Monitoring:** Alertar si el score técnico o la cobertura semántica caen más de un 5% (Delta < -0.05).

---

## 🛠️ Guía de Implementación Rápida

### A. Estructura del Dataset (`eval_dataset.json`)
```json
{
  "id": "test-001",
  "input": "...",
  "expected_concepts": ["termino1", "termino2"],
  "expected_tools": ["herramienta_A"],
  "min_score": 80
}
```

### B. Ciclo de Ejecución
1.  **Run:** Ejecutar el pipeline completo sin caché.
2.  **Score:** Calcular métricas automáticas para los 5 niveles.
3.  **Compare:** Ejecutar script de regresión contra la última versión estable.
4.  **Report:** Generar reporte Markdown para revisión humana.

---
> **"Lo que no se mide, no se puede mejorar. Lo que no se evalúa automáticamente, se rompe silenciosamente."**
