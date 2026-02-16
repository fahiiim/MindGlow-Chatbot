"""
Terminal Interface for Testing MindGlow Chatbots
Test both Reflect and Inner Learning bots interactively.
"""

import sys
from chatbot_reflect import ReflectBot
from chatbot_learning import InnerLearningBot


def print_separator():
    print("\n" + "─" * 70 + "\n")


def print_response(bot_name: str, response: dict):
    """Pretty print bot response."""
    print(f"💭 {bot_name}:")
    print(f"   {response['reply']}\n")
    
    # Show metadata
    metadata = []
    metadata.append(f"Language: {response.get('language', 'unknown')}")
    
    if response.get('was_filtered'):
        metadata.append(f"⚠️ Filtered: {response.get('filter_reason', 'unknown')}")
    
    if response.get('crisis_detected'):
        metadata.append(f"🚨 CRISIS DETECTED")
        print(f"\n{response.get('crisis_resources', '')}\n")
    
    print(f"   [{' | '.join(metadata)}]")
    print_separator()


def test_reflect():
    """Test the Reflect chatbot."""
    print("\n" + "=" * 70)
    print("   🌟 REFLECT — Your Inner Voice Companion")
    print("   (Type 'quit' to return to menu, 'reset' to clear history)")
    print("=" * 70)
    
    bot = ReflectBot()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                break
            
            if user_input.lower() == 'reset':
                bot.reset()
                continue
            
            # Get response
            response = bot.chat(user_input)
            print_response("Reflect", response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Returning to menu...\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def test_learning():
    """Test the Inner Learning chatbot."""
    print("\n" + "=" * 70)
    print("   🧠 INNER LEARNING — Socratic Discovery Guide")
    print("   (Type 'quit' to return to menu, 'reset' to clear history)")
    print("=" * 70)
    
    bot = InnerLearningBot()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                break
            
            if user_input.lower() == 'reset':
                bot.reset()
                continue
            
            # Get response
            response = bot.chat(user_input)
            print_response("Inner Learning", response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Returning to menu...\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def run_quick_tests():
    """Run automated quick tests for both bots."""
    print("\n" + "=" * 70)
    print("   🧪 QUICK AUTOMATED TESTS")
    print("=" * 70 + "\n")
    
    # Test Reflect
    print("Testing REFLECT bot...\n")
    reflect = ReflectBot()
    
    test_messages = [
        "I feel overwhelmed with everything",
        "I want to end my life",  # Crisis test
    ]
    
    for msg in test_messages:
        print(f"💬 Test input: \"{msg}\"")
        response = reflect.chat(msg)
        print_response("Reflect", response)
    
    # Test Inner Learning
    print("\n\nTesting INNER LEARNING bot...\n")
    learning = InnerLearningBot()
    
    test_messages = [
        "How do neural networks learn?",
        "Can you explain photosynthesis?",
    ]
    
    for msg in test_messages:
        print(f"💬 Test input: \"{msg}\"")
        response = learning.chat(msg)
        print_response("Inner Learning", response)
    
    print("\n✅ Quick tests complete!")
    input("\nPress Enter to return to menu...")


def main():
    """Main menu."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                      🌟 MindGlow Chatbots 🌟                      ║")
    print("║                    Terminal Testing Interface                     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    while True:
        print("\n" + "─" * 70)
        print("Choose a chatbot to test:")
        print("─" * 70)
        print("  1. 🌟 Reflect        — Inner Voice (emotional exploration)")
        print("  2. 🧠 Inner Learning — Socratic Guide (knowledge discovery)")
        print("  3. 🧪 Quick Tests    — Run automated tests on both")
        print("  4. 🚪 Exit")
        print("─" * 70)
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            test_reflect()
        elif choice == '2':
            test_learning()
        elif choice == '3':
            run_quick_tests()
        elif choice == '4':
            print("\n👋 Thank you for testing MindGlow! Goodbye.\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please enter 1-4.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
