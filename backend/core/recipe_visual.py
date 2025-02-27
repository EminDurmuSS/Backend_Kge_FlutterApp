import json
from core.llm_session import chat_session
from core.llm_generator import generate_recipe_llm
from core.vlm_generator import generate_vlm_prompt, call_vlm_api

def generate_recipe_with_visual(user_criteria: dict) -> str:
    """
    Full pipeline:
    1) Generate a recipe JSON with the LLM (which includes "recipes": [ {...} ])
    2) Generate an image prompt from that recipe JSON
    3) Call the VLM API to get the final image URL
    4) Ask the LLM to produce a final JSON with these keys:
       - "title"
       - "description"
       - "recipe"
       - "image_url"
    5) Return that final JSON string
    """
    print("[DEBUG] Generating recipe JSON with LLM...")
    recipe_json = generate_recipe_llm(user_criteria)
    print(f"[DEBUG] Recipe JSON: {recipe_json}")
    
    # Convert recipe JSON into an image-generation prompt
    print("[DEBUG] Generating VLM prompt from recipe JSON...")
    vlm_prompt = generate_vlm_prompt(recipe_json)
    
    # Call the VLM API to get the image
    print("[DEBUG] Generating image via VLM API...")
    image_url = call_vlm_api(vlm_prompt)

    # Final step: produce a last JSON output summarizing everything
    final_prompt = f"""
You are a creative culinary storyteller. Below is a recipe in JSON format along with a generated image URL representing the dish.

Recipe JSON:
{recipe_json}

Generated Image URL: {image_url}

Please produce a final presentation strictly in JSON format with the following keys:
- "title": The dish's creative title.
- "description": A captivating description that incorporates the image URL.
- "recipe": The original recipe JSON.
- "image_url": The URL of the generated image.

Output only the final JSON.
"""
    print("[DEBUG] Sending final prompt to Gemini LLM for output generation...")
    print(f"[DEBUG] Final prompt:\n{final_prompt}")

    final_response = chat_session.send_message(final_prompt)
    final_text = final_response.text.strip()
    print(f"[DEBUG] Raw final LLM response: {final_text}")

    # Strip code fences if any
    if final_text.startswith("```"):
        lines = final_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        final_text = "\n".join(lines).strip()
    
    print(f"[DEBUG] Final output: {final_text}")
    return final_text
