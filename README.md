# Noah's AI Assistant

Noah's AI Assistant (repo: NoahsAIAssistant-) is a retrieval-augmented generative AI application that adapts its conversational style and retrieval strategy based on distinct user roles. It tailors responses for hiring managers, software developers, casual visitors, and personal interactions while emphasizing transparency, robustness, and compliance.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Role-Specific Behaviors](#role-specific-behaviors)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Role-Based Interaction**: Session-level role selection shapes retrieval + formatting.
- **Retrieval-Augmented Generation (RAG)**: FAISS vector stores (career KB, code index, optional transcripts).
- **Dual-Audience Formatting**: Engineer Detail + Plain-English Summary (for technical audiences).
- **Code & Career Grounding**: File:line citations where available.
- **MMA Query Routing**: Direct fight link for MMA-related queries (bypasses general retrieval).
- **Confession Mode**: Lightweight, guarded input path with no unintended PII retention.
- **Analytics Panel**: Interaction counts, role distribution, basic query metrics.
- **Extensible Orchestration**: Designed to plug into LangGraph for future routing graphs.
- **Observability Ready**: LangSmith integration hooks (traces/evals) planned.

## Tech Stack
- **Frontend/UI**: Streamlit (chat UI, role selector, analytics panel)
- **Core Framework**: LangChain (loaders, embeddings, retrieval pipeline) 
- **Vector Storage**: Google Vertex AI Vector Search (career_kb, code_index)
- **Models**: OpenAI GPT (generation), OpenAI Embeddings (vectorization)
- **Memory**: Google Cloud Memorystore (Redis) for session management
- **Analytics DB**: Google Cloud SQL (PostgreSQL) with real-time analytics
- **Event Streaming**: Google Cloud Pub/Sub for analytics events
- **Security**: Google Secret Manager for API keys and credentials
- **Deployment**: Google Cloud Run with auto-scaling
- **Observability**: Cloud-native monitoring and LangSmith integration
- **Testing**: Pytest with cloud environment support

## Role-Specific Behaviors

### 1. Hiring Manager (nontechnical)
- Goal: High-level résumé narrative
- Sources: Career KB CSV, résumé text
- Format: Career Overview → Notable Outcomes → Source Citations (lightweight)
- UI: Contact CTA (email / LinkedIn)

### 2. Hiring Manager (technical)
- Goal: Blend career signal + engineering depth
- Sources: Career KB + Code Index
- Format:
  - Section 1: Engineer Detail (with file:line citations)
  - Section 2: Plain-English Summary
- UI: Expandable code reference (future enhancement)

### 3. Software Developer
- Goal: Deep technical explanation, architecture, design tradeoffs
- Sources: Code Index + Career KB fallback
- Format: Engineer Detail → Summary (same dual format)

### 4. Just Looking Around
- Goal: Fun facts + MMA info
- MMA queries: Direct fight link
- Other queries: Light career / personal facts

### 5. Looking to Confess Crush
- Goal: Safe, minimal interaction channel
- Storage: Only explicit submission, no hidden PII retention
- Response: Acknowledgment only (no model overreach)

## Installation
```bash
git clone https://github.com/iNoahCodeGuy/NoahsAIAssistant-.git
cd NoahsAIAssistant-
pip install -r requirements.txt
```

Copy environment variables:
```bash
cp .env.example .env
# edit .env and add OPENAI_API_KEY, optional LANGSMITH_API_KEY
```

## Usage
Development run (current entrypoint uses Streamlit main):
```bash
streamlit run src/main.py
```
(If/when a dedicated `src/ui/streamlit_app.py` is added, update command accordingly.)

## File Structure
```
noahs-ai-assistant
├── src
│   ├── main.py
│   ├── config/
│   ├── core/
│   ├── retrieval/
│   ├── agents/
│   ├── ui/
│   ├── analytics/
│   └── utils/
├── data/
├── vector_stores/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Contributing
1. Create a branch: feature/<name>
2. Keep commits focused
3. Open PR → request review

## License
MIT (see LICENSE if present). Add LICENSE file if not yet created.
