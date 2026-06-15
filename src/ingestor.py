from datetime import datetime
import re
import json
import os
import glob
import shutil
from pathlib import Path
from src.config import RAW_HISTORY_FILE, MEMORIES_DIR, BASE_DIR, LOGS_DIR, INBOX_BUFFER_DIR, LIBRARY_DIR, MEDIA_DIR
from src.file_ops import pop_inbox, append_to_file
from src.registry import Registry
from src.ai_engine import AIEngine
from src.capabilities import Capabilities

# Initialize Singletons
registry = Registry()
ai = AIEngine()

def log_transaction(raw_input, ai_output, source="text"):
    """Logs the input and AI decision for debugging."""
    log_file = LOGS_DIR / "ingestion.log"
    entry = f"""
=== {datetime.now()} [{source}] ===
INPUT:
{raw_input[:1000]}...

AI OUTPUT:
{json.dumps(ai_output, indent=2, ensure_ascii=False)}
========================
"""
    append_to_file(log_file, entry)

def _move_to_media(filepath):
    """Moves a file to Memories/Media/YYYY/MM/filename.ext"""
    try:
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        target_dir = MEDIA_DIR / year / month
        target_dir.mkdir(parents=True, exist_ok=True)
        
        src_path = Path(filepath)
        filename = src_path.name
        # Clean filename
        safe_name = re.sub(r'[^\w\s\-\.]', '', filename).replace(' ', '_').lower()
        
        dest_path = target_dir / safe_name
        
        # Handle duplicates
        if dest_path.exists():
            timestamp = int(now.timestamp())
            dest_path = target_dir / f"{timestamp}_{safe_name}"
            
        shutil.move(src_path, dest_path)
        return dest_path
    except Exception as e:
        print(f"Error moving media: {e}")
        return None

def _enrich_content(text, attachment_path=None):
    """
    Expands content by:
    1. Extracting limited text from PDF attachments (1000 chars)
    2. Fetching content from URLs (YouTube/Web)
    Returns: (enriched_text_for_ai)
    """
    ai_context_blocks = []
    
    # 1. Attachment Handling (PDF only, 1000 chars)
    if attachment_path:
        file_ext = attachment_path.suffix.lower()
        if file_ext == ".pdf":
            print(f"   Reading PDF Snippet: {attachment_path.name}")
            pdf_text = Capabilities.extract_pdf_text(attachment_path)
            if pdf_text:
                snippet = pdf_text[:1000]
                ai_context_blocks.append(f"\n--- [PDF SNIPPET: {attachment_path.name}] ---\n{snippet}\n-----------------------------------\n")
    
    # 2. Link Expansion
    urls = Capabilities.extract_urls(text)
    for url in urls:
        print(f"   Found Link: {url}")
        if Capabilities.is_youtube_url(url):
            print("   Fetching YouTube Transcript...")
            title, transcript = Capabilities.fetch_youtube_transcript(url)
            if transcript:
                ai_context_blocks.append(f"\n--- [YOUTUBE TRANSCRIPT: {title}] ---\n{transcript[:20000]}\n-----------------------------------\n")
        else:
            print("   Fetching Web Article...")
            title, content = Capabilities.fetch_web_content(url)
            if content:
                ai_context_blocks.append(f"\n--- [WEB CONTENT: {title}] ---\n{content}\n-----------------------------------\n")

    return "".join(ai_context_blocks)

