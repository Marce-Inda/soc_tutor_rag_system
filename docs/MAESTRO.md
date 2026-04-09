# DOCUMENTO MAESTRO - SOC-Tutor-RAG

## 1. Visión del Proyecto
Desarrollar un sistema de feedback pedagógico basado en RAG que asista a analistas SOC en entrenamiento, utilizando documentación técnica oficial como base de verdad.

## 2. Arquitectura de Componentes
- **Módulo 1: RAG Engine**: Ingesta y búsqueda vectorial sobre NIST, MITRE y OWASP.
- **Módulo 2: Agentes Especializados**: 
    - `Analista`: Evaluación técnica (ReAct).
    - `Explicador`: Feedback pedagógico adaptativo.
    - `Validador`: Control de calidad y alucionaciones.
- **Módulo 3: Orquestación**: Coordinación del flujo y persistencia de memoria.
- **Módulo 4: Observabilidad**: Tracing de métricas, costos y reasoning chains.

## 3. Estándares de Producción
- **Tipado**: Uso estricto de Pydantic.
- **Testing**: Cobertura >70% en lógica de agentes.
- **Despliegue**: Dockerización completa.
- **Seguridad**: Guardrails dinámicos.

## 4. Roadmap v1.1
- [ ] Integración con Dashboard Web.
- [ ] Soporte para Multi-idioma dinámico.
- [ ] Evaluación automática con RAGAS.
- [ ] Conexión nativa con Firebase para logs de producción.
