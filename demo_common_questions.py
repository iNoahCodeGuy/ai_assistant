#!/usr/bin/env python3
"""Demonstration of the Common Questions Analytics System.

This script demonstrates the key functionality of the common questions
system including data tracking, analysis, and UI integration.
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analytics.comprehensive_analytics import (
    ComprehensiveAnalytics, UserInteraction, create_interaction_from_rag_result
)
from src.ui.components.common_questions import (
    CommonQuestionsDisplay, get_question_suggestions
)
from src.integration.common_questions_integration import CommonQuestionsIntegration


def create_sample_data(analytics: ComprehensiveAnalytics):
    """Create realistic sample data for demonstration."""
    print("📊 Creating sample interaction data...")
    
    # Realistic question patterns based on different user roles
    sample_interactions = [
        # Technical Hiring Manager questions
        ("What's Noah's technical background?", "Hiring Manager (technical)", "career", 15),
        ("Show me Noah's code examples", "Hiring Manager (technical)", "technical", 12),
        ("How does he approach system design?", "Hiring Manager (technical)", "technical", 8),
        ("What AI projects has he worked on?", "Hiring Manager (technical)", "career", 6),
        
        # Non-technical Hiring Manager questions  
        ("What's Noah's professional background?", "Hiring Manager (nontechnical)", "career", 18),
        ("Tell me about his achievements", "Hiring Manager (nontechnical)", "career", 10),
        ("How does he work with teams?", "Hiring Manager (nontechnical)", "career", 7),
        ("What industries has he worked in?", "Hiring Manager (nontechnical)", "career", 5),
        
        # Software Developer questions
        ("How does the RAG engine work?", "Software Developer", "technical", 14),
        ("Show me the code architecture", "Software Developer", "technical", 11),
        ("How is the vector store implemented?", "Software Developer", "technical", 9),
        ("What's the role routing logic?", "Software Developer", "technical", 7),
        ("How does the memory system work?", "Software Developer", "technical", 5),
        
        # Casual visitor questions
        ("Tell me about Noah", "Just looking around", "general", 20),
        ("What's interesting about him?", "Just looking around", "fun", 8),
        ("Noah MMA fight", "Just looking around", "mma", 6),
        ("What does he do for work?", "Just looking around", "career", 4),
    ]
    
    # Generate interactions with realistic patterns
    session_counter = 0
    for question, role, query_type, frequency in sample_interactions:
        for i in range(frequency):
            session_counter += 1
            
            # Simulate realistic response patterns
            if query_type == "technical":
                code_snippets = 2 + (i % 3)
                citations = 3 + (i % 4)
                response_length = 600 + (i % 300)
            elif query_type == "career":
                code_snippets = 0 if role == "Hiring Manager (nontechnical)" else 1
                citations = 1 + (i % 2)
                response_length = 400 + (i % 200)
            else:
                code_snippets = 0
                citations = 0
                response_length = 200 + (i % 150)
            
            interaction = UserInteraction(
                session_id=f"demo_session_{session_counter}",
                timestamp=datetime.now() - timedelta(days=i % 30, hours=i % 24),
                user_role=role,
                query=question,
                query_type=query_type,
                response_time=1.2 + (i % 4 * 0.5),
                response_length=response_length,
                code_snippets_shown=code_snippets,
                citations_provided=citations,
                success=True,  # Most interactions successful
                follow_up_query=i % 5 == 0,  # 20% are follow-ups
                conversation_turn=1 + (i % 3)
            )
            
            analytics.log_interaction(interaction)
    
    print(f"✅ Created {session_counter} sample interactions")


def demonstrate_analytics_capabilities(analytics: ComprehensiveAnalytics):
    """Demonstrate analytics and insights capabilities."""
    print("\n" + "="*60)
    print("📈 ANALYTICS CAPABILITIES DEMONSTRATION")
    print("="*60)
    
    # 1. Most Common Questions Overall
    print("\n🔥 Most Common Questions (All Roles):")
    print("-" * 40)
    common_questions = analytics.get_most_common_questions(days=30, limit=5)
    
    for i, q_data in enumerate(common_questions, 1):
        question = q_data['question']
        frequency = q_data['frequency']
        success_rate = q_data['success_rate']
        roles = q_data.get('roles', [])
        
        print(f"{i}. {question}")
        print(f"   📊 Asked {frequency} times | ✅ {success_rate:.1%} success")
        print(f"   👥 Popular with: {', '.join(roles[:2])}")
        print()
    
    # 2. Role-Specific Patterns
    print("\n🎭 Questions by Role:")
    print("-" * 40)
    role_questions = analytics.get_common_questions_by_role(days=30, limit_per_role=3)
    
    for role, questions in role_questions.items():
        if questions:
            print(f"\n📋 {role}:")
            for q_data in questions:
                question = q_data['question']
                frequency = q_data['frequency']
                query_type = q_data.get('query_type', 'general')
                print(f"   • {question} ({frequency}x, {query_type})")
    
    # 3. User Behavior Insights
    print("\n\n🧠 User Behavior Insights:")
    print("-" * 40)
    insights = analytics.get_user_behavior_insights(days=30)
    
    if insights:
        print(f"Total interactions: {insights.get('total_interactions', 0)}")
        print(f"Active roles: {len(insights.get('role_distribution', {}))}")
        
        # Role distribution
        role_dist = insights.get('role_distribution', {})
        print("\nRole popularity:")
        for role, count in sorted(role_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / sum(role_dist.values())) * 100
            print(f"   {role}: {count} interactions ({percentage:.1f}%)")
        
        # Performance by role
        performance = insights.get('performance_by_role', {})
        if performance:
            print("\nPerformance by role:")
            for role, metrics in performance.items():
                success_rate = metrics.get('success_rate', 0)
                avg_time = metrics.get('avg_response_time', 0)
                print(f"   {role}: {success_rate:.1%} success, {avg_time:.2f}s avg response")
    
    # 4. Content Effectiveness
    print("\n\n📊 Content Effectiveness:")
    print("-" * 40)
    content_report = analytics.get_content_effectiveness_report()
    
    if content_report.get('top_content'):
        print("Most accessed content:")
        for item in content_report['top_content'][:3]:
            content_type = item['type']
            content_id = item['id']
            access_count = item['access_count']
            relevance = item['relevance_score']
            print(f"   • {content_type}: {content_id}")
            print(f"     {access_count} accesses, {relevance:.1f}/1.0 relevance")


def demonstrate_ui_integration(analytics: ComprehensiveAnalytics):
    """Demonstrate UI component capabilities."""
    print("\n" + "="*60)
    print("🖥️  UI INTEGRATION DEMONSTRATION")
    print("="*60)
    
    display = CommonQuestionsDisplay(analytics_system=analytics)
    
    # Test different roles
    roles_to_test = [
        "Software Developer",
        "Hiring Manager (technical)", 
        "Hiring Manager (nontechnical)",
        "Just looking around"
    ]
    
    for role in roles_to_test:
        print(f"\n👤 {role} Experience:")
        print("-" * 40)
        
        # Get suggestions (simulating what UI would show)
        suggestions = get_question_suggestions(role, analytics_system=analytics, limit=3)
        
        print("Quick suggestions they would see:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        # Show analytics-driven questions
        analytics_questions = analytics.get_most_common_questions(role=role, days=30, limit=2)
        if analytics_questions:
            print("\nData-driven popular questions:")
            for q_data in analytics_questions:
                question = q_data['question']
                frequency = q_data['frequency']
                print(f"   💡 {question} (asked {frequency} times)")


def demonstrate_integration_layer():
    """Demonstrate the complete integration capabilities."""
    print("\n" + "="*60)
    print("🔗 INTEGRATION LAYER DEMONSTRATION")
    print("="*60)
    
    # Create integration (normally would connect to real RAG engine)
    integration = CommonQuestionsIntegration()
    
    print("\n✅ Integration Features Available:")
    print("   • Analytics tracking enabled:", integration.analytics_enabled)
    print("   • Common questions display ready")
    print("   • Sidebar suggestions ready") 
    print("   • Performance monitoring ready")
    print("   • Content effectiveness tracking ready")
    
    # Simulate a question processing cycle
    if integration.analytics_enabled:
        print("\n🔄 Simulated Question Processing:")
        
        # Mock RAG result
        mock_rag_result = {
            'response': 'This is a detailed technical response about the RAG engine implementation.',
            'code_snippets': [
                {'citation': 'src/core/rag_engine.py:100-120'},
                {'citation': 'src/retrieval/code_index.py:50-70'}
            ]
        }
        
        # Track interaction
        success = integration.track_user_interaction(
            session_id="demo_session_integration",
            user_role="Software Developer",
            query="How does the RAG engine work?",
            query_type="technical",
            response_time=2.3,
            rag_result=mock_rag_result,
            conversation_turn=1
        )
        
        print(f"   • Interaction tracking: {'✅ Success' if success else '❌ Failed'}")
        
        # Get personalized suggestions
        suggestions = integration.get_personalized_suggestions(
            role="Software Developer",
            session_history=["How does the RAG engine work?"]
        )
        
        print(f"   • Personalized suggestions: {len(suggestions)} generated")
        for suggestion in suggestions[:2]:
            print(f"     - {suggestion}")


def main():
    """Run the complete demonstration."""
    print("🚀 Noah's AI Assistant - Common Questions System Demo")
    print("=" * 60)
    
    # Create temporary database for demo
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize analytics system
        analytics = ComprehensiveAnalytics(db_path=db_path)
        
        # Create sample data
        create_sample_data(analytics)
        
        # Demonstrate capabilities
        demonstrate_analytics_capabilities(analytics)
        demonstrate_ui_integration(analytics)
        demonstrate_integration_layer()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRATION COMPLETE")
        print("="*60)
        print("\n📋 Key Features Demonstrated:")
        print("   • ✅ Question frequency tracking")
        print("   • ✅ Role-based analytics")
        print("   • ✅ User behavior insights")
        print("   • ✅ Content effectiveness measurement")
        print("   • ✅ UI component integration")
        print("   • ✅ Real-time suggestion generation")
        print("   • ✅ Performance monitoring")
        print("   • ✅ Seamless fallback to static questions")
        
        print("\n🎯 Next Steps:")
        print("   1. Integrate with main Streamlit app")
        print("   2. Connect to existing RAG engine")
        print("   3. Add user feedback collection")
        print("   4. Set up production analytics dashboard")
        
        analytics.close()
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    main()
