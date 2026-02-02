import os
import json
import time
import google.generativeai as genai
from google.api_core import exceptions

class AIEngine:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            self.enabled = True
        else:
            print("Warning: GEMINI_API_KEY not found. AI features disabled.")
            self.enabled = False

    def process_thought(self, raw_text, known_entities_context):
        """
        Unified pipeline: Parse -> Refine -> Route.
        """
        if not self.enabled:
            return {"refined_content": raw_text, "action": "fallback"}

        prompt = f"""
        You are an intelligent personal memory assistant. 
        
        **INPUT RULES:**
        The user input may contain CONTENT and COMMANDS.
        - Commands are ALWAYS prefixed with `@ai`.
        - Syntax: `[Content] @ai [Instruction]`
        - Example: `The server crashed again @ai fix grammar and save to incidents`
        - Example: `@ai research quantum computing`
        - IGNORE plain `@` symbols (e.g. email addresses, decorators like @dataclass). 
        - IGNORE `#` symbols (markdown headers, comments).
        - ONLY process text after `@ai` as instructions.

        **YOUR JOB:**
        1. **Interpret:** Separate content from `@ai` commands.
        2. **Execute:** Apply commands to the content (fix grammar, remove quotes, expand, etc.).
           - If no commands, preserve content exactly as is.
           - **CRITICAL:** The `refined_content` field MUST NOT contain the `@ai` command text. You MUST strip the instructions.
        3. **Route:** Decide where to save the result.
           - **Categorization:** Prefer specific subjects (e.g. "Philosophy", "Cooking", "Science") over generic "People" or "Ideas".
           - Check **Known Entities**: {known_entities_context}
           - If content matches an existing entity, use `action: "append"` and the EXACT `entity` and `folder` names.
           - If New, create a meaningful Folder/Entity.

        **OUTPUT JSON:**
        {{
            "refined_content": "Final text to save (Markdown format, NO @ai commands)",
            "entity": "EntityName",
            "folder": "FolderName",
            "action": "append" | "new" | "ambiguous",
            "summary": "One sentence summary"
        }}

        **RAW INPUT:**
        {raw_text}
        """

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                text = response.text.strip()
                if text.startswith("```json"): text = text[7:]
                if text.endswith("```"): text = text[:-3]
                    
                return json.loads(text)
                
            except exceptions.ResourceExhausted:
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    print("AI Error: Rate limit exceeded.")
                    return {"action": "error", "error": "rate_limit"}
            except Exception as e:
                print(f"AI Error: {e}")
                return {"action": "error", "error": str(e)}
