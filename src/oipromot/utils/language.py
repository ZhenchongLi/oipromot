"""
Language detection and handling utilities.
"""


def is_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def get_language_code(text: str) -> str:
    """Get language code for the given text."""
    return "zh" if is_chinese(text) else "en"


def localize_message(message_key: str, language: str = "en", **kwargs) -> str:
    """Get localized message for the given key and language."""
    messages = {
        "en": {
            "app_selection": "App: 0=Word, 1=Excel",
            "selected_app": "Selected {app}. Please describe the specific task.",
            "ai_strength": "✅AI Strength: {reason}",
            "vba_strength": "🔧VBA Strength: {reason}",
            "hybrid_approach": "🔀Hybrid approach: AI+VBA",
            "provide_details": "Provide more details to determine best approach",
            "conversation_cleared": "🧹 Conversation cleared! Starting fresh with new memory.",
            "goodbye": "👋 Goodbye!",
            "processing": "🤔 Processing...",
            "error": "❌ Error: {error}"
        },
        "zh": {
            "app_selection": "应用选择：0=Word, 1=Excel",
            "selected_app": "已选择{app}。请继续描述具体任务。",
            "ai_strength": "✅AI优势任务：{reason}",
            "vba_strength": "🔧VBA优势任务：{reason}",
            "hybrid_approach": "🔀混合方案：AI+VBA",
            "provide_details": "请提供更多细节以确定最佳方案",
            "conversation_cleared": "🧹 对话已清除！开始新的记忆。",
            "goodbye": "👋 再见！",
            "processing": "🤔 处理中...",
            "error": "❌ 错误：{error}"
        }
    }
    
    lang_messages = messages.get(language, messages["en"])
    message = lang_messages.get(message_key, message_key)
    
    return message.format(**kwargs) if kwargs else message