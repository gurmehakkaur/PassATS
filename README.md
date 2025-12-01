# GossipAI - Your Personal AI Work Companion

<img width="1919" height="871" alt="image" src="https://github.com/user-attachments/assets/f1978502-b813-4f82-a0bc-383e0632e79d" />

GossipAI is an intelligent chatbot built to be your supportive work friend. Unlike typical AI assistants that just answer questions, GossipAI actively listens, remembers your conversations, and builds a genuine understanding of who you are over time. It's designed to help you process work stress, track your goals, and manage your calendar through natural conversation.

## Core Features

### 1. Conversational AI Chat
The main interface is a real-time chat where you can talk about anything on your mind. The AI maintains a warm, empathetic tone and actively encourages you to share more. It's built on GPT-4o and designed to feel like talking to a supportive colleague rather than a robotic assistant. 

**Screenshot needed: Main chat interface showing conversation**

### 2. Two-Tier Memory Architecture

#### Episodic Memory (Journal System)
Every conversation you have is automatically processed into structured episodic memories. These aren't just raw transcripts - the system uses an LLM to extract:
- A narrative summary from your perspective
- The primary emotion you were feeling
- Key entities (people, projects, things mentioned)
- Your intent in the conversation
- An importance score

The unique aspect is the journal labeling system. Each memory is assigned to a persistent topic label like "Gifts to Colleagues" or "Networking with Director". If you mention the same topic weeks or months later, it gets grouped under the same label. This creates a personal journal organized by themes rather than chronology.

**Screenshot needed: Journal/Stories page showing expandable journal cards**

#### Semantic Memory (Long-term Facts)
The system periodically analyzes your episodic memories to extract stable, general facts about you:
- Personality traits
- Preferences and values
- Stable facts (job, relationships, etc.)
- Behavioral patterns
- Important relationships

These semantic memories are automatically injected into the system prompt for every conversation, allowing the AI to personalize its responses based on what it knows about you.

### 3. Idle Detection & Batch Processing
The system doesn't process every single message immediately. Instead, it uses a 60-second idle timer. When you stop chatting, it waits to see if you're done with that conversation thread. Once you've been idle for a minute, it:
1. Summarizes the entire conversation chunk
2. Creates an episodic memory with a journal label
3. Periodically extracts semantic memories from recent episodes
4. Stores everything in a Qdrant vector database

This approach reduces API calls and creates more coherent memory units rather than fragmenting every message.

### 4. Journal Page
The Stories/Journal page displays all your episodic memories organized by journal labels. Each label appears as an expandable card showing:
- The journal topic (e.g., "Career Growth Discussions")
- Total number of entries under that topic
- All conversation summaries related to that topic
- Timestamps and emotional context

All entries are expanded by default for easy browsing. The language is first-person ("My Journal", "My Entries") to emphasize that this is your personal space.

**Screenshot needed: Expanded journal card showing multiple entries**

### 5. Reflect Page - AI-Powered Introspection
This page lets you query your entire conversation history using specialized AI agents:

- **Personal Reflection Agent**: Provides deep, thoughtful analysis of your experiences and emotional patterns
- **Informal Overview Agent**: Gives you a casual, friendly summary of what's been going on
- **Resume Bullet Points Agent**: Extracts professional achievements and formats them as resume-ready bullet points

Each agent searches through your episodic memories and generates insights based on your actual conversations. It's like having a therapist, friend, and career coach all analyzing your journal.

**Screenshot needed: Reflect page with agent selection and generated insights**

### 6. Goals Tracking
A dedicated page for setting and tracking personal goals. Currently supports:
- Adding goals with titles and descriptions
- Categorizing goals (Career, Health, Personal, Financial, Learning)
- Visual progress bars (hardcoded for now, will be conversation-driven later)
- Category-specific color coding and icons

The plan is to have the AI automatically update goal progress based on your conversations, but for now it provides a structured way to define what you're working toward.

**Screenshot needed: Goals page with multiple goal cards**

### 7. Google Calendar Integration (MCP)
The system integrates with Google Calendar using the Model Context Protocol. The AI has function calling capabilities to:
- View your upcoming calendar events
- Create new events from natural language ("Schedule a meeting with Sarah tomorrow at 2pm")
- Parse flexible time formats (ISO timestamps or natural language)
- Set event durations and descriptions

The integration uses OAuth 2.0 for secure authentication. After the first-time browser-based login, a token is stored locally for seamless future access.

### 8. Vector Search
All episodic and semantic memories are stored in Qdrant with embeddings generated by OpenAI's text-embedding-3-small model. This enables:
- Semantic search across your conversation history
- Retrieval of relevant memories for context injection
- Similarity-based grouping of related conversations

## Technical Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **LLMs**: 
  - GPT-4o for main chat and semantic extraction
  - GPT-4o-mini for episodic memory creation and journal labeling
- **Vector Database**: Qdrant (cloud-hosted)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Memory Models**: Pydantic models for type safety
- **Calendar**: Google Calendar API with MCP pattern

The backend is modular with separate files for:
- `chat.py` - Main FastAPI app and endpoints
- `episodic_memory.py` - Episodic memory creation and storage
- `semantic_memory.py` - Semantic memory extraction and retrieval
- `memory_models.py` - Pydantic data models
- `calendar_mcp.py` - Google Calendar integration

### Frontend (Next.js + React)
- **Framework**: Next.js with React
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with modern design
- **State Management**: React hooks (useState, useEffect)
- **API Communication**: Fetch API for backend calls

Pages:
- `dashboard.js` - Main chat interface
- `stories.js` - Journal/episodic memory browser
- `reflect.js` - AI introspection agents
- `goals.js` - Goal tracking interface

### Data Flow
1. User sends message via frontend
2. Backend receives message, adds to session buffer
3. Semantic context retrieved from Qdrant
4. GPT-4o generates response (with calendar function calling if needed)
5. Idle timer starts (60 seconds)
6. On idle timeout:
   - Conversation summarized
   - Journal label determined (checking existing labels first)
   - Episodic memory created and stored in Qdrant
   - Periodically, semantic memories extracted from recent episodes
7. Semantic memories injected into future conversations

### Memory Collections (Qdrant)
- **episodic_memory**: Stores conversation summaries with journal labels
- **semantic_memory**: Stores extracted facts, traits, patterns

Both use cosine similarity for vector search.

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
