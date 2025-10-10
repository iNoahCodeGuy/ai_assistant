# 🔄 Noah's AI Assistant - Request Flow Architecture

## Overview
This document explains how a user request flows through Noah's AI Assistant from UI to final response.

## 🚀 Complete Request Flow

```
┌─────────────────┐
│   Streamlit UI  │ ← User selects role & enters query
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│     Memory      │ ← Retrieves chat history & context
│    (session)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   RoleRouter    │ ← Classifies query & routes by role
│  (query type)   │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────────┐
│ Career  │   │    Code     │ ← Retrieval strategies
│   KB    │   │   Index     │   based on role
└─────────┘   └─────────────┘
    │           │
    └─────┬─────┘
          │
          ▼
┌─────────────────┐
│   RagEngine     │ ← Combines knowledge sources
│  (retrieval)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ ResponseGen     │ ← Generates role-aware response
│    (LLM)        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Formatter     │ ← Formats for target audience
│ (dual-audience) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│     Memory      │ ← Stores conversation
│   (persistence) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Analytics      │ ← Logs metrics
│   (metrics)     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   User Gets     │ ← Final formatted response
│   Response      │
└─────────────────┘
```

## 🎭 Role-Based Flow Variations

### **Technical Manager Path**
```
Query → RoleRouter → (Career KB + Code Index) → RagEngine → ResponseGen → 
Formatter (Engineer Detail + Plain-English) → User
```

### **Software Developer Path**
```
Query → RoleRouter → Code Index (primary) → RagEngine → ResponseGen → 
Formatter (Maximum Technical Detail) → User
```

### **Non-technical Manager Path**
```
Query → RoleRouter → Career KB → RagEngine → ResponseGen → 
Formatter (Business-Focused) → User
```

### **Casual Visitor Path**
```
Query → RoleRouter → (MMA Check) → Direct Link OR Career KB → 
Simple Response → User
```

## 🔧 Key Components Deep Dive

### **1. RoleRouter** (`src/agents/role_router.py`)
- **Purpose**: Query classification and role-based routing
- **Input**: `(role, query, memory, rag_engine, chat_history)`
- **Output**: `{"response": str, "type": str, "context": List}`
- **Logic**: 
  - Classifies query as "technical", "career", "mma", "fun"
  - Routes to appropriate knowledge source
  - Calls specialized handlers

### **2. RagEngine** (`src/core/rag_engine.py`)
- **Purpose**: Retrieval orchestration and knowledge synthesis
- **Key Methods**:
  - `retrieve_with_code()` - Enhanced retrieval for technical roles
  - `retrieve_career_info()` - Career knowledge retrieval
  - `generate_technical_response()` - Code-integrated responses
- **Architecture**: Factory pattern with modular components

### **3. ResponseGenerator** (`src/core/response_generator.py`)
- **Purpose**: LLM interaction and prompt management
- **Types**:
  - Basic responses (simple queries)
  - Technical responses (code integration)
  - Contextual responses (conversation aware)

### **4. ResponseFormatter** (`src/agents/response_formatter.py`)
- **Purpose**: Audience-appropriate formatting
- **Formats**:
  - **Engineer Detail**: Technical depth with citations
  - **Plain-English Summary**: Business-friendly translation
  - **Code Examples**: Syntax highlighted with GitHub links

## 📊 Data Flow Details

### **Career Knowledge Base Flow**
```
CSV File → DocumentProcessor → Text Chunks → FAISS Embeddings → 
Vector Search → Relevant Docs → Context Assembly
```

### **Code Index Flow**
```
Source Files → CodeIndex → Real-time Monitoring → File:Line Citations → 
GitHub URLs → Snippet Assembly → Technical Context
```

### **Memory Flow**
```
Session Start → Role Selection → Chat History → Context Building → 
Token Budgeting → Persistence → Session Recovery
```

## 🔄 Real-time Updates

### **Code Index Versioning**
```
File Change Detection → Hash Comparison → Index Rebuild → 
Version Update → Fresh Code Retrieval
```

### **Memory Management**
```
New Message → History Append → Truncation (10 messages) → 
Persistence → Context Retrieval
```

## 🧪 Testing Flow

```
Request → Mock Components → Test Assertions → 
Performance Checks → Integration Validation
```

## 🎯 Response Quality Assurance

1. **Citation Accuracy**: File:line verification
2. **Role Appropriateness**: Content filtering by audience
3. **Performance Monitoring**: Response time tracking
4. **Error Handling**: Graceful degradation paths

## 📈 Analytics Flow

```
User Interaction → Metrics Collection → Performance Tracking → 
Feedback Analysis → Test Generation → Continuous Improvement
```

This architecture enables:
- **Role-aware intelligence**
- **Real-time code accuracy**
- **Conversation continuity**
- **Production monitoring**
- **Automatic testing**

Each component is independently testable and follows single responsibility principles.
