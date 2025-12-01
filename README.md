# GossipAI — Memory-Augmented Personal Work Companion

GossipAI is a chat-to-journal system I built to solve a real problem.

During my co-op, I realized how much growth gets lost: achievements, lessons, decisions, mistakes, insights. Traditionally, we are advised to have work journals, but being a genZ I started doing it on chatgpt, just tell it what happened, boom recorded and refer when needed, but, one day that chat was so full, I could no longer add to it. GossipAI fixes that with an actual memory architecture — fast, structured, and retrieval-ready.

This is not just a “chat app.”
It's like you telling all your achievements, goals, failures to your best friend and they maintain the journal and you can use that whenever you want bullet points for a resume or reflection for the year-end meeting.

<img width="1919" height="871" alt="image" src="https://github.com/user-attachments/assets/256d7bc4-9576-4897-80c8-2e5829e9bea7" />


## TL;DR (What Actually Matters)

- We don’t store raw chats — we summarize them.
- Summaries become episodic memories (journal entries) with tags, emotion, and importance.
- Smart consolidation & pruning: new summaries are matched to existing episodes when appropriate.
- Semantic memory extracts stable facts/traits over time and is injected into the prompt.
- Dynamic retrieval + Reflect agents: personal reflection, resume bullets, or informal overview.
- MCP calendar (fully working) + fan-out orchestration for parallel scheduling.
- Built with FastAPI, Next.js, Qdrant, OpenAI embeddings/LLMs.

## Key Features

### 1. Episodic Memory — Summaries, Not Logs

After natural pauses (60s idle), the system summarizes the recent conversation into a story chunk containing:
- story  
- tags  
- emotion  
- intent  
- importance  

This becomes an episode — a single, meaningful journal entry.
<img width="1919" height="1023" alt="image" src="https://github.com/user-attachments/assets/8e96d903-d76d-45c7-ad11-09f19df89c33" />


### 2. Smart Tagging & Consolidation

Before creating a new episode, the system checks existing journal topics:

- If the new story matches an existing episode (semantic similarity, tag overlap, recency/importance rules), it is appended to that journal.
- If not, a new episode is created.

This creates topic-centric journals where a task discussed months apart still belongs to the same coherent history.
<img width="1919" height="839" alt="image" src="https://github.com/user-attachments/assets/a58db4d1-ad4a-4ae0-8094-7da5c5c18e06" />


### 3. Memory Management — Consolidation & Pruning

The system periodically:
- consolidates overlapping episodes,
- prunes low-importance duplicates,
- re-scores episode importance by recency and frequency.

The memory store stays lean and high-signal.

### 4. Semantic Memory — Who You Are

A background extractor turns recurring patterns into:
- traits  
- preferences  
- stable work facts  

These semantic memories are injected automatically into prompts for long-term personalization.
<img width="1107" height="580" alt="image" src="https://github.com/user-attachments/assets/4731242c-a4e1-4ab2-910e-8db17497a52f" />

### 5. Dynamic Retrieval + Reflect Agents

A decision agent selects the correct retrieval tool for each query:

- Personal Reflection Agent — deep emotional or narrative analysis  
- Professional Bullets Agent — resume-ready achievements  
- Informal Overview Agent — quick life or project statuses  

The app uses agent orchestration to route queries and merge outputs cleanly.

### 6. MCP Calendar + Fan-Out Pattern

Example: “Book a meeting with Sarah tomorrow at 5pm.”

Process:
- Episodic memory is saved.
- CalendarAgent creates the Google Calendar event via OAuth2.
- Logging, notifications, and follow-up tasks run in parallel (fan-out).
- Outputs are merged into a single final message.

This demonstrates real parallel tool use, not a toy example.
<img width="1148" height="441" alt="image" src="https://github.com/user-attachments/assets/f077a46c-2308-4300-aa3b-110143e51d9a" />
<img width="1500" height="637" alt="image" src="https://github.com/user-attachments/assets/0909398d-9bde-434d-994e-dc15ec7cc802" />



## Technical Architecture

### Backend (FastAPI)
The backend runs on FastAPI with full async support for handling concurrent requests efficiently. The architecture is deliberately modular to separate concerns:

**LLM Strategy:**
- GPT-4o handles the main chat interface and semantic memory extraction where reasoning quality matters
- GPT-4o-mini processes episodic memories and journal labels where speed and cost efficiency are priorities
- This hybrid approach balances performance with budget

**Vector Database:**
Qdrant stores all memories with 1536-dimensional embeddings from OpenAI's text-embedding-3-small model. The choice of Qdrant over alternatives like Pinecone or Weaviate came down to:
- Native support for payload filtering (crucial for journal label queries)
- Excellent performance on cosine similarity search
- Clean Python client with async support
- Generous free tier for development

**Memory Architecture:**
The system maintains two separate Qdrant collections:
- `episodic_memory` - Conversation summaries with journal labels, emotions, entities
- `semantic_memory` - Extracted facts, traits, patterns, relationships

This separation allows different retrieval strategies. Episodic memories are queried by similarity and filtered by journal labels. Semantic memories are retrieved for context injection based on confidence scores.

**Modular Backend Structure:**
- `chat.py` - Main FastAPI app, endpoints, function calling logic
- `episodic_memory.py` - Journal labeling, episodic memory creation, Qdrant storage
- `semantic_memory.py` - Pattern extraction, semantic memory management
- `memory_models.py` - Pydantic models ensuring type safety across the system
- `calendar_mcp.py` - Google Calendar OAuth and API wrapper following MCP patterns
- `memory_functions.py` - Compatibility layer re-exporting from specialized modules

