
## Observability Agent (Monitoring & Intelligence)

**Problem Statement:-** Modern systems generate massive volumes of logs and metrics, making it difficult to detect and diagnose issues in a timely manner. Traditional monitoring tools rely heavily on rule-based alerts, leading to high false positives and delayed root cause identification. There is a need for an intelligent observability system that can proactively detect anomalies, explain issues, and recommend actions.

## Functional Product Metrics

**1. Customer**

- **Who is the user?.** DevOps engineers, SRE teams, and support engineers responsible for maintaining system reliability and uptime across enterprise platforms.

- **What problem is solved?.** Users struggle with overwhelming volumes of logs and metrics, leading to delayed issue detection and slow root cause identification. Existing monitoring tools generate excessive alerts without actionable insights, forcing teams to spend significant time on manual investigation.

**2. Scenario Thinking**

- End-to-end workflow: - The system continuously ingests logs and metrics from enterprise applications. When abnormal patterns such as latency spikes or error rate increases are detected, the agent identifies the anomaly, analyzes patterns, and generates an alert with contextual insights and probable causes.

- Not just components:- Instead of relying on static rule-based alerts, the agent provides an intelligent monitoring flow that detects, analyzes, and prioritizes issues, reducing the need for manual log inspection and reactive troubleshooting.

**3. Business Impact**

- Why does this matter?. Delayed detection of system issues leads to downtime, degraded user experience, and potential revenue loss. Inefficient alerting systems also increase operational costs and engineer workload.

- What metric improves?
    
    - Reduction in Mean Time to Detect (MTTD)
    - Reduction in Mean Time to Resolve (MTTR)
    - Decrease in false positive alerts
    - Improvement in system uptime and reliability

**4. Platform Thinking**

- How components interact: The observability agent acts as the entry point of the platform by continuously monitoring system data and triggering events. Detected anomalies are passed to downstream agents such as the research agent for root cause analysis and the finance agent for business impact evaluation.

- Extensibility:The agent can be extended to support additional data sources such as real-time streaming pipelines, cloud-native monitoring tools, and application performance metrics. It can also integrate with automated remediation systems for future autonomous operations. The agent can be extended to support advanced financial use cases such as pricing optimization, demand forecasting, investment planning, and scenario-based simulations. It can integrate with enterprise financial systems (ERP, CRM) and evolve into a comprehensive financial intelligence layer within the platform.

## Value Metrics

**Value Tagline:** Predict, explain, and resolve — the future of observability for Industry 5.0

**Value Proposition:** An AI-native, multi-modal log viewer that empowers human-AI collaboration to predict, explain, and resolve issues in real time. It reduces downtime, enhances trust and compliance, and future-proofs observability for Industry 5.0.

**Market Value**: It is estimated that log analytics / management total market market in 2025 is between USD 3 to 4 billion, with a CAGR of 18% growth. 

**Existing Tools**
                A. Static Search & Filters: Legacy tools rely on regex, keyword search, or manual dashboards — requiring expert operators.
                B. Reactive, Not Proactive: They show what happened but don’t infer why or what’s next.
                C. Limited Contextualization: Logs, traces, and metrics are siloed, requiring cross-tool investigation.
                D. No Adaptive Learning: Alerts are threshold-based, leading to noise or missed anomalies.
                E. Scalability Issues: Increasing log volume (IoT, edge, robotics) makes it impractical to manually sift through.
                F. Not Human-Centric: Industry 5.0 emphasizes human-AI collaboration; legacy tools aren’t designed for augmented decision-making.

**Vision**
                
A multi-modal, AI-native observability platform that:

                A. Understands logs, metrics, traces, events, images (screenshots), audio (voice commands), and video (CCTV/robot feeds).
                B. Proactively detects anomalies, root causes, and predicts failures with LLMs + specialized anomaly detection.
                C. Presents findings in natural language & interactive visualizations, accessible to both engineers and non-technical operators.
                D. Optionally integrates Web3.0 concepts (blockchain-backed audit logs, decentralized knowledge sharing, privacy-preserving federated learning).
                E. Embeds co-pilot mode, where AI works alongside human experts to explain, recommend, and even auto-remediate.

## Technical

**vLLM:-**

vLLM is a high-throughput inference and serving engine for LLMs, leveraging PagedAttention for efficient KV cache management via virtual memory-style paging to eliminate fragmentation and enable dynamic batching.

Core Architecture: Multi-process design with LLMEngine orchestrating tokenization, priority-based scheduling (FCFS with look-ahead), and distributed model execution across GPU workers using tensor parallelism.

PagedAttention: Divides KV cache into fixed-size non-contiguous blocks (like OS pages), tracked via block tables; attention computes over scattered blocks using CUDA kernels, achieving near-zero waste and 2-4x throughput gains over systems like FasterTransformer.

Optimizations: Continuous batching integrates new requests mid-decoding; supports prefix caching, FlashAttention-3 integration, torch.compile, and multimodal models; scales via tensor/sequence parallelism on NVIDIA GPUs.

**Key Components:**

    - Scheduler: Prioritizes requests by arrival time and remaining tokens.
    - KV Cache Manager: Handles block allocation/deallocation.
    - Model Runner: Executes forward passes with optimized kernels (e.g., for AWQ/GPTQ quantization)


**Architecture**

