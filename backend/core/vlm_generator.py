import os
import json
import requests
from core.llm_session import chat_session

# Recraft API integration details
RECRAFT_API_URL = "https://external.api.recraft.ai/v1/images/generations"
RECRAFT_API_KEY = os.environ.get("RECRAFT_API_KEY")

def generate_vlm_prompt(recipe_json: str) -> str:
    """
    Convert the recipe JSON into a vivid prompt for the image-generation model.
    """
    prompt = f"""
You are a world-class food photographer and visual design expert. Based on the following recipe details in JSON,
generate an extremely detailed and vivid image prompt for a high-quality food image. Your description should include:
- The dish's presentation and plating style
- Specific lighting, color palette, and texture details
- Arrangement of key ingredients
- Background setting
- Artistic effects (bokeh, selective focus, etc.)

Limit your output to a maximum of 1000 characters.

Recipe JSON (trimmed if too long):
{recipe_json[:3000]}

Output only the final prompt text.
"""
    print("[DEBUG] Sending improved prompt to LLM for VLM prompt generation...")
    response = chat_session.send_message(prompt)
    vlm_prompt = response.text.strip()
    print(f"[DEBUG] Raw VLM prompt response: {vlm_prompt}")
    
    # Remove code fences if present
    if vlm_prompt.startswith("```"):
        lines = vlm_prompt.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        vlm_prompt = "\n".join(lines).strip()
    
    # Enforce a 1000-character limit
    if len(vlm_prompt) > 1000:
        vlm_prompt = vlm_prompt[:1000]
        print("[DEBUG] Truncated VLM prompt to 1000 characters.")
    
    print(f"[DEBUG] Final VLM prompt: {vlm_prompt}")
    return vlm_prompt

def call_vlm_api(vlm_prompt: str) -> str:
    """
    Call the Recraft (VLM) API with the prompt and return the generated image URL.
    """
    if not RECRAFT_API_KEY:
        raise EnvironmentError("RECRAFT_API_KEY is not set in environment variables.")

    payload = {
        "prompt": vlm_prompt,
        "style": "realistic_image",
        "model": "recraftv3",
        "size": "1024x1024"
    }
    headers = {
        "Authorization": f"Bearer {RECRAFT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("[DEBUG] Calling VLM API with payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(RECRAFT_API_URL, json=payload, headers=headers)
    print(f"[DEBUG] VLM API response status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[DEBUG] VLM API response JSON: {json.dumps(data, indent=2)}")
        # Typically the generated image is in data["data"][0]["url"] or similar
        image_url = data["data"][0]["url"]
        print(f"[DEBUG] Generated Image URL: {image_url}")
        return image_url
    else:
        error_msg = f"VLM API error: {response.text}"
        print(f"[DEBUG] {error_msg}")
        raise Exception(error_msg)
