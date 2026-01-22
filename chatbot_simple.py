#!/usr/bin/env python3
"""
Medical Chatbot - Groq API Based
A simple medical chatbot using Groq LLM API
"""

import os
from dotenv import load_dotenv
from typing import List, Dict
from groq import Groq

load_dotenv()

class MedicalChatbot:
    """Simple medical chatbot using Groq API"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=api_key)
        self.chat_history = []
        # Try latest available model - will fall back if needed
        self.model = "llama-3.3-70b-versatile"
        
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """
        Send a message to the chatbot and get a response
        
        Args:
            user_message: User input message
            system_prompt: Optional system prompt for the model
            
        Returns:
            Model response
        """
        if not system_prompt:
            system_prompt = """You are a helpful medical chatbot assistant. 
            You provide accurate medical information based on your knowledge.
            Always remind users to consult healthcare professionals for specific medical advice.
            Be empathetic and professional in your responses."""
        
        try:
            # Prepare messages for API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Add chat history for context (last 5 exchanges)
            for i, msg in enumerate(self.chat_history[-10:]):
                messages.insert(1 + i, msg)
            
            # Call Groq API using official SDK
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


def main():
    """Main interactive chatbot loop"""
    
    print("=" * 60)
    print("Medical Chatbot - Powered by Groq API")
    print("=" * 60)
    print("\nInitializing chatbot...\n")
    
    try:
        bot = MedicalChatbot()
        print("✓ Connected to Groq API")
        print("✓ Ready to chat\n")
        print("Commands:")
        print("  'quit' or 'exit' - Exit the chatbot")
        print("  'clear' - Clear chat history")
        print("  'help' - Show this help message")
        print("-" * 60 + "\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using Medical Chatbot. Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                bot.clear_history()
                print("Chat history cleared.\n")
                continue
            
            if user_input.lower() == 'help':
                print("\nCommands:")
                print("  'quit' or 'exit' - Exit the chatbot")
                print("  'clear' - Clear chat history")
                print("  'help' - Show this help message")
                print("-" * 60 + "\n")
                continue
            
            print("\nBot: ", end="", flush=True)
            response = bot.chat(user_input)
            print(response + "\n")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please ensure GROQ_API_KEY is set in .env file")
        return 1
    except KeyboardInterrupt:
        print("\n\nChatbot interrupted by user.")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
