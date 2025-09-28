# Noah's AI Assistant

Noah's AI Assistant is a retrieval-augmented generative AI application designed to adapt its conversational style and retrieval strategy based on distinct user roles. The system provides tailored responses for hiring managers, software developers, casual visitors, and personal interactions, ensuring a seamless user experience.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Role-Based Interaction**: Users can select their role to receive customized responses.
- **Retrieval-Augmented Generation**: Combines document retrieval with generative AI for accurate and relevant answers.
- **Dual-Audience Formatting**: Provides both technical details and plain-English summaries.
- **Analytics Panel**: Displays metrics and insights about user interactions.
- **Compliance and Safety**: Enforces guardrails to ensure safe and compliant responses.

## Tech Stack

- **Frontend/UI**: Streamlit for chat UI, role prompt, and analytics panel.
- **Core Framework**: LangChain for document loading, embeddings, retrieval, and RAG pipeline.
- **Vector Storage**: FAISS for career knowledge base, code index, and YouTube transcripts.
- **Models**: OpenAI GPT for answers and OpenAI Embeddings for vectorization.
- **Memory**: Short-term buffer and rolling summary for context management.
- **Orchestration**: LangGraph for routing retrieval and enforcing invariants.
- **Observability**: LangSmith for traces and evaluations.
- **Analytics Database**: SQLite/Postgres for metrics logging.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/noahs-ai-assistant.git
   cd noahs-ai-assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage

To run the application, execute the following command:
```
streamlit run src/ui/streamlit_app.py
```

Follow the prompts in the Streamlit interface to interact with Noah's AI Assistant.

## File Structure

```
noahs-ai-assistant
├── src
│   ├── main.py
│   ├── config
│   ├── core
│   ├── retrieval
│   ├── agents
│   ├── ui
│   ├── analytics
│   └── utils
├── data
├── vector_stores
├── tests
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
<<<<<<< HEAD
# Noah's AI Assistant

Noah's AI Assistant is a retrieval-augmented generative AI application designed to adapt its conversational style and retrieval strategy based on distinct user roles. The system provides tailored responses for hiring managers, software developers, casual visitors, and personal interactions, ensuring a seamless user experience.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Role-Based Interaction**: Users can select their role to receive customized responses.
- **Retrieval-Augmented Generation**: Combines document retrieval with generative AI for accurate and relevant answers.
- **Dual-Audience Formatting**: Provides both technical details and plain-English summaries.
- **Analytics Panel**: Displays metrics and insights about user interactions.
- **Compliance and Safety**: Enforces guardrails to ensure safe and compliant responses.

## Tech Stack

- **Frontend/UI**: Streamlit for chat UI, role prompt, and analytics panel.
- **Core Framework**: LangChain for document loading, embeddings, retrieval, and RAG pipeline.
- **Vector Storage**: FAISS for career knowledge base, code index, and YouTube transcripts.
- **Models**: OpenAI GPT for answers and OpenAI Embeddings for vectorization.
- **Memory**: Short-term buffer and rolling summary for context management.
- **Orchestration**: LangGraph for routing retrieval and enforcing invariants.
- **Observability**: LangSmith for traces and evaluations.
- **Analytics Database**: SQLite/Postgres for metrics logging.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/noahs-ai-assistant.git
   cd noahs-ai-assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage

To run the application, execute the following command:
```
streamlit run src/ui/streamlit_app.py
```

Follow the prompts in the Streamlit interface to interact with Noah's AI Assistant.

## File Structure

```
noahs-ai-assistant
├── src
│   ├── main.py
│   ├── config
│   ├── core
│   ├── retrieval
│   ├── agents
│   ├── ui
│   ├── analytics
│   └── utils
├── data
├── vector_stores
├── tests
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
=======
# NoahsAIAssistant-
AI assistant 
>>>>>>> d1d7b1e47ac5cf6abad6183fce0ba8c6f24431b7
