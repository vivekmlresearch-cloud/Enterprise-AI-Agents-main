## Research Agent (Reasoning / RAG)

**Problem Statement:-** Enterprise teams need to extract actionable insights from fragmented data sources such as logs, documents, and knowledge bases. Existing tools require manual search and need more contextual understanding, leading to slow and inconsistent decision-making. There is a need for an system that can unify data, reason across contexts, and deliver precise answers in real time.

# Functional

**1. Customer**

**Who is the user?.** Knowledge workers across the enterprise, including product managers, analysts, support engineers, and business teams who need to quickly gather insights, validate hypotheses, and make informed decisions.

**What problem is solved?.** Users spend significant time searching across multiple tools such as documentation, dashboards, reports, and external sources. Information is fragmented, and existing tools need the ability to understand context, synthesize insights, and provide actionable answers.

**2. Scenario Thinking**

**End-to-end workflow:-** A user asks a question such as “What are the key reasons for declining product performance this quarter?” The agent retrieves relevant information from internal data sources, documents, and historical trends, synthesizes the findings, and generates a structured, context-aware response with explanations and recommendations. A user can also asks a natural language query such as “Why is system performance degrading?” The agent retrieves relevant data from logs, documents, research papers and historical incidents, applies contextual reasoning, and generates a concise explanation with supporting evidence and recommended actions.

**Not just components:-** Instead of acting as a simple search tool, the agent functions as an intelligent research assistant that combines retrieval, reasoning, and summarization to provide end-to-end insights across technical and business domains.

**3. Business Impact**

**- Why does this matter?**
Slow and inconsistent access to insights leads to delayed decisions, increased operational costs, and reduced productivity across teams. Organizations need faster, more reliable ways to interpret complex data.

**- What metric improves?**

     - Reduction in time spent on research and analysis
     - Faster decision-making cycles
     - Improved accuracy and consistency of insights
     - Increased productivity across technical and business teams

**4. Platform Thinking**

- **How components interact:-** The research agent acts as a central reasoning layer that can consume inputs from multiple sources, including outputs from the observability agent and enterprise data systems. It synthesizes this information into structured insights that can be used directly by users or passed to other agents such as the finance agent.

- **Extensibility:-** The agent can be extended to support multiple domains such as market research, customer insights, financial analysis, and operational intelligence. It can integrate with enterprise systems, APIs, and external knowledge bases, evolving into a unified enterprise copilot.


## Technical 

Design notes:-

- Nemotron for reasoning and summarization
- Triton for serving
- NeMo Retriever for ingest / embed / rerank
- Vector DB for indexed papers and user memory
- MCP for tool calling
- arXiv + Semantic Scholar as live paper discovery backends
- Version 1 (Previous):- phi3 model, Version 2 (Current Version):- Nemotron Based

<img width="1062" height="703" alt="image" src="https://github.com/user-attachments/assets/c5a2b584-56e9-4829-83a0-c22278347645" />


Query:

<img width="847" height="128" alt="image" src="https://github.com/user-attachments/assets/912679c7-418d-47cc-8598-ff013b9f246e" />


Response:

![Sample Results](https://github.com/user-attachments/assets/f62718c7-335c-4a60-b6f3-206967cb2414)


RAGAS will Further Evaluate:-

Did retrieval bring the right evidence | how response use that evidence | How response stay on question | How response avoid unsupported claims. 


Model Used:-

 - LLM_MODEL=Llama-3_3-Nemotron-Super-49B-v1_5
 - EMBEDDING_MODEL=nvidia/nv-embedqa-e5-v5 (Fine-tuned E5-Large-Unsupervised retriever)
