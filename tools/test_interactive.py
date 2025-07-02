#!/usr/bin/env python3
"""
Test Interactive Office Prompt Optimizer
Demonstrates conversational optimization with sample inputs
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from oipromot.deepseek_service import DeepSeekService


def test_conversational_flow():
    print("=== Interactive Office Optimizer Demo ===")
    print("Showing conversational optimization with sample inputs...\n")
    
    deepseek = DeepSeekService()
    conversation_history = []
    
    def add_to_history(role: str, content: str):
        conversation_history.append({"role": role, "content": content})
    
    def smart_mock_response(user_input: str) -> str:
        """Smart mock that asks questions or gives concise commands"""
        user_lower = user_input.lower()
        
        # Content generation requests
        if any(word in user_lower for word in ["write", "generate", "create content", "draft"]):
            return "What type of document? (letter, report, contract, etc.)"
        
        # Font/formatting
        if "bigger" in user_lower or "字号" in user_lower or "font" in user_lower:
            if "size" not in user_lower and "14" not in user_lower:
                return "What font size? (12pt, 14pt, 16pt, etc.)"
            return "Select text → Home → Font Size → 14pt"
        
        # Table operations
        if "table" in user_lower or "表格" in user_lower:
            if not any(num in user_lower for num in ["3", "4", "5", "rows", "columns"]):
                return "How many rows and columns? (e.g., 3x4 table)"
            return "Insert → Table → 3 rows × 4 columns"
        
        # Excel formulas
        if "sum" in user_lower or "求和" in user_lower:
            if not any(col in user_lower for col in ["a:", "b:", "column", "range"]):
                return "Which column or range? (e.g., A:A, B2:B10)"
            return "=SUM(A:A)"
        
        # Specific responses for follow-ups
        if "14pt" in user_lower:
            return "Select text → Home → Font Size → 14pt"
        if "3x4" in user_lower or "3 rows" in user_lower:
            return "Insert → Table → 3 rows × 4 columns"
        if "column a" in user_lower or "a:a" in user_lower:
            return "=SUM(A:A)"
        
        return f"For '{user_input}' - which application (Word/Excel) and what specifically?"
    
    # Test conversation flows
    test_conversations = [
        # Flow 1: Font size clarification
        ["make text bigger", "14pt"],
        
        # Flow 2: Table creation
        ["create a table", "3x4 table"],
        
        # Flow 3: Excel sum
        ["sum column", "column A"],
        
        # Flow 4: Chinese input
        ["字号调大一点", "14磅"],
        
        # Flow 5: Content generation
        ["write a document", "business letter"]
    ]
    
    for conversation in test_conversations:
        print(f"{'='*50}")
        conversation_history = []  # Reset for each test
        
        for i, user_input in enumerate(conversation):
            print(f"👤 User: {user_input}")
            
            # Try DeepSeek first, fallback to mock
            if deepseek.api_key:
                context = ""
                if conversation_history:
                    context = "\nPrevious conversation:\n"
                    for msg in conversation_history[-4:]:
                        context += f"{msg['role']}: {msg['content']}\n"
                
                full_prompt = f"""You are an OfficeAI assistant for Word and Excel automation. Based on the conversation, provide either:
1. A precise, concise command (1-2 lines max)
2. ONE clarifying question to better understand

Rules:
- Focus ONLY on Word and Excel
- Keep responses very short
- Use specific parameters when possible

{context}
Current request: {user_input}

Response:"""
                
                response = deepseek.optimize_prompt_with_context(full_prompt)
                if response:
                    source = "(DeepSeek)"
                else:
                    response = smart_mock_response(user_input)
                    source = "(mock)"
            else:
                response = smart_mock_response(user_input)
                source = "(mock)"
            
            print(f"🤖 Assistant: {response} {source}")
            
            add_to_history("user", user_input)
            add_to_history("assistant", response)
            
            print()
    
    print("Demo completed! 🎉")


if __name__ == "__main__":
    test_conversational_flow()