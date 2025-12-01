# GossipAI - Your Personal AI Work Companion

<img width="1919" height="871" alt="image" src="https://github.com/user-attachments/assets/f1978502-b813-4f82-a0bc-383e0632e79d" />

## The Problem

There's a well-documented phenomenon in career development: people forget what they've achieved. Not because the achievements weren't significant, but because we're human. We move from project to project, sprint to sprint, and the details fade. When it's time to write a resume, prepare for a performance review, or answer "tell me about a time when..." in an interview, we draw blanks.

I experienced this firsthand during my co-op at RBC. I started documenting my daily work in ChatGPT - what I accomplished, mistakes I made, lessons learned, goals I was working toward. It became my external memory. Before heading into roundtables with senior leadership, I'd scroll through to remember key projects. When applying for full-time positions, that chat history became the foundation for my resume and interview prep.

Then the chat got too long. It stopped loading. The context window filled up. I lost access to months of documented growth.

That's when I realized the fundamental limitation: ChatGPT wasn't designed to be a long-term memory system. It's a conversational interface with a fixed context window. What I needed was something that could remember indefinitely, organize memories by topic, and retrieve relevant context on demand.

I'd been learning RAG (Retrieval-Augmented Generation) techniques for three months. Vector databases, embedding models, semantic search, memory architectures. This project became the perfect opportunity to implement everything I'd learned while solving a real problem I was experiencing.

## What It Does

GossipAI is an intelligent chatbot built to be your supportive work friend. Unlike typical AI assistants that just answer questions, GossipAI actively listens, remembers your conversations, and builds a genuine understanding of who you are over time. It's designed to help you process work stress, track your goals, and manage your calendar through natural conversation.

More importantly, it never forgets. Every conversation is processed into structured memories, organized by persistent topics, and made searchable. When you need to recall what you achieved three months ago, it's there. When you're preparing for an interview and need to remember that project where you learned a critical lesson, the system retrieves it instantly.

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

## What Makes This Different

Most AI chatbots treat every conversation as isolated. They might have some basic context window, but they don't truly remember you. GossipAI takes a fundamentally different approach inspired by how human memory works.

The episodic memory system doesn't just store what you said - it understands the narrative, emotion, and significance. The journal labeling ensures that when you talk about "networking with that director" three months from now, the system knows exactly what you're referring to and can pull up all related context.

The semantic layer goes further by distilling patterns. If you mention work-life balance struggles across multiple conversations, it extracts that as a core value or concern. This gets injected into every future conversation, making the AI genuinely personalized rather than just contextually aware.

The idle detection is subtle but crucial. Instead of processing every message individually, it waits for natural conversation breaks. This creates more coherent memory units and significantly reduces API costs. A 20-message back-and-forth becomes one well-structured episodic memory rather than 20 fragmented entries.

The calendar integration with function calling means you can literally say "schedule a meeting with Sarah tomorrow at 2pm" and it happens. No switching apps, no manual entry. The AI parses your intent, extracts the details, and executes the action.

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

**Key Design Decisions:**
- Server-side rendering disabled in favor of client-side for this use case (single-user, local deployment)
- Real-time chat updates using controlled components and state management
- Expandable journal cards with smooth animations for better information density
- Category-based color coding for goals (visual hierarchy)
- First-person language throughout ("My Journal", "My Entries") for personal feel

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
