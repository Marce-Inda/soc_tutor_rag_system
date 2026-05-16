# Guion Hablado: Defensa de SOC Tutor RAG System

**Consejo de Presentación:** Las diapositivas deben tener poco texto (solo para apoyo visual). Tu voz es la que lleva la narrativa fuerte. Usa un tono de voz seguro; estás presentando un sistema de grado de producción, no un proyecto estudiantil.

---

### [Slide 1] Título y Presentación
**Tú dices:** 
"Hola a todos, soy Marcela Inda. Hoy vengo a presentarles **SOC Tutor RAG System**. A simple vista, podría parecer un videojuego o un simulador para entrenar analistas de ciberseguridad... pero debajo del capó, es un **Motor Cognitivo Multi-Agente** diseñado para resolver uno de los problemas más costosos en la educación tecnológica hoy en día."

---

### [Slide 2] El Problema
**Tú dices:**
"¿Cuál es este problema? El 'Abismo' en la educación SOC. Hoy en día, entrenar a un analista es caro y requiere simuladores estáticos que no te dicen *por qué* te equivocaste. 
La industria intentó solucionar esto conectando modelos como ChatGPT, pero se encontraron con un muro: **La alucinación técnica**. La IA genérica inventa logs, cita leyes que no existen y peca de 'complacencia pedagógica' (te dice que todo está bien para evitar contradecirte). Como Ingeniera de IA, mi reto no fue hacer un chatbot, fue **domesticar la estocástica** de los LLMs para crear un sistema determinista, auditable y seguro."

---

### [Slide 3] La Solución (Ingeniería de IA)
**Tú dices:**
"Mi solución fue abandonar los prompts monolíticos frágiles. Diseñé una arquitectura donde la IA no es un ente único, sino un ecosistema. El sistema evalúa las decisiones del jugador cruzándolas contra documentación real como MITRE y NIST, interactúa con herramientas de simulación e inyecta un feedback que se adapta al *seniority* del usuario."

---

### [Slide 4] Arquitectura del Sistema (Manager of Drafts)
**Tú dices:**
"Para lograr esto, implementé un patrón arquitectónico llamado *Manager of Drafts*. No hay un solo LLM pensando todo. Hay un comité de **5 agentes asimétricos**:
Tengo un *Guard Agent* que filtra inyecciones de prompt. Un *Analista* que investiga. Un agente de *Gobernanza* que revisa el cumplimiento de leyes como GDPR. Un *Explicador* pedagógico. 
Y lo más importante: un **Validador Asimétrico**. Este último actúa como un juez severo que audita el trabajo de los demás agentes antes de mostrarlo al usuario, garantizando calidad total."

---

### [Slide 5] RAG y MCP (El Diferenciador Técnico)
**Tú dices:**
"El mayor orgullo técnico de este proyecto es cómo eliminé las alucinaciones forenses. Separé el conocimiento en dos mundos:
Para la teoría normativa, construí un **Cognitive RAG** con ChromaDB. 
Pero para la evidencia del juego, implementé el estándar **Model Context Protocol (MCP)**. Mi agente Analista no 'adivina' qué pasó en el juego; utiliza herramientas reales por consola (STDIO) para leer los logs del SIEM o aislar un host en el EDR. Es IA interactuando con sistemas deterministas. Es evidencia pura."

---

### [Slide 6] Resiliencia Blindada (Cascada de 3 Niveles)
**Tú dices:**
"En producción, si OpenAI o Google se caen, tu producto muere. Para evitarlo, diseñé una **Cascada de Resiliencia de 3 niveles**. 
El sistema usa Gemini por defecto para máxima velocidad. Si falla, pivota automáticamente a Groq. Y para la validación de alta precisión, delega el trabajo a la infraestructura de **NVIDIA NIM** usando un modelo pesado de 70 billones de parámetros. Si llegara a ocurrir un apagón mundial de APIs, el sistema tiene un modo *Fail-Safe* que devuelve respuestas pre-calculadas. El jugador nunca ve un error rojo en pantalla."

---

### [Slide 7] Desempeño y Métricas Financieras
**Tú dices:**
"Todo esto suena costoso, pero la ingeniería de IA también trata sobre rentabilidad.
Logré un **99.5% de fidelidad anti-alucinaciones** usando verificación cruzada con Hashes SHA-256. 
Y gracias a un *Gateway* que obliga a los agentes a razonar internamente en Inglés y a un sistema de Caché Semántico, redujimos el consumo de tokens en un 30%. ¿El costo real de operar este ecosistema de 5 agentes? **Apenas 0.003 dólares por turno**. Es masivamente escalable."

---

### [Slide 8] Demo en Vivo (Workstation)
**Tú dices:**
"Para demostrarles que esto no es solo teoría, veamos la consola en acción."
*(Muestras la interfaz en Vercel y haces clic en el botón de realizar una acción).*
"Al presionar este botón, fíjense que no hay un simple mensaje de 'Cargando'. Lo que ven en pantalla es la trazabilidad de nuestro **Manager of Drafts** operando en tiempo real. 

Internamente, el *Guard Agent* acaba de validar que mi orden es segura. Ahora mismo, el *Analista* está usando el protocolo **MCP** para conectarse al simulador y extraer la evidencia táctica, mientras consulta en nuestro **RAG** la normativa del NIST. 

Y justo antes de que el reporte final aparezca aquí frente a nosotros, el *Validador Asimétrico* alojado en **NVIDIA NIM** acaba de certificar que el feedback no contiene alucinaciones. El resultado que estamos viendo no es texto predictivo; es un dictamen forense real, adaptado perfectamente al nivel de nuestro analista."

---

### [Slide 9] Conclusiones
**Tú dices:**
"En conclusión, SOC Tutor demuestra que la inteligencia artificial generativa, cuando se la somete a patrones estrictos de Ingeniería de IA, MCP y validación asimétrica, deja de ser un generador de texto impredecible para convertirse en un **motor cognitivo empresarial**.
El sistema está desplegado, asegurado contra ataques de prompt, es económicamente viable y está listo para integrarse a cualquier simulador del mercado.

Muchas gracias. Quedo a disposición para cualquier pregunta sobre la arquitectura o el código."
