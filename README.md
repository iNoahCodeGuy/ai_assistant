# Noah's AI Assistant 🤖

A role-adaptive AI chatbot built with Streamlit, LangChain, FAISS, and OpenAI that tailors responses based on user roles. Whether you're a hiring manager, developer, or just looking for casual conversation, Noah's Assistant adapts to provide the most relevant and useful responses.

## Features ✨

### Role-Based Adaptation
- **Non-Technical Hiring Managers**: Get concise résumé summaries and candidate overviews
- **Technical Managers**: Access detailed technical stack information and architecture insights  
- **Developers**: Receive code examples with file:line citations and GitHub links
- **Casual Users**: Enjoy fun facts and entertaining content including MMA fight links
- **Crush Users**: Share thoughts anonymously in a supportive environment

### Core Capabilities
- 🎯 **Smart Citations**: File:line references with GitHub integration
- 🔍 **FAISS Vector Search**: Intelligent document retrieval and context awareness
- 🤖 **OpenAI Integration**: Powered by GPT models for natural language understanding
- 📊 **Analytics & Observability**: Token usage tracking and performance monitoring
- 🔒 **Privacy & Compliance**: Role-appropriate responses with privacy protection
- 🚀 **Streamlit UI**: Interactive and responsive web interface

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/iNoahCodeGuy/NoahsAIAssistant-.git
   cd NoahsAIAssistant-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the app**
   Open your browser to `http://localhost:8501`

## Usage Guide 📖

### Getting Started
1. Select your role from the sidebar dropdown
2. Start chatting - the assistant will adapt responses to your role
3. Enjoy role-specific features and citations

### Role-Specific Features

#### For Hiring Managers 👔
- Get bullet-pointed résumé summaries
- Focus on skills, experience, and cultural fit
- Jargon-free explanations of technical concepts

#### For Technical Managers 🏗️
- Detailed technology stack explanations
- Architecture insights and trade-offs
- Performance and scalability considerations
- Industry best practices with citations

#### for Developers 💻
- Code examples with syntax highlighting
- File:line citations for easy navigation
- GitHub repository links
- Implementation details and alternatives
- Technical deep-dives

#### For Casual Users 😊
- Fun facts and interesting trivia
- Light-hearted and engaging responses
- Entertainment links including MMA fights
- Learning made enjoyable

#### For Crush Users 💕
- Anonymous and supportive environment
- Privacy-protected conversations
- Encouraging and understanding responses
- Safe space for sharing thoughts

## Architecture 🏗️

```
├── app.py                 # Main Streamlit application
├── src/
│   ├── __init__.py       # Package initialization
│   ├── role_handler.py   # Role-based response logic
│   ├── ai_engine.py      # OpenAI and LangChain integration
│   ├── data_loader.py    # FAISS vector search and document management
│   └── citation_manager.py # Citation generation and formatting
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

### Key Components

- **RoleHandler**: Manages role-specific prompts and response enhancement
- **AIEngine**: Handles OpenAI API calls with usage tracking
- **DataLoader**: Manages FAISS vector search and document indexing
- **CitationManager**: Generates and formats citations with GitHub links

## Configuration ⚙️

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Customization
- **Add new roles**: Extend `role_configs` in `RoleHandler`
- **Update sample data**: Modify `_initialize_sample_data()` in `DataLoader`
- **Customize citations**: Adjust citation styles in `CitationManager`

## Development 🛠️

### Running Tests
```bash
# Install development dependencies
pip install pytest streamlit-testing

# Run tests (if implemented)
pytest tests/
```

### Code Structure
- Follow PEP 8 style guidelines
- Use type hints throughout
- Maintain separation of concerns between modules
- Add docstrings to all classes and methods

## Privacy & Compliance 🔒

- **Anonymous Mode**: Crush users can share thoughts without identification
- **Data Protection**: No sensitive information is stored permanently
- **Role Awareness**: Responses are filtered based on user role permissions
- **Usage Tracking**: Token usage monitoring for cost management

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- **Issues**: [GitHub Issues](https://github.com/iNoahCodeGuy/NoahsAIAssistant-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iNoahCodeGuy/NoahsAIAssistant-/discussions)

## Acknowledgments 🙏

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
- Language models via [LangChain](https://python.langchain.com/)

---

*Made with ❤️ by Noah - Your Adaptive AI Assistant*
