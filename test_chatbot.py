#!/usr/bin/env python3
"""
Test script for Medical Chatbot
"""

import sys
sys.path.insert(0, 'c:\\Users\\thama\\Downloads\\Med-chatbot')

from chatbot_simple import MedicalChatbot

def main():
    print("Testing Medical Chatbot...\n")
    
    try:
        bot = MedicalChatbot()
        print("✓ Chatbot initialized successfully\n")
        
        # Test message
        test_questions = [
            "What are the symptoms of hypertension?",
            "How can I prevent heart disease?"
        ]
        
        for question in test_questions:
            print(f"Q: {question}")
            response = bot.chat(question)
            print(f"A: {response}\n")
            print("-" * 60 + "\n")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