def _finalize_item(content, source="text", extra_context=""):
    """Shared logic to send to AI and save result."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Prepare Prompt
    full_prompt = f"{content}\n\n{extra_context}"
    
    # 2. AI Processing
    print("   Thinking...")
    context = registry.get_all_entities_summary()
    result = ai.process_thought(full_prompt, context)
    
    log_transaction(full_prompt, result, source)
    
    # Ensure result is dict
    if not isinstance(result, dict):
        result = {"action": "fallback", "refined_content": content}

    # 3. Extract Decisions
    action = result.get("action", "fallback")
    refined_content = result.get("refined_content", content)
    
    if refined_content is None: refined_content = content

    # STRIP COMMANDS (@ai)
    if refined_content:
        refined_content = re.sub(r'(?m)(?i)^@ai.*$', '', refined_content)
        refined_content = re.sub(r'(?i)\s+@ai\s+.*$', '', refined_content).strip()

    entity_name = result.get("entity")
    folder = result.get("folder", "Unsorted")
    summary = result.get("summary", "")

    # 4. Execution
    if action == "fallback" or action == "error":
        print(f"   AI Action: {action}. Saving to Unsorted.")
        target_file = MEMORIES_DIR / "Unsorted.md"
        append_to_file(target_file, f"\n## {timestamp} [{source}]\n{refined_content}\n")

    elif action == "ambiguous":
        decision_file = BASE_DIR / "_decisions.txt"
        append_to_file(decision_file, f"\n[AMBIGUOUS] {timestamp}\nContent: {refined_content}\n")
        print("   Ambiguous content flagged.")

    elif action in ["new", "append"]:
        final_entity_name = str(entity_name) if entity_name else "Unknown"
        final_folder = str(folder) if folder else "Unsorted"
        
        safe_entity = re.sub(r'[^\w\s-]', '', final_entity_name).strip().replace(' ', '_').lower()
        safe_folder = re.sub(r'[^\w\s-]', '', final_folder).strip().replace(' ', '_').lower()
        
        folder_path = MEMORIES_DIR / safe_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / f"{safe_entity}.md"
        
        append_to_file(file_path, f"\n## {timestamp}\n{refined_content}\n")
        
        if action == "new":
            registry.add_entity(final_entity_name, safe_folder, str(file_path.relative_to(BASE_DIR)), summary)
        else:
            registry.update_entity_timestamp(final_entity_name)
            
        print(f"   Processed: {action.upper()} -> {file_path}")

def process_buffer():
    """Checks the INBOX_BUFFER_DIR for new JSON packets."""
    # Glob all .json files
    files = sorted(glob.glob(str(INBOX_BUFFER_DIR / "*.json")))
    
    if not files:
        return

    log_file = LOGS_DIR / "ingestion.log"
    append_to_file(log_file, f"[{datetime.now()}] [DEBUG] Found {len(files)} files in buffer.")
    
    for json_file in files:
        try:
            append_to_file(log_file, f"[{datetime.now()}] [DEBUG] Processing file: {json_file}")
            print(f"Processing Buffer Item: {Path(json_file).name}")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract basic data
            text = data.get("text", "")
            media_path = data.get("media_path")
            
            # Archive Attachment to Media Folder
            final_attachment_path = None
            if media_path and os.path.exists(media_path):
                # SECURITY: Ensure media_path is within ATTACHMENTS_BUFFER_DIR
                from src.config import ATTACHMENTS_BUFFER_DIR
                media_path_abs = Path(media_path).resolve()
                buffer_dir_abs = ATTACHMENTS_BUFFER_DIR.resolve()
                
                if buffer_dir_abs in media_path_abs.parents or media_path_abs == buffer_dir_abs:
                    print(f"   Saving media to archive...")
                    final_attachment_path = _move_to_media(media_path)
                else:
                    print(f"   SECURITY WARNING: Attempted to access file outside buffer: {media_path}")
            
            # Expand Content (OCR snippet for PDF / Link Fetch)
            extra_context = _enrich_content(text, final_attachment_path)
            
            # If we have a media path, append it to the user text so the AI knows it exists
            if final_attachment_path:
                text += f"\n\n[System: Associated media stored at: {final_attachment_path}]"

            # Finalize
            _finalize_item(text, source="whatsapp", extra_context=extra_context)
            
            # Cleanup
            os.remove(json_file)
            print("   Buffer item cleared.")

        except Exception as e:
            print(f"Error processing buffer file {json_file}: {e}")
            try:
                Path(json_file).rename(Path(json_file).with_suffix(".error"))
            except: pass

def process_inbox():
    """Main ingestion logic."""
    
    # 1. Check Buffer First (Priority)
    process_buffer()

    # 2. Check Text Inbox
    content = pop_inbox()
    if content and content.strip():
        print(f"Processing Inbox Content: {content[:30]}...")
        
        # Raw Backup
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        raw_entry = f"--- {timestamp} ---\n{content}\n----------------\n"
        append_to_file(RAW_HISTORY_FILE, raw_entry)
        
        # Expand Content (Links in text)
        extra_context = _enrich_content(content, attachment_path=None)
        
        _finalize_item(content, source="desktop", extra_context=extra_context)

if __name__ == "__main__":
    process_inbox()
