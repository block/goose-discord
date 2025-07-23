import asyncio
import json
import tempfile
import os
import logging
import shutil
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class GooseClient:
    """Client for interacting with Goose CLI"""
    
    def __init__(self):
        self.sessions = {}  # thread_id -> session_dir
        self.goose_command = os.getenv('GOOSE_COMMAND', 'goose')
        self.docs_path = os.getenv('GOOSE_DOCS_PATH', '')
    
    async def run_barebones(self, thread_id: str, prompt: str) -> Optional[str]:
        """Start a new Goose session with barebones recipe (no tool calls)"""
        try:
            # Create a temporary directory for this session
            session_dir = tempfile.mkdtemp(prefix=f"goose_session_{thread_id}_")
            self.sessions[thread_id] = session_dir
            logger.info(f"Created session directory: {session_dir}")
            
            # Run goose with barebones recipe
            result = await self._run_goose_command(session_dir, prompt, thread_id, is_initial=True, use_barebones=True)
            return result
            
        except Exception as e:
            logger.error(f"Error in run_barebones: {e}")
            return None
    
    async def run_initial(self, thread_id: str, prompt: str, use_help_recipe: bool = False) -> Optional[str]:
        """Start a new Goose session with initial prompt"""
        try:
            # Create a temporary directory for this session
            session_dir = tempfile.mkdtemp(prefix=f"goose_session_{thread_id}_")
            self.sessions[thread_id] = session_dir
            logger.info(f"Created session directory: {session_dir}")
            
            # Run goose with the initial prompt
            result = await self._run_goose_command(session_dir, prompt, thread_id, is_initial=True, use_help_recipe=use_help_recipe)
            return result
            
        except Exception as e:
            logger.error(f"Error in run_initial: {e}")
            return None
    
    async def run_with_history(self, thread_id: str, history: List[Dict]) -> Optional[str]:
        """Continue a Goose session with message history"""
        try:
            session_dir = self.sessions.get(thread_id)
            if not session_dir:
                logger.warning(f"Session not found for thread {thread_id}")
                return "🦆 Session not found. Please start a new session with `/session` or `/assistant`"
            
            # Get the latest user message
            user_messages = [msg for msg in history if msg["role"] == "user"]
            if not user_messages:
                logger.warning("No user messages found in history")
                return None
                
            latest_message = user_messages[-1]["content"]
            logger.info(f"Processing message: {latest_message[:50]}...")
            
            # Build context from conversation history
            context_prompt = self._build_context_prompt(history, latest_message)
            
            # Run goose with the context-aware prompt
            result = await self._run_goose_command(session_dir, context_prompt, thread_id, use_help_recipe=False)
            return result
            
        except Exception as e:
            logger.error(f"Error in run_with_history: {e}")
            return None
    
    async def _run_goose_command(self, session_dir: str, prompt: str, thread_id: str = None, is_initial: bool = False, use_help_recipe: bool = False, use_barebones: bool = False) -> Optional[str]:
        """Execute goose run command and return the response"""
        try:
            logger.info(f"Running goose command in {session_dir}")
            recipes = "recipes"
            
            # Build goose command arguments
            if use_help_recipe:
                # Use the recipe for help sessions with parameters
                recipe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f"{recipes}/goose_help.yaml")
                docs_path = os.getenv('GOOSE_DOCS_PATH', '/Users/dkatz/git/goose/documentation')
                docs_url = os.getenv('GOOSE_DOCS_URL', 'https://block.github.io/goose/docs/')
                source_path = os.getenv('GOOSE_SOURCE_PATH', '/Users/dkatz/git/goose')
                
                # Log the parameters being used
                logger.info(f"Help recipe parameters:")
                logger.info(f"  docs_path: {docs_path}")
                logger.info(f"  docs_url: {docs_url}")
                logger.info(f"  source_path: {source_path}")
                logger.info(f"  user_question: {prompt[:100]}...")
                
                # Let Goose manage its own session directory by not specifying cwd
                # and not using --no-session so it creates a default session
                cmd_args = [
                    self.goose_command, 'run', 
                    '--recipe', recipe_path,
                    '--params', f'docs_path={docs_path}',
                    '--params', f'docs_url={docs_url}',
                    '--params', f'source_path={source_path}',
                    '--params', f'user_question={prompt}'
                    # No --session flag, let Goose create a default session
                ]
                
                # Log the full command being executed
                logger.info(f"Executing command: {' '.join(cmd_args)}")
                
                # Run goose command without specifying cwd so it uses default session location
                process = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                    # No cwd specified - let Goose use its default session directory
                )
                
            elif use_barebones:
                # Use barebones recipe (no tool calls) with parameters
                recipe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f"{recipes}/goose_session.yaml")
                cmd_args = [
                    self.goose_command, 'run',
                    '--recipe', recipe_path,
                    '--params', f'user_prompt={prompt}',
                    '--no-session'
                ]
                
                # Run goose command
                process = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session_dir
                )
            else:
                # Regular session
                cmd_args = [self.goose_command, 'run', '--text', prompt, '--no-session']
                
                # Run goose command
                process = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session_dir
                )
            
            # Set a timeout for the process
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=300  # 5 minute timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                logger.error("Goose command timed out")
                return "🦆 *Tired honking* - That took too long, please try a simpler request!"
            
            if process.returncode == 0:
                response = stdout.decode('utf-8').strip()
                
                if use_help_recipe:
                    # Try to extract session path from stdout and get clean response
                    jsonl_response = self._extract_from_stdout_session_path(response)
                    if jsonl_response:
                        logger.info(f"Using JSONL response from session path, length: {len(jsonl_response)}")
                        return self._clean_response(jsonl_response)
                
                # Fallback to stdout parsing
                logger.info(f"Fallback to stdout response, length: {len(response)}")
                return self._clean_response(response)
            else:
                error_msg = stderr.decode('utf-8').strip()
                logger.error(f"Goose command failed with return code {process.returncode}")
                logger.error(f"Stderr: {error_msg}")
                logger.error(f"Stdout: {stdout.decode('utf-8').strip()}")
                return f"🦆 *Error honking* - Goose encountered an issue: {error_msg[:500]}..."
                
        except FileNotFoundError:
            logger.error(f"Goose command not found: {self.goose_command}")
            return "🦆 *Confused honking* - I can't find the Goose command! Make sure Goose is installed and accessible."
        except Exception as e:
            logger.error(f"Error running goose command: {e}")
            return f"🦆 *Panicked honking* - Something went wrong: {str(e)[:100]}..."
    
    def _build_context_prompt(self, history: List[Dict], latest_message: str) -> str:
        """Build a context-aware prompt from conversation history"""
        # Get the last few messages for context (limit to avoid token limits)
        recent_history = history[-6:]  # Last 6 messages (3 exchanges)
        
        context_parts = ["Here's our conversation so far:\n"]
        
        for msg in recent_history[:-1]:  # Exclude the latest message
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:200]  # Truncate long messages
            context_parts.append(f"{role}: {content}")
        
        context_parts.extend([
            "\nNow please respond to this new message:",
            f"User: {latest_message}"
        ])
        
        return "\n".join(context_parts)
    
    def _extract_final_response_from_jsonl(self, session_dir: str) -> Optional[str]:
        """Extract the final assistant response from the session JSONL file"""
        try:
            # Debug: List all files in the session directory
            logger.info(f"Checking session directory: {session_dir}")
            all_files = []
            for root, dirs, files in os.walk(session_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    all_files.append(full_path)
                    logger.info(f"Found file: {full_path}")
            
            # Look for JSONL files
            jsonl_files = [f for f in all_files if f.endswith('.jsonl')]
            
            if not jsonl_files:
                logger.warning(f"No JSONL files found in session directory. All files: {all_files}")
                return None
            
            # Use the most recent JSONL file
            jsonl_file = max(jsonl_files, key=os.path.getmtime)
            logger.info(f"Reading session data from: {jsonl_file}")
            
            # Read the JSONL file and find the last assistant message
            last_assistant_message = None
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('role') == 'assistant' and entry.get('content'):
                            last_assistant_message = entry['content']
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSONL line: {e}")
                        continue
            
            if last_assistant_message:
                logger.info(f"Found final assistant response, length: {len(last_assistant_message)}")
                return last_assistant_message
            else:
                logger.warning("No assistant messages found in JSONL file")
                return None
                
        except Exception as e:
            logger.error(f"Error reading JSONL file: {e}")
            return None

    async def _extract_from_goose_session(self, session_name: str) -> Optional[str]:
        """Extract the final assistant response from Goose's default session location"""
        try:
            import os.path
            
            # Try common Goose session locations
            possible_session_dirs = [
                os.path.expanduser(f"~/.config/goose/sessions/{session_name}"),
                os.path.expanduser(f"~/.goose/sessions/{session_name}"),
                os.path.expanduser(f"~/Library/Application Support/goose/sessions/{session_name}"),  # macOS
            ]
            
            for session_dir in possible_session_dirs:
                logger.info(f"Checking Goose session directory: {session_dir}")
                if os.path.exists(session_dir):
                    logger.info(f"Found session directory: {session_dir}")
                    # List files in the session directory
                    try:
                        files = os.listdir(session_dir)
                        logger.info(f"Files in session directory: {files}")
                        
                        # Look for JSONL files
                        jsonl_files = [f for f in files if f.endswith('.jsonl')]
                        if jsonl_files:
                            jsonl_file = os.path.join(session_dir, jsonl_files[0])
                            logger.info(f"Reading session data from: {jsonl_file}")
                            
                            # Read the JSONL file and find the last assistant message
                            last_assistant_message = None
                            with open(jsonl_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    try:
                                        entry = json.loads(line.strip())
                                        if entry.get('role') == 'assistant' and entry.get('content'):
                                            last_assistant_message = entry['content']
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"Failed to parse JSONL line: {e}")
                                        continue
                            
                            if last_assistant_message:
                                logger.info(f"Found final assistant response, length: {len(last_assistant_message)}")
                                return last_assistant_message
                    except Exception as e:
                        logger.warning(f"Error reading session directory {session_dir}: {e}")
                        continue
            
            logger.warning(f"No Goose session found for: {session_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting from Goose session: {e}")
            return None

    async def _extract_from_latest_goose_session(self) -> Optional[str]:
        """Extract the final assistant response from the most recent Goose session"""
        try:
            import os.path
            import glob
            
            # Try common Goose session locations
            possible_session_base_dirs = [
                os.path.expanduser("~/.config/goose/sessions/"),
                os.path.expanduser("~/.goose/sessions/"),
                os.path.expanduser("~/Library/Application Support/goose/sessions/"),  # macOS
            ]
            
            latest_session_dir = None
            latest_time = 0
            
            for base_dir in possible_session_base_dirs:
                logger.info(f"Checking Goose sessions base directory: {base_dir}")
                if os.path.exists(base_dir):
                    # Find all session directories
                    session_dirs = [d for d in os.listdir(base_dir) 
                                  if os.path.isdir(os.path.join(base_dir, d))]
                    logger.info(f"Found session directories: {session_dirs}")
                    
                    for session_name in session_dirs:
                        session_dir = os.path.join(base_dir, session_name)
                        try:
                            # Get the modification time of the session directory
                            mtime = os.path.getmtime(session_dir)
                            if mtime > latest_time:
                                latest_time = mtime
                                latest_session_dir = session_dir
                        except Exception as e:
                            logger.warning(f"Error checking session {session_dir}: {e}")
                            continue
            
            if not latest_session_dir:
                logger.warning("No Goose sessions found")
                return None
                
            logger.info(f"Using latest session directory: {latest_session_dir}")
            
            # Look for JSONL files in the latest session
            try:
                files = os.listdir(latest_session_dir)
                logger.info(f"Files in latest session directory: {files}")
                
                # Look for JSONL files
                jsonl_files = [f for f in files if f.endswith('.jsonl')]
                if jsonl_files:
                    jsonl_file = os.path.join(latest_session_dir, jsonl_files[0])
                    logger.info(f"Reading session data from: {jsonl_file}")
                    
                    # Read the JSONL file and find the last assistant message
                    last_assistant_message = None
                    with open(jsonl_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('role') == 'assistant' and entry.get('content'):
                                    last_assistant_message = entry['content']
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse JSONL line: {e}")
                                continue
                    
                    if last_assistant_message:
                        logger.info(f"Found final assistant response, length: {len(last_assistant_message)}")
                        return last_assistant_message
                    else:
                        logger.warning("No assistant messages found in JSONL file")
                        return None
                else:
                    logger.warning(f"No JSONL files found in session directory: {latest_session_dir}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error reading session directory {latest_session_dir}: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Error extracting from latest Goose session: {e}")
            return None

    def _extract_from_stdout_session_path(self, stdout_response: str) -> Optional[str]:
        """Extract the final assistant response by parsing the session path from stdout"""
        try:
            # Look for the logging path in stdout
            # Pattern: "logging to /path/to/session.jsonl"
            import re
            
            logger.info("Searching for session path in stdout...")
            
            # Regex to find the logging path
            session_path_pattern = r'logging to ([^\s]+\.jsonl)'
            match = re.search(session_path_pattern, stdout_response)
            
            if not match:
                logger.warning("No session path found in stdout")
                return None
            
            jsonl_path = match.group(1)
            logger.info(f"Found session JSONL path: {jsonl_path}")
            
            # Check if the file exists
            if not os.path.exists(jsonl_path):
                logger.warning(f"Session JSONL file does not exist: {jsonl_path}")
                return None
            
            # Read the JSONL file and find the last assistant message
            last_assistant_message = None
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('role') == 'assistant' and entry.get('content'):
                            content = entry['content']
                            
                            # Handle different content types
                            if isinstance(content, str):
                                last_assistant_message = content
                            elif isinstance(content, list):
                                # If content is a list, join the text parts
                                text_parts = []
                                for item in content:
                                    if isinstance(item, str):
                                        text_parts.append(item)
                                    elif isinstance(item, dict) and item.get('type') == 'text':
                                        text_parts.append(item.get('text', ''))
                                last_assistant_message = ''.join(text_parts)
                            elif isinstance(content, dict):
                                # If content is a dict, try to get text field
                                last_assistant_message = content.get('text', str(content))
                            else:
                                # Fallback: convert to string
                                last_assistant_message = str(content)
                                
                            logger.debug(f"Processed assistant message, type: {type(content)}, length: {len(last_assistant_message)}")
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSONL line: {e}")
                        continue
            
            if last_assistant_message:
                logger.info(f"Found final assistant response from session, length: {len(last_assistant_message)}")
                return last_assistant_message
            else:
                logger.warning("No assistant messages found in session JSONL file")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting from stdout session path: {e}")
            return None

    def _clean_response(self, response: str) -> str:
        if not response:
            return "🦆 *Silent honking* - Goose didn't have anything to say."
        
        # Remove ANSI color codes
        result = re.sub(r'\x1b\[[0-9;]*m', '', response)
        
        # Basic cleanup - just trim whitespace
        result = result.strip()
        
        # If still empty, provide a default response
        if not result:
            result = "🦆 *Thoughtful honking* - I processed your request, but don't have a specific response."
        
        return result
    
    def cleanup_session(self, thread_id: str):
        """Clean up a session directory"""
        session_dir = self.sessions.get(thread_id)
        if session_dir and os.path.exists(session_dir):
            try:
                shutil.rmtree(session_dir)
                logger.info(f"Cleaned up session directory: {session_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up session directory: {e}")
            finally:
                self.sessions.pop(thread_id, None)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session thread IDs"""
        return list(self.sessions.keys())
