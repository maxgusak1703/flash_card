# core/ai_service.py

import json

try:
    import google.generativeai as genai
    HAS_AI = True
except ImportError:
    HAS_AI = False

def generate_flashcards(api_key, topic, count, lang_q, lang_a, context):
    """Викликає Gemini API для генерації карток"""

    if not HAS_AI:
        raise RuntimeError("Бібліотека 'google-generativeai' не знайдена.")

    genai.configure(api_key=api_key)
    
    # Вибираємо модель
    try:
        model = genai.GenerativeModel('gemini-2.0-flash') 
    except:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            model = genai.GenerativeModel(available_models[0])
        else:
            raise Exception("Не знайдено доступних моделей для генерації контенту")

    context_str = f". Додаткові умови: {context}" if context else ""
    
    prompt = f"""
    Create exactly {count} flashcards about "{topic}".
    Question Language: {lang_q}.
    Answer Language: {lang_a}.
    Context/Style: {context_str}.
    Output format: A raw JSON array of objects. No markdown formatting.
    Keys: "q" (question/term), "a" (answer/definition).
    """
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    if text.startswith("```json"): text = text[7:]
    if text.startswith("```"): text = text[3:]
    if text.endswith("```"): text = text[:-3]
    
    cards = json.loads(text)
    return cards