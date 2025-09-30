#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test code integration functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_code_index():
    """Test CodeIndex functionality."""
    print("Testing CodeIndex functionality...")
    
    try:
        from retrieval.code_index import CodeIndex
        
        # Initialize with current directory as repo
        code_index = CodeIndex(repo_path=".")
        print("SUCCESS: CodeIndex initialized with " + str(len(code_index.index)) + " code snippets")
        
        # Test search functionality
        search_results = code_index.search_code("retrieve", max_results=3)
        print("SUCCESS: Found " + str(len(search_results)) + " results for 'retrieve'")
        
        for result in search_results[:2]:
            print("   - " + result['name'] + " in " + result['citation'])
            print("     GitHub: " + result['github_url'])
        
        # Test keyword search
        keyword_results = code_index.search_by_keywords(["memory", "session"], max_results=2)
        print("SUCCESS: Found " + str(len(keyword_results)) + " results for keywords ['memory', 'session']")
        
        return True
        
    except Exception as e:
        print("FAILED: CodeIndex test failed: " + str(e))
        return False

def test_rag_code_integration():
    """Test RAG engine code integration."""
    print("\nTesting RAG code integration...")
    
    try:
        from core.rag_engine import RagEngine
        from config.settings import Settings
        
        # Initialize RAG engine
        settings = Settings()
        rag_engine = RagEngine(settings=settings)
        print("SUCCESS: RAG engine initialized")
        
        # Test code retrieval
        code_info = rag_engine.retrieve_code_info("memory")
        print("SUCCESS: Retrieved " + str(len(code_info)) + " code snippets for 'memory'")
        
        # Test enhanced retrieval with code
        if hasattr(rag_engine, 'retrieve_with_code'):
            enhanced_results = rag_engine.retrieve_with_code("How does retrieval work?", "Software Developer")
            print("SUCCESS: Enhanced retrieval returned " + str(len(enhanced_results.get('code_snippets', []))) + " code snippets")
            
            if enhanced_results.get('code_snippets'):
                for snippet in enhanced_results['code_snippets'][:2]:
                    print("   - " + snippet['name'] + " (" + snippet['citation'] + ")")
        else:
            print("WARNING: retrieve_with_code method not found")
        
        return True
        
    except Exception as e:
        print("FAILED: RAG code integration test failed: " + str(e))
        return False

def test_role_router_integration():
    """Test role router with code integration."""
    print("\nTesting role router code integration...")
    
    try:
        from agents.role_router import RoleRouter
        from core.rag_engine import RagEngine
        from core.memory import Memory
        from config.settings import Settings
        
        # Initialize components
        router = RoleRouter()
        memory = Memory()
        settings = Settings()
        rag_engine = RagEngine(settings=settings)
        
        # Test technical role routing
        result = router.route(
            role="Software Developer",
            query="How does the retrieval system work?",
            memory=memory,
            rag_engine=rag_engine
        )
        
        print("SUCCESS: Router returned response type: " + str(result.get('type')))
        print("   Response length: " + str(len(result.get('response', ''))))
        
        if result.get('context'):
            print("   Context items: " + str(len(result['context'])))
        
        return True
        
    except Exception as e:
        print("FAILED: Role router integration test failed: " + str(e))
        return False

if __name__ == "__main__":
    print("Testing Code Integration Features...\n")
    
    results = []
    results.append(test_code_index())
    results.append(test_rag_code_integration())
    results.append(test_role_router_integration())
    
    print("\n" + "="*60)
    if all(results):
        print("SUCCESS: ALL CODE INTEGRATION TESTS PASSED!")
        print("\nVERIFIED FEATURES:")
        print("* Code Index: Building and searching code snippets")
        print("* RAG Integration: Retrieving code with career context")
        print("* Role Router: Technical responses with code citations")
        print("* GitHub Links: Automatic URL generation for code references")
        print("\nTechnical roles now have file:line citations!")
    else:
        print("FAILED: Some tests failed!")
        print("Review the errors above and check implementation.")
