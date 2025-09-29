#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

def test_basic_functionality():
    """Test basic functionality with better error reporting."""
    
    print("Testing basic RAG engine functionality...")
    
    try:
        # Test settings
        from config.settings import Settings
        settings = Settings()
        print("✓ Settings loaded successfully")
        
        # Test RAG engine
        from core.rag_engine import RagEngine
        rag_engine = RagEngine(settings)
        print("✓ RagEngine initialized successfully")
        
        # Test basic query
        result = rag_engine.query("What is Noah's background?")
        print(f"✓ Basic query works: {result['answer'][:50]}...")
        
        # Test role-based query
        result = rag_engine.query("What technical skills does Noah have?", role="Hiring Manager (technical)")
        print(f"✓ Role-based query works: {result['answer'][:50]}...")
        
        # Test RoleRouter
        from agents.role_router import RoleRouter
        from core.memory import Memory
        
        router = RoleRouter()
        memory = Memory()
        
        # Test router functionality
        response = router.route(
            "Hiring Manager (technical)",
            "What are Noah's Python skills?",
            memory,
            rag_engine
        )
        print(f"✓ RoleRouter integration works: {response[:50]}...")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic_functionality()
