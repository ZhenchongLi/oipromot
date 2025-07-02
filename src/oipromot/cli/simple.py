"""
Simple CLI interface for basic prompt optimization.
"""

from ..ai.deepseek_client import DeepSeekClient


class SimpleCLI:
    """Simple command-line interface for basic Office prompt optimization."""
    
    def __init__(self):
        self.deepseek = DeepSeekClient()
    
    def run(self):
        """Main loop for simple optimization."""
        print("=== Office Prompt Optimizer ===")
        print("Enter your Office requests and get optimized commands!")
        print("Commands: /q=quit, /e=exit\\n")
        
        while True:
            try:
                user_input = input("Your request: ").strip()
                
                if user_input.lower() in ['/q', '/quit', '/e', '/exit']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("Processing...")
                
                # Try real DeepSeek first, fall back to mock
                optimized = self.deepseek.optimize_prompt(user_input)
                if optimized is None:
                    print("DeepSeek not available, using mock responses...")
                    optimized = self._mock_response(user_input)
                
                print(f"Optimized: {optimized}\\n")
                
            except KeyboardInterrupt:
                print("\\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\\n")
    
    def _mock_response(self, user_input: str) -> str:
        """Simple mock responses for when DeepSeek is not available."""
        mock_responses = {
            "make text bigger": "Increase font size to 14pt for selected text",
            "add numbers to rows": "Insert row numbers in column A starting from 1",
            "make a table": "Create a 3x4 table with headers in row 1",
            "bold text": "Apply bold formatting to selected text",
            "center text": "Align selected text to center",
            "sum column": "Insert SUM formula for selected column range",
            "create chart": "Insert column chart for selected data range A1:B10",
            "freeze rows": "Freeze top row (row 1) for scrolling",
        }
        
        user_lower = user_input.lower()
        for key, response in mock_responses.items():
            if key in user_lower:
                return response
        
        return f"Optimize '{user_input}' for Office automation (specific command needed)"