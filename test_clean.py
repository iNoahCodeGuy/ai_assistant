#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_memory_functionality():
    """Test basic memory functionality."""
    print("Testing Memory functionality...")
    
    try:
        from core.memory import Memory
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{}')
            temp_file = f.name
        
        try:
            # Test initialization
            memory = Memory(persistence_file=temp_file)
            print("SUCCESS: Memory initialization works")
            
            # Test session storage
            session_id = "test-session-123"
            role = "Software Developer"
            chat_history = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
            
            memory.store_session_context(session_id, role, chat_history)
            retrieved = memory.retrieve_session_context(session_id)
            
            assert retrieved is not None
            assert retrieved["role"] == role
            assert len(retrieved["chat_history"]) == 2
            print("SUCCESS: Session storage and retrieval works")
            
            # Test persistence across instances
            memory2 = Memory(persistence_file=temp_file)
            retrieved2 = memory2.retrieve_session_context(session_id)
            
            assert retrieved2 is not None
            assert retrieved2["role"] == role
            print("SUCCESS: Persistence across instances works")
            
            # Test chat history truncation
            long_chat = []
            for i in range(15):
                long_chat.append({"role": "user", "content": "Message " + str(i)})
                long_chat.append({"role": "assistant", "content": "Response " + str(i)})
            
            memory.store_session_context("truncation-test", role, long_chat)
            truncated = memory.retrieve_session_context("truncation-test")
            
            assert len(truncated["chat_history"]) == 10
            print("SUCCESS: Chat history truncation works")
            
            return True
            
        finally:
            os.unlink(temp_file)
            
    except Exception as e:
        print("FAILED: Memory test failed: " + str(e))
        return False

def test_role_router():
    """Test RoleRouter functionality."""
    print("Testing RoleRouter functionality...")
    
    try:
        from agents.role_router import RoleRouter
        
        router = RoleRouter(max_context_tokens=1000)
        print("SUCCESS: RoleRouter initialization works")
        
        # Test context building
        chat_history = [
            {"role": "user", "content": "What is Noah's background?"},
            {"role": "assistant", "content": "Noah has experience in sales and tech."}
        ]
        
        context = router._build_context_from_history(chat_history)
        assert "Previous conversation:" in context
        print("SUCCESS: Context building works")
        
        # Test token truncation
        long_history = []
        for i in range(20):
            long_history.append({
                "role": "user", 
                "content": "Very long message number " + str(i) + " " * 50
            })
        
        truncated = router._truncate_chat_history(long_history)
        assert len(truncated) < len(long_history)
        print("SUCCESS: Token budgeting and truncation works")
        
        return True
        
    except Exception as e:
        print("FAILED: RoleRouter test failed: " + str(e))
        return False

if __name__ == "__main__":
    print("Running memory and router functionality tests...")
    print("=" * 50)
    
    memory_ok = test_memory_functionality()
    print("")
    router_ok = test_role_router()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print("=" * 50)
    
    if memory_ok and router_ok:
        print("SUCCESS: ALL TESTS PASSED!")
        print("")
        print("VERIFIED FEATURES:")
        print("* Rolling chat history: WORKING")
        print("* Role persistent context: WORKING") 
        print("* Multi-turn memory: WORKING")
        print("* Token budgeting + truncation: WORKING")
        print("* Persist memory across sessions: WORKING")
        print("* RoleRouter accepts chat_history: WORKING")
        print("")
        print("Your multi-turn chat system is ready!")
    else:
        print("FAILED: Some tests failed!")
        if not memory_ok:
            print("- Memory functionality failed")
        if not router_ok:
            print("- RoleRouter functionality failed")
