"""
Quick Demo — Test both chatbots with sample conversations
"""

from chatbot_reflect import ReflectBot
from chatbot_learning import InnerLearningBot


def demo_reflect():
    """Demo Reflect bot with emotional exploration."""
    print("\n" + "=" * 70)
    print("   🌟 REFLECT BOT DEMO — Inner Voice Companion")
    print("=" * 70 + "\n")
    
    bot = ReflectBot()
    
    conversations = [
        "I've been feeling really overwhelmed with work lately",
        "I don't know, everything just feels like too much",
        "Maybe... I feel like I'm not doing enough",
    ]
    
    for user_msg in conversations:
        print(f"💬 You: {user_msg}")
        response = bot.chat(user_msg)
        print(f"\n💭 Reflect: {response['reply']}")
        print(f"   [Language: {response['language']} | Filtered: {response['was_filtered']}]\n")
        print("─" * 70 + "\n")


def demo_learning():
    """Demo Inner Learning bot with Socratic discovery."""
    print("\n" + "=" * 70)
    print("   🧠 INNER LEARNING BOT DEMO — Socratic Discovery")
    print("=" * 70 + "\n")
    
    bot = InnerLearningBot()
    
    conversations = [
        "How does machine learning work?",
        "I think it involves patterns and data?",
        "Maybe it learns by finding patterns in examples?",
    ]
    
    for user_msg in conversations:
        print(f"💬 You: {user_msg}")
        response = bot.chat(user_msg)
        print(f"\n🧠 Inner Learning: {response['reply']}")
        print(f"   [Language: {response['language']} | Filtered: {response['was_filtered']}]\n")
        print("─" * 70 + "\n")


def demo_crisis_detection():
    """Demo crisis detection in Reflect bot."""
    print("\n" + "=" * 70)
    print("   🚨 CRISIS DETECTION DEMO")
    print("=" * 70 + "\n")
    
    bot = ReflectBot()
    
    print("💬 You: I don't want to live anymore")
    response = bot.chat("I don't want to live anymore")
    
    print(f"\n💭 Reflect: {response['reply']}\n")
    
    if response['crisis_detected']:
        print("🚨 CRISIS DETECTED!")
        print(f"   Indicators: {response.get('crisis_indicators', [])}")
        print(f"\n{response['crisis_resources']}\n")
    
    print("─" * 70 + "\n")


def demo_filter():
    """Demo response filtering (note: bots usually avoid directives, but we can show intent)."""
    print("\n" + "=" * 70)
    print("   ⚠️ RESPONSE FILTER INFO")
    print("=" * 70 + "\n")
    
    print("Both bots automatically filter their responses:")
    print("  • Blocked phrases: 'you should', 'try doing', 'I recommend', etc.")
    print("  • If detected: Auto-regenerates up to 2 times")
    print("  • Learning bot also blocks: 'the answer is', 'let me explain', etc.")
    print("\n  This ensures both bots maintain their non-directive principles.\n")
    print("─" * 70 + "\n")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║                  🌟 MindGlow Chatbots Demo 🌟                     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\nRunning automated demos of both chatbots...\n")
    
    # Run demos
    demo_reflect()
    demo_learning()
    demo_crisis_detection()
    demo_filter()
    
    print("\n✅ Demo complete!")
    print("\n💡 To test interactively, run: python test_bots.py\n")
