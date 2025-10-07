# 🎭 Noah's AI Assistant - Features by Role

## Overview
After selecting a role, the AI Assistant customizes its behavior, retrieval strategy, and response format to match your needs. Here's what each role gets:

---

## 🎯 Available Roles

### 1. **Hiring Manager (nontechnical)** 👔
**Target Audience:** HR professionals, recruiters, business leaders

**Features:**
- ✅ **Career-focused responses** - Information about Noah's work history, achievements, and experience
- ✅ **Business-oriented language** - No heavy technical jargon
- ✅ **Resume/CV information** - Access to career knowledge base
- ✅ **Chat memory** - Remembers previous questions in the conversation
- ✅ **Context-aware answers** - Can answer follow-up questions naturally

**Query Types Handled:**
- Career history and roles
- Achievements and accomplishments
- General background information
- Experience summaries

**Example Questions:**
- "What is Noah's work history?"
- "Tell me about Noah's achievements"
- "What kind of roles has Noah held?"

---

### 2. **Hiring Manager (technical)** 💼🔧
**Target Audience:** Technical recruiters, engineering managers, CTOs

**Features:**
- ✅ **Technical + career responses** - Best of both worlds
- ✅ **Code references** - Links to GitHub repositories and code snippets
- ✅ **Technical architecture details** - System design and implementation info
- ✅ **Career knowledge base** - Work history and achievements
- ✅ **Dual-audience formatting** - Can explain technical concepts clearly
- ✅ **Chat memory** - Full conversation context
- ✅ **Code snippet citations** - Direct links to GitHub with file references

**Query Types Handled:**
- Technical career questions
- Code implementations
- System architecture
- Technology stack details
- General career info

**Example Questions:**
- "What technical projects has Noah worked on?"
- "Show me Noah's code for the RAG engine"
- "How did Noah implement the retrieval system?"
- "What's Noah's tech stack?"

**Special Features:**
When you ask about code/technical implementation, responses include:
```markdown
**Code References:**
- [rag_engine.py:152-220](https://github.com/user/repo/blob/main/rag_engine.py#L152-L220)
```

---

### 3. **Software Developer** 👨‍💻
**Target Audience:** Engineers, developers, technical collaborators

**Features:**
- ✅ **Deep technical focus** - Prioritizes code index and implementation details
- ✅ **Complete code snippets** - Full functions/classes embedded in responses
- ✅ **Architecture explanations** - System design and technical decisions
- ✅ **Chat memory** - Remembers technical discussion context
- ✅ **Detailed code implementation** - Formatted code blocks with syntax highlighting
- ✅ **GitHub links** - Direct navigation to source code
- ✅ **Technical depth** - Assumes technical background

**Query Types Handled:**
- Code implementation details
- Technical architecture
- Function/class specifics
- General background (less focus)

**Example Questions:**
- "How does the RAG retrieval work?"
- "Show me the pgvector implementation"
- "What's the architecture of this system?"
- "How did you implement chat memory?"

**Special Features:**
Responses include embedded code blocks:
```markdown
## Code Implementation

### PgVectorRetriever ([pgvector_retriever.py](https://github.com/...))
```python
def retrieve(self, query: str, top_k: int = 3):
    embedding = self.embed(query)
    # ... implementation details ...
```
```

---

### 4. **Just looking around** 👀
**Target Audience:** Casual visitors, curious explorers, potential connections

**Features:**
- ✅ **Conversational tone** - Friendly and approachable
- ✅ **Lightweight retrieval** - Quick, concise answers
- ✅ **Fun facts support** - Access to interesting tidbits about Noah
- ✅ **MMA content** - Special handling for MMA-related queries (YouTube fight link)
- ✅ **General knowledge base** - Career and background info
- ✅ **Chat memory** - Remembers conversation flow

**Query Types Handled:**
- General questions about Noah
- Fun facts and hobbies
- MMA/sports interests
- Casual background info

**Example Questions:**
- "Tell me about Noah"
- "What are some fun facts about Noah?"
- "Does Noah do MMA?" (returns YouTube link to fight)
- "What's Noah interested in?"

**Special Features:**
- **MMA Queries**: Returns direct YouTube link to Noah's fight
- **Fun Facts Mode**: Generates 3 short fun facts (under 60 words total)

---

### 5. **Looking to confess crush** 💘
**Target Audience:** Secret admirers (for fun)

**Features:**
- ✅ **Privacy-focused** - No LLM calls, no data logging beyond acknowledgment
- ✅ **Form integration** - Directs to confession submission form
- ✅ **Simple acknowledgment** - Friendly confirmation message

