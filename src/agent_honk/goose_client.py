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
                return "🦆 Session not found. Please start a new session with `/honk` or `/assistant`"
            
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
    
    async def _run_goose_command(self, session_dir: str, prompt: str, thread_id: str = None, is_initial: bool = False, use_help_recipe: bool = False) -> Optional[str]:
        """Execute goose run command and return the response"""
        try:
            logger.info(f"Running goose command in {session_dir}")
            
            # Build goose command arguments
            if use_help_recipe:
                # Use the recipe for help sessions with parameters
                recipe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'goose_help.yaml')
                docs_path = os.getenv('GOOSE_DOCS_PATH', 'https://block.github.io/goose/docs')
                cmd_args = [
                    self.goose_command, 'run', 
                    '--recipe', recipe_path,
                    '--params', f'docs_path={docs_path}',
                    '--params', f'user_question={prompt}',
                    '--no-session'
                ]
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
                logger.info(f"Goose command successful, response length: {len(response)}")
                # Clean up the response (remove command echoes, etc.)
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
    
    def _clean_response(self, response: str) -> str:
        """Clean up the goose response for Discord"""
        if not response:
            return "🦆 *Silent honking* - Goose didn't have anything to say."
            
        # Remove any command prompts or system messages
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines at the start
            if not cleaned_lines and not line.strip():
                continue
            # Skip command echo lines
            if line.startswith('goose run') or line.startswith('$ goose'):
                continue
            # Skip Goose startup messages
            if 'running without session' in line or 'starting session' in line:
                continue
            if 'provider:' in line and 'model:' in line:
                continue
            if 'working directory:' in line or 'logging to' in line:
                continue
            # Skip tool call traces
            if line.startswith('─── ') and ('|' in line):
                continue
            if line.startswith('extension_name:') or line.startswith('k:') or line.startswith('query:'):
                continue
            if line.startswith('save_as:') or line.startswith('url:') or line.startswith('command:'):
                continue
            if line.startswith('path:') and not line.startswith('path to'):
                continue
            # Skip common CLI artifacts
            if line.strip() in ['', '---', '===']:
                continue
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        
        # Remove ANSI color codes
        result = re.sub(r'\x1b\[[0-9;]*m', '', result)
        
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
