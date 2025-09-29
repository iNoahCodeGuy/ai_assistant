#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_key_and_connection():
    """Test OpenAI API key loading and connection."""
    print("🔑 Testing OpenAI API Key and Connection...")
    
    try:
        # Test 1: API key loading
        from src.config.settings import Settings
        settings = Settings()
        settings.validate_api_key()
        print("✅ API key loaded from .env file")
        
        # Test 2: OpenAI client initialization
        import openai
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        print("✅ OpenAI client initialized")
        
        # Test 3: Simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API connection successful!' in exactly those words."}
            ],
            max_tokens=10
        )
        
        api_response = response.choices[0].message.content.strip()
        print(f"✅ API call successful: {api_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_memory_functionality():
    """Test comprehensive memory functionality."""
    print("\n💾 Testing Memory System...")
    
    try:
        from src.core.memory import Memory
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{}')
            temp_file = f.name
        
        try:
            # Test 1: Memory initialization
            memory = Memory(persistence_file=temp_file)
            print("✅ Memory initialization successful")
            
            # Test 2: Session storage and retrieval
            session_id = "test-session-123"
            role = "Software Developer"
            chat_history = [
                {"role": "user", "content": "What's Noah's background?"},
                {"role": "assistant", "content": "Noah started in sales and moved to tech..."},
                {"role": "user", "content": "How strong is his Python?"},
                {"role": "assistant", "content": "Noah's Python skills are intermediate level..."}
            ]
            
            memory.store_session_context(session_id, role, chat_history)
            retrieved = memory.retrieve_session_context(session_id)
            
            assert retrieved is not None
            assert retrieved["role"] == role
            assert len(retrieved["chat_history"]) == 4
            assert "timestamp" in retrieved
            print("✅ Session storage and retrieval working")
            
            # Test 3: Chat history truncation
            long_chat = []
            for i in range(15):
                long_chat.append({"role": "user", "content": f"Message {i}"})
                long_chat.append({"role": "assistant", "content": f"Response {i}"})
            
            memory.store_session_context("truncation-test", role, long_chat)
            truncated = memory.retrieve_session_context("truncation-test")
            
            assert len(truncated["chat_history"]) == 10
            print("✅ Chat history truncation working")
            
            # Test 4: Persistence across instances
            memory2 = Memory(persistence_file=temp_file)
            retrieved2 = memory2.retrieve_session_context(session_id)
            
            assert retrieved2 is not None
            assert retrieved2["role"] == role
            print("✅ Cross-instance persistence working")
            
            # Test 5: Working memory
            memory.add_to_working_memory("test_preferences", {"theme": "dark", "model": "gpt-4"})
            prefs = memory.get_from_working_memory("test_preferences")
            assert prefs["theme"] == "dark"
            print("✅ Working memory functionality working")
            
            return True
            
        finally:
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between OpenAI and Memory systems."""
    print("\n🔗 Testing OpenAI + Memory Integration...")
    
    try:
        from src.config.settings import Settings
        from src.core.memory import Memory
        from openai import OpenAI
        import tempfile
        
        # Initialize components
        settings = Settings()
        client = OpenAI(api_key=settings.openai_api_key)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{}')
            temp_file = f.name
        
        try:
            memory = Memory(persistence_file=temp_file)
            
            # Simulate a conversation with memory persistence
            session_id = "integration-test"
            role = "Technical Hiring Manager"
            
            # Turn 1: User asks about Noah
            user_msg_1 = "What's Noah's technical background?"
            
            # Simulate getting AI response
            response_1 = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Noah's AI assistant. Respond briefly about his technical background in Python and AI."},
                    {"role": "user", "content": user_msg_1}
                ],
                max_tokens=50
            )
            
            ai_response_1 = response_1.choices[0].message.content.strip()
            
            # Store in memory
            chat_history = [
                {"role": "user", "content": user_msg_1},
                {"role": "assistant", "content": ai_response_1}
            ]
            memory.store_session_context(session_id, role, chat_history)
            
            # Turn 2: Follow-up question with context
            user_msg_2 = "Can you tell me more about his Python projects?"
            
            # Retrieve context from memory
            context = memory.retrieve_session_context(session_id)
            previous_conversation = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in context["chat_history"]
            ])
            
            # AI response with context
            response_2 = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Previous conversation:\n{previous_conversation}\n\nRespond about Noah's Python projects briefly."},
                    {"role": "user", "content": user_msg_2}
                ],
                max_tokens=50
            )
            
            ai_response_2 = response_2.choices[0].message.content.strip()
            
            # Update memory
            chat_history.extend([
                {"role": "user", "content": user_msg_2},
                {"role": "assistant", "content": ai_response_2}
            ])
            memory.store_session_context(session_id, role, chat_history)
            
            # Verify integration worked
            final_context = memory.retrieve_session_context(session_id)
            assert len(final_context["chat_history"]) == 4
            assert final_context["role"] == role
            
            print("✅ OpenAI + Memory integration successful")
            print(f"   📝 Conversation stored: {len(final_context['chat_history'])} messages")
            print(f"   🎭 Role persisted: {final_context['role']}")
            
            return True
            
        finally:
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running comprehensive OpenAI API Key and Memory Tests...")
    print("=" * 70)
    
    api_ok = test_api_key_and_connection()
    memory_ok = test_memory_functionality()  
    integration_ok = test_integration()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 70)
    
    if api_ok and memory_ok and integration_ok:
        print("🎉 SUCCESS: ALL TESTS PASSED!")
        print("\n✅ VERIFIED SYSTEMS:")
        print("✅ OpenAI API key loading: WORKING")
        print("✅ OpenAI API connection: WORKING") 
        print("✅ Memory persistence: WORKING")
        print("✅ Chat history management: WORKING")
        print("✅ Role-based context: WORKING")
        print("✅ OpenAI + Memory integration: WORKING")
        print("\n🚀 Your AI Assistant is fully operational!")
        print("\n💡 Ready to run: streamlit run src/main.py")
    else:
        print("❌ SOME TESTS FAILED!")
        if not api_ok:
            print("❌ OpenAI API issues")
        if not memory_ok:
            print("❌ Memory system issues")
        if not integration_ok:
            print("❌ Integration issues")