<img width="1336" height="882" alt="image" src="https://github.com/user-attachments/assets/38f6e74a-932e-4647-82bd-f9bbc571f854" />

    -  Frontend: Next.js (custom observability console)
    -  Backend: FastAPI
    -  Agent Layer: LangGraph
    -  Workflow Engine: Temporal
    -  Storage: ClickHouse
    -  Prediction Engine: River + StatsForecast
    -  Model Serving: vLLM (Llama 3)
    -  Ingestion: OpenTelemetry + Fluent Bit
    -  Actions: MCP-based tool integrations


## Optimization Techniques

1) Sliding window and streaming logs

- Longest Substring Without Repeating Characters
- Shows sliding window basics for unique event/session tracking.
- Minimum Window Substring
- Find smallest log segment containing all required signals.
- Sliding Window Maximum
- Excellent for rolling peak error rate / latency windows.
- Find All Anagrams in a String
- Longest Repeating Character Replacement

[Rolling metrics]

2) Heap / Top-K for frequent errors and noisy alerts

- Top K Frequent Elements
- Top K Frequent Wordsprob
- K Closest Points to Origin
- Find Median from Data Stream
- Merge K Sorted Lists

[Top 10 error messages, top noisy services, top items causing failures, rolling median latency]

3) Interval problems for time ranges 

- Merge Intervals
- Insert Interval
- Non-overlapping Intervals
- Meeting Rooms II
- My Calendar I

4. Trie / string indexing for log search

- Implement Trie (Prefix Tree)
- Design Add and Search Words Data Structure
- Word Search II
- Replace Words

5. Stack problems for parsing logs and queries

- Valid Parentheses
- Min Stack
- Daily Temperatures
- Largest Rectangle in Histogram
- Basic Calculator
- Decode String

6. Graph problems for service dependency maps

- Number of Islands
- Clone Graph
- Course Schedule
- Course Schedule II
- Network Delay Time
- Redundant Connection
- Accounts Merge
- Evaluate Division

[Service dependency graphs and root cause paths]

7. Binary search for fast query response

- Binary Search
- Search in Rotated Sorted Array
- Find First and Last Position of Element in Sorted Array
- Time Based Key-Value Store
- Koko Eating Bananas

[Time Based Key Value Store]

8. Design problems

- LRU Cache
- LFU Cache
- Insert Delete GetRandom O(1)
- Design Hit Counter
- Logger Rate Limiter
- Time Based Key-Value Store
- Encode and Decode Strings
- Serialize and Deserialize Binary Tree

[Retrival/Storage thinking]

Overall, an observability log viewer with efficient log search, rolling-window analytics, top-K error aggregation, rate limiting, cached queries and service dependency analysis. Core techniques were inspired by classic problems such as Trie, Sliding Window Maximum, LRU Cache, Logger Rate Limiter, Time-Based Key-Value Store and graph traversal.

This project leverages patterns inspired by well known LeetCode problems to build efficient log processing features.

**Quick Start**

docker compose up --build

Then:

    UI → http://localhost:3000
    
    API → http://localhost:8005/docs
    
    Temporal → http://localhost:8233


**App User Interface:-**

<img width="1902" height="945" alt="image" src="https://github.com/user-attachments/assets/8dee2d0d-c344-42f9-954d-915622a91299" />


**Azure Tech Stack (For Cloud Hosting):-**


      1. Resource Group
      2. Azure Container Registry
      3. Build and push Docker image
      4. Container Apps Environment
      5. Scheduled Container Apps Job
      6. Add environment variables securely
      7. Test it
      8. Run on schedule
      9. View logs


**Prompts:-**

az account show

az login --use-device-code

**Confirm the registry is reachable**

az acr show --name <ACR_NAME> --output table

**Log in to the registry**

az acr login --name <ACR_NAME>

**Build and test locally**

docker build -t <IMAGE_NAME>:latest .

docker run --rm --env-file .env -v "${PWD}/<LOCAL_FILE>:/app/<CONTAINER_FILE>" <IMAGE_NAME>:latest python -m <MODULE_PATH> --stocks-file <CONTAINER_FILE>

**Tag and push to ACR**

az acr login --name <ACR_NAME>

docker tag <IMAGE_NAME>:latest <ACR_NAME>.azurecr.io/<IMAGE_NAME>:latest

docker push <ACR_NAME>.azurecr.io/<IMAGE_NAME>:latest

<img width="1541" height="393" alt="image" src="https://github.com/user-attachments/assets/30319add-a3a8-4a36-b2c2-16a11559fb77" />

<img width="1012" height="677" alt="image" src="https://github.com/user-attachments/assets/185cfe4f-e988-4e37-9384-7ee424386bd4" />


**Core Capabilities**
                
                A. Semantic & natural language log search.
                B. Multi-modal input (logs, metrics, traces).
                C. AI clustering, anomaly detection & root cause analysis.
                D. Predictive failure insights
                E. Explainable AI with plain-language summaries.
                F. Auto-remediation guidance + compliance reporting.
                G. Blockchain-backed immutable logs (optional).



**Use Cases:** Predict machine downtime, detect cyber threats, summarize IoT floods, Field operators query with alerts/voice, SME's will get AI reports.

**Core Benefits:** Reduce downtime & costs, Enable human-centric collaboration, Ensure trust, compliance & scalability, Future-proof for Industry 5.0 data growth. And, a goal towards Responsible AI.