**Response:**
```
"Your message is noted. Use the form for new confessions. 💌"
```

**Note:** This is a playful feature and doesn't perform retrieval or generate dynamic responses.

---

## 🔄 Common Features Across All Roles

### Chat Memory
All roles (except confession) support multi-turn conversations:
- Remembers last 4 messages (2 exchanges)
- Contextualizes follow-up questions
- Maintains conversation flow

**Example:**
```
You: "What programming languages does Noah know?"
AI: "Noah is proficient in Python, JavaScript, TypeScript..."

You: "Which of those has he used professionally?"
AI: "Based on his career history, Noah has used Python and TypeScript 
     professionally at [companies mentioned in previous context]..."
```

### Retrieval Strategy
All roles use RAG (Retrieval-Augmented Generation):
- Queries are embedded using OpenAI's `text-embedding-3-small`
- Relevant chunks retrieved from Supabase pgvector database
- Similarity threshold: 0.3 (cosine similarity)
- Top-k results: 3 most relevant chunks

### Response Generation
- Uses OpenAI GPT model for natural language generation
- Contextually aware (uses retrieved knowledge + chat history)
- Role-appropriate formatting
- No generic "I don't have information" responses (fixed!)

---

## 📊 Analytics Tracking

Every interaction is logged to Supabase with:
- Query text
- Role/mode
- Response generated
- Query type (technical, career, general, mma, fun)
- Response time (latency in ms)
- Success/failure status
- Session ID (for conversation tracking)

---

## 🎛️ How Role Selection Works

### Initial Selection
1. When you first open the app, you see role options
2. Select your role from dropdown
3. Click "Confirm Role"
4. Role persists for entire session

### Changing Roles
- Click "Change Role" in sidebar
- Returns to role selection screen
- Chat history is cleared (new session starts)

### Why Role Selection Matters
Different roles need different knowledge sources and response styles:
- **Software Developer**: Prioritize code index, technical depth
- **Hiring Manager (technical)**: Career KB + code snippets, dual-audience format
- **Hiring Manager (nontechnical)**: Career KB only, business-focused
- **Casual Visitor**: Lightweight retrieval, conversational tone

Without knowing the role, the system can't optimize retrieval or formatting.

---

## 🚀 Technical Implementation

### Role Router
The `RoleRouter` class handles query classification and routing:

```python
def route(self, role: str, query: str, memory: Memory, 
          rag_engine: RagEngine, chat_history: List[Dict]) -> Dict:
    # Classifies query type: mma, fun, technical, career, or general
    query_type = self._classify_query(query)
    
    # Routes to appropriate handler based on role
    if role == "Hiring Manager (technical)":
        return self._handle_technical_manager(...)
    # ... other roles
```

### Query Classification
Automatic detection based on keywords:
- **MMA**: "mma", "fight", "ufc", "bout"
- **Fun Facts**: "fun fact", "fun", "fact", "hobby"
- **Technical**: "code", "technical", "stack", "function", "architecture"
- **Career**: "career", "resume", "cv", "experience", "achievement"
- **General**: Everything else

### Code Integration
Technical roles get code snippets through:
```python
results = rag_engine.retrieve_with_code(query, role=role)
# Returns both text chunks AND code snippets with GitHub links
```

---

## 💡 Tips for Best Results

### For Hiring Managers (nontechnical)
- Ask about achievements, impact, and business outcomes
- Request resume summaries or career highlights
- Ask about soft skills and leadership

### For Hiring Managers (technical)
- Combine career and technical questions
- Ask about technical projects with business context
- Request code examples of specific implementations

### For Software Developers
- Be specific about technical topics
- Ask for code snippets and architecture details
- Request implementation explanations

### For Casual Visitors
- Ask open-ended questions
- Try asking for fun facts
- Inquire about hobbies and interests

---

## 🎯 Current Status

✅ **All features fully operational**
- Chat memory working
- Response generation with LLM
- Client-side similarity search
- Role-based routing
- Code snippet integration
- Analytics logging

🚀 **Ready to test in browser**: http://localhost:8501

---

## 📝 Future Enhancements

Potential improvements:
- **Performance**: Optimize retrieval for larger knowledge bases (>100 chunks)
- **PostgREST Fix**: Investigate RPC function issue for server-side similarity
- **More Roles**: Add "Recruiter", "Colleague", etc.
- **Enhanced Memory**: Implement conversation summarization for longer chats
- **Multimodal**: Add support for images, diagrams, or videos

---

**Last Updated**: October 6, 2025
**Status**: ✅ Production Ready
