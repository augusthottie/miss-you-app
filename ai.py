import google.generativeai as genai
import os
import json

# Initialize Gemini AI with error handling
gemini_available = False
gemini_model = None

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-pro')
        gemini_available = True
        print("🤖 Gemini AI initialized successfully")
    else:
        print("⚠️  GOOGLE_API_KEY not found, AI features will be disabled")
except Exception as e:
    print(f"❌ Gemini AI initialization failed: {e}")
    print("   AI features will not be available")


def notify_prompt(source_username, target_username):
    prompt = f"""
    Create a sweet, heartfelt message for a "Miss You" app.

    Context: {source_username} wants to send a message to {target_username}

    Please create:
    1. A short, catchy title (max 30 characters)
    2. A sweet, personal description (max 100 characters)

    Make it feel personal, warm, and genuine. Avoid generic messages,
    you can also use emojis but do not use too many.

    Format your response as json, do not do markdown only return json object.
    {{
        "title": "[title here]",
        "description": "[description here]"
    }}
    """

    return prompt


def generate_notify_message(source_username, target_username):
    """Generate notification message using Gemini AI or fallback"""
    if not gemini_available or not gemini_model:
        print("⚠️  Using fallback message generation (Gemini not available)")
        title = f"Miss you, {target_username}!"
        description = f"{source_username} is thinking about you 💭"
        return title, description

    try:
        prompt = notify_prompt(source_username, target_username)
        response = gemini_model.generate_content(prompt)

        # Remove any leading/trailing whitespace and ```json/``` markers
        cleaned_text = response.text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        parsed = json.loads(cleaned_text)

        default_title = f"Miss you, {target_username}!"
        default_desc = f"{source_username} is thinking about you"
        title = parsed.get("title", default_title)
        description = parsed.get("description", default_desc)

        return title, description

    except Exception as e:
        print(f"❌ Error generating AI message: {e}")
        print("   Using fallback message")
        fallback_title = f"Miss you, {target_username}!"
        fallback_desc = f"{source_username} is thinking about you 💭"
        return fallback_title, fallback_desc
