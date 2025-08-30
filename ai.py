import google.generativeai as genai
import os
import json


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

gemini_model = genai.GenerativeModel('gemini-2.5-flash')


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

    title = parsed["title"]
    description = parsed["description"]

    return title, description