### Frontend (Next.js + React)
The frontend is built with Next.js and React, prioritizing clean UX and responsive design. Tailwind CSS handles styling with a custom color scheme that maintains consistency across pages.

**Page Structure:**
- `dashboard.js` - Main chat interface with message history and input
- `stories.js` - Journal browser with expandable topic cards
- `reflect.js` - AI introspection with three specialized agents
- `goals.js` - Goal tracking with progress visualization
- `Sidebar.js` - Navigation component with active state management

The frontend communicates with the backend via standard fetch calls. No complex state management library needed since each page maintains its own state independently.

### Data Flow
The system processes conversations through a carefully orchestrated pipeline:

1. **Message Received**: User sends message from frontend chat interface
2. **Session Management**: Backend adds message to user's session buffer (in-memory)
3. **Context Retrieval**: System queries Qdrant for relevant semantic memories based on conversation topic
4. **Response Generation**: 
   - Semantic context injected into system prompt
   - GPT-4o processes message with full conversation history
   - If calendar-related, function calling triggers (create_event, get_events)
   - Response streamed back to frontend
5. **Idle Timer Activation**: 60-second countdown starts/resets with each message
6. **Batch Processing** (on idle timeout):
   - Entire conversation chunk summarized
   - LLM determines journal label (reuses existing labels when possible)
   - Episodic memory created with extracted emotion, entities, intent, importance
   - Memory embedded and stored in Qdrant with journal label as primary tag
7. **Semantic Extraction** (periodic, triggered by episode count):
   - Recent episodic memories analyzed for patterns
   - Stable facts extracted (traits, preferences, relationships, patterns)
   - Semantic memories stored separately with confidence scores
8. **Future Context Injection**: Semantic memories automatically retrieved and injected into system prompts for subsequent conversations

This architecture ensures conversations feel natural and responsive while maintaining rich, structured memory in the background.

### Memory Collections (Qdrant)
The system uses two distinct Qdrant collections with different purposes:

**episodic_memory Collection:**
- Stores narrative summaries of conversation chunks
- Payload includes: story, emotion, key_entities, user_intent, importance, journal_label, timestamp
- Queried by semantic similarity for Reflect page agents
- Filtered by journal_label for Stories page display
- Average size: 200-500 tokens per entry

**semantic_memory Collection:**
- Stores distilled facts about the user
- Payload includes: type (trait/preference/fact/pattern/relationship), content, confidence, source_episodes, occurrence_count
- Retrieved by confidence score for context injection
- Updated less frequently than episodic (only when patterns emerge)
- Average size: 20-50 tokens per entry

Both collections use cosine similarity on 1536-dimensional embeddings for retrieval.

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 16+
- Qdrant Cloud account (or local Qdrant instance)
- OpenAI API key
- Google Cloud project (for calendar integration)

### Backend Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd PassATS/server
```

2. Create a `.env` file in the `server` directory:
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

3. Install Python dependencies:
```bash
cd llms
pip install -r requirements.txt
```

4. (Optional) Set up Google Calendar:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download `credentials.json` and place in `server/` directory
   - See `server/llms/CALENDAR_SETUP.md` for detailed instructions

5. Start the backend server:
```bash
python chat.py
```

The server will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd my-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

### First-Time Use

1. Open `http://localhost:3000` in your browser
2. Start chatting in the main interface
3. After 60 seconds of inactivity, your conversation will be processed into memory
4. Check the Journal page to see your episodic memories
5. Use the Reflect page to get AI-generated insights
6. (If calendar configured) Say "What's on my calendar?" to trigger OAuth flow

### Environment Variables

**Backend (.env in server/)**
- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_URL` - Qdrant instance URL
- `QDRANT_API_KEY` - Qdrant API key

**Frontend**
No environment variables required. API endpoint is hardcoded to `http://localhost:8000`

### Important Notes

- The system requires active Qdrant and OpenAI services
- Calendar integration is optional - the app works without it
- First calendar use will open a browser for Google OAuth
- Add `credentials.json` and `token.pickle` to `.gitignore`
- Memory processing happens after 60 seconds of idle time
- Semantic memories are extracted periodically from episodic memories

## Project Structure

```
PassATS/
├── server/
│   ├── llms/
│   │   ├── chat.py                 # Main FastAPI application
│   │   ├── episodic_memory.py      # Episodic memory logic
│   │   ├── semantic_memory.py      # Semantic memory logic
│   │   ├── memory_models.py        # Pydantic models
│   │   ├── memory_functions.py     # Re-exports for compatibility
│   │   ├── calendar_mcp.py         # Google Calendar integration
│   │   ├── requirements.txt        # Python dependencies
│   │   └── CALENDAR_SETUP.md       # Calendar setup guide
│   ├── credentials.json            # Google OAuth credentials (gitignored)
│   ├── token.pickle                # Google OAuth token (gitignored)
│   └── .env                        # Environment variables (gitignored)
├── my-app/
│   ├── pages/
│   │   ├── dashboard.js            # Main chat interface
│   │   ├── stories.js              # Journal browser
│   │   ├── reflect.js              # AI introspection
│   │   └── goals.js                # Goal tracking
│   ├── src/
│   │   └── components/
│   │       └── Sidebar.js          # Navigation sidebar
│   └── package.json                # Node dependencies
└── README.md
```

## Future Enhancements

- Automatic goal progress tracking from conversations
- Calendar event suggestions based on conversation context
- Export journal entries as PDF or Markdown
- Multi-user support with authentication
- Mobile app version
- Voice input/output
- Integration with other productivity tools (Notion, Todoist, etc.)
- Advanced analytics on emotional patterns over time
- Conversation threading and topic clustering

## License

This project is for personal use and demonstration purposes.
