# Goose Assistant Enhancement - Knowledge-Based Documentation Helper

This enhancement adds a session-based Goose assistant that helps users get the most out of Goose AI with comprehensive documentation links and knowledge-based responses.

## Changes Made

### 1. Enhanced Help Recipe System
- Updated `_create_help_prompt()` in `GooseClient` to reference documentation
- Includes comprehensive documentation links for all major Goose topics
- **Explicitly instructs assistant to NOT use any tools** - knowledge-based responses only
- **Biased towards shorter, more focused responses with prominent links**
- Provides structured guidance with direct links to relevant docs

### 2. Documentation Link Mapping
- Maps GitHub documentation structure to live web URLs
- References https://block.github.io/goose/docs/ for current information
- Provides users with clickable links to relevant documentation sections
- Uses knowledge-based responses instead of live web scraping for safety

### 3. Discord Message Handling Improvements
- **Added message splitting functionality** to handle Discord's 2000 character limit
- Messages are intelligently split by lines, then words, then characters if needed
- Continuation messages are clearly marked with "*(continued...)*"
- **Added initial context messages** showing who asked what question

### 4. User Experience Enhancements
- **Immediate feedback**: Shows "@username asked: question" when thread is created
- **Faster perceived response**: Thread creation happens immediately, Goose processing follows
- **Better message handling**: Long responses are properly split across multiple messages
- **Cleaner interface**: No more truncated messages or lost information

### 5. Comprehensive Documentation Links
The help recipe now includes direct links to:

**Goose Basics:**
- https://block.github.io/goose/docs/quickstart
- https://block.github.io/goose/docs/category/getting-started

**Extensions:**
- https://block.github.io/goose/docs/guides/managing-tools/
- https://block.github.io/goose/extensions

**Best Practices:**
- https://block.github.io/goose/docs/guides/tips
- https://block.github.io/goose/docs/guides/creating-plans

**Troubleshooting:**
- https://block.github.io/goose/docs/troubleshooting
- https://block.github.io/goose/docs/guides/handling-llm-rate-limits-with-goose

**Advanced Usage:**
- https://block.github.io/goose/docs/guides/managing-goose-sessions
- https://block.github.io/goose/docs/guides/recipes/

**Configuration & Setup:**
- https://block.github.io/goose/docs/guides/config-file
- https://block.github.io/goose/docs/guides/environment-variables

### 6. Tool Call Output Filtering
- **Added comprehensive filtering** in `_clean_response()` to remove tool call traces
- Filters out lines starting with `─── ` (tool call headers)
- Removes parameter lines like `extension_name:`, `k:`, `query:`, `save_as:`, `url:`, etc.
- **Clean output**: Users only see the final response, not the technical implementation

### 7. Simple `/assistant` Command
- Just `/assistant <your question>` - no complex sub-arguments
- Creates a threaded session exactly like `/honk`
- Users can continue conversing naturally in the thread
- Assistant provides knowledge-based responses with documentation links

## Usage

### For Regular Goose Sessions:
- `/honk <prompt>` - Normal Goose AI session

### For Goose Help Sessions:
- `/assistant <question>` - Specialized help session with documentation links

## Example Usage:
- `/assistant How do I install Goose?`
- `/assistant What extensions are available?`
- `/assistant Best practices for writing prompts`
- `/assistant How to troubleshoot connection issues`

## Benefits

1. **Knowledge-Based**: Fast responses based on assistant's knowledge of Goose
2. **Clickable Links**: Users get direct links to relevant documentation sections
3. **Session-Based**: Continue conversations naturally in threads
4. **Safe & Fast**: No tool calls means faster responses and cleaner output
5. **Comprehensive Coverage**: Covers all major Goose topics with proper links
6. **Always Available**: No dependency on external tools or web scraping
7. **Better UX**: Immediate feedback with proper Discord user mentions
8. **No Message Truncation**: Intelligent message splitting handles Discord's 2000 char limit
9. **Concise Responses**: Assistant biased towards shorter, more focused answers with prominent links
10. **Clean Output**: No tool call traces or technical implementation details

## Assistant Capabilities

The assistant provides:
- **Knowledge-Based Responses**: Fast answers based on comprehensive Goose knowledge
- **Comprehensive Link Database**: Pre-loaded with all major documentation links  
- **Session Management**: Same thread-based system as regular Goose
- **Clean Output**: No tool call traces or technical implementation details

## Security & Performance
- Uses the same session management as regular Goose
- Knowledge-based responses are faster than web scraping
- No external dependencies or tool calls for safety
- Clean, focused output without technical traces

The assistant sessions work exactly like regular Goose sessions but with specialized focus on helping users learn Goose effectively, providing immediate answers with comprehensive documentation links!
