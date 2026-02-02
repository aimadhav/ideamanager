from datetime import datetime
import re
import json
import os
from src.config import RAW_HISTORY_FILE, MEMORIES_DIR, BASE_DIR, LOGS_DIR
from src.file_ops import pop_inbox, append_to_file
from src.registry import Registry
from src.ai_engine import AIEngine

# Initialize Singletons
registry = Registry()
ai = AIEngine()

def log_transaction(raw_input, ai_output):
    """Logs the input and AI decision for debugging."""
    log_file = LOGS_DIR / "ingestion.log"
    entry = f"""
=== {datetime.now()} ===
INPUT:
{raw_input}

AI OUTPUT:
{json.dumps(ai_output, indent=2, ensure_ascii=False)}
========================
"""
    append_to_file(log_file, entry)

def process_inbox():
    """Main ingestion logic - AI Driven."""
    # Note: Locking is now handled by the Queue consumer in main.py
    
    # Atomic Read & Clear
    content = pop_inbox()
    
    if not content or not content.strip():
        # Silent return to avoid log spam on empty checks
        return

    print(f"Processing content: {content[:50]}...")

    # 1. Raw Backup
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_entry = f"--- {timestamp} ---\n{content}\n----------------\n"
    append_to_file(RAW_HISTORY_FILE, raw_entry)
    print("Backed up to raw history.")

    # 2. AI Processing
    print("Processing with AI...")
    context = registry.get_all_entities_summary()
    
    # Send everything to AI
    result = ai.process_thought(content, context)
    
    # Log the result
    log_transaction(content, result)
    
    # Ensure result is a dict (fallback for extreme errors)
    if not isinstance(result, dict):
        result = {"action": "fallback", "refined_content": content}

    # 3. Extract Decisions
    action = result.get("action", "fallback")
    refined_content = result.get("refined_content", content)
    
    # Safety: If refined_content is missing
    if refined_content is None: 
        refined_content = content

    # FIX: Strip commands from the final output (only lines/segments starting with @ai)
    if refined_content:
        # Regex explanation:
        # (?m) -> Multiline mode
        # (?i) -> Case insensitive (@AI, @ai)
        # @ai -> Matches literal @ai
        # .* -> Matches rest of the line
        refined_content = re.sub(r'(?m)(?i)^@ai.*$', '', refined_content)
        # Also remove trailing @ai commands if they are on the same line
        refined_content = re.sub(r'(?i)\s+@ai\s+.*$', '', refined_content).strip()

    entity_name = result.get("entity")
    folder = result.get("folder", "Unsorted")
    summary = result.get("summary", "")

    # 4. Execution
    if action == "fallback" or action == "error":
        print(f"AI Action: {action}. Saving to Unsorted.")
        target_file = MEMORIES_DIR / "Unsorted.md"
        append_to_file(target_file, f"\n## {timestamp}\n{refined_content}\n")

    elif action == "ambiguous":
        decision_file = BASE_DIR / "_decisions.txt"
        append_to_file(decision_file, f"\n[AMBIGUOUS] {timestamp}\nContent: {refined_content}\n")
        print("Ambiguous content flagged.")

    elif action in ["new", "append"]:
        final_entity_name = str(entity_name) if entity_name else "Unknown"
        final_folder = str(folder) if folder else "Unsorted"
        final_summary = str(summary) if summary else ""

        safe_entity = re.sub(r'[^\w\s-]', '', final_entity_name).strip().replace(' ', '_').lower()
        safe_folder = re.sub(r'[^\w\s-]', '', final_folder).strip().replace(' ', '_').lower()
        
        folder_path = MEMORIES_DIR / safe_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / f"{safe_entity}.md"
        
        append_to_file(file_path, f"\n## {timestamp}\n{refined_content}\n")
        
        if action == "new":
            registry.add_entity(final_entity_name, safe_folder, str(file_path.relative_to(BASE_DIR)), final_summary)
        else:
            registry.update_entity_timestamp(final_entity_name)
            
        print(f"Processed: {action.upper()} -> {file_path}")

    # Cleanup is done at start (pop_inbox)

if __name__ == "__main__":
    process_inbox()
