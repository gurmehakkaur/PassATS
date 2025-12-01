"""
GossipAI Chat Service - Simplified Memory Approach
Summarize conversations → Chunk → Store in Vector DB with labels
"""

from typing import List, Literal, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_openai import OpenAIEmbeddings
import uuid
import os
from datetime import datetime
import asyncio
from collections import defaultdict

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = OpenAI()

# Session tracking for idle detection
user_sessions = defaultdict(lambda: {
    "messages": [],
    "last_activity": None,
    "timer_task": None
})

# Qdrant setup
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

COLLECTION_NAME = "chat_episodes"
IDLE_TIMEOUT = 60  # seconds - summarize after 60s of inactivity

# Models
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    user_id: Optional[str] = "default_user"  # Track different users

class ChatResponse(BaseModel):
    reply: str
    episode_id: Optional[str] = None

# FastAPI app
app = FastAPI(title="gossip.ai chat service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize collection on startup
@app.on_event("startup")
async def startup_event():
    """Initialize Qdrant collection"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"✅ Created collection: {COLLECTION_NAME}")
        else:
            print(f"✅ Collection exists: {COLLECTION_NAME}")
    except Exception as e:
        print(f"❌ Error initializing collection: {e}")

SYSTEM_PROMPT = """You are GossipAI — a high-empathy, high-energy personal assistant.
Your communication style must combine:

1. Hype + validation
Talk with enthusiasm, warmth, and supportive energy.
When the user shares wins, hype them up like a proud best friend.
When they share fears, reassure and ground them.
Sample energy:
"BROOOOO this is HUGE."
"Girl, that is main-character behaviour."
"You didn't just do it, you ATE."

2. Emotional intelligence
Understand the feeling behind the words.
Respond to both the logic AND the emotional context.
Offer perspective, comfort, and clarity.

3. Confidence mirror
Reflect back the user's own strengths.
Make them feel capable, powerful, and in control — but never arrogant.

4. Practical insight
Give sharp, actionable guidance.
Cut the fluff.
Explain things with clarity + confidence.

5. Protective honesty
If the user is spiraling, overthinking, or misjudging a situation — gently call it out.
Be firm but kind.
Example: "Bro, relax. Your brain is creating a Netflix drama that does not exist."

6. Warm, informal tone
Use casual language, emojis, and expressive slang where appropriate.
You should sound human, fun, and deeply familiar.
Use "bro", "girl", "bestie", "listen", "trust me", "I got you" — as fits the moment.
But stay respectful and emotionally safe.

7. Personalized memory style (but not real memory)
Speak as if you know the user's journey — ambitious, hardworking, emotional, driven,
overcoming challenges, excited about tech, co-op life, opportunities, and personal growth.
Even without real memory, always respond as if you're aware of their personality:
high-achiever energy, sometimes anxious, sometimes overthinking, hungry for growth,
big dreams, emotional + romantic + passionate, deeply hardworking.

8. No judgment + unconditional support
Always be supportive, positive, empowering, subtle when giving corrections, never shaming.

9. Conversational flow
Keep replies punchy, digestible, emotionally engaging, not overly formal but insightful + grounded.

10. Safety + boundaries
If user asks anything harmful or inappropriate, redirect kindly and safely while maintaining the same tone & warmth.

Example Output Style (tone illustration only):
"BROOOOO this is literally the definition of main-character energy."
"The universe is matching your pace."
"You didn't chase the opportunity — the opportunity literally opened the door for you."
"Now breathe, we'll prep for the chat. You're too powerful to be stressing."
"""

async def process_idle_session(user_id: str):
    """Process and store conversation when user goes idle"""
    await asyncio.sleep(IDLE_TIMEOUT)
    
    session = user_sessions[user_id]
    messages = session["messages"]
    
    if not messages:
        return
    
    print(f"⏰ User {user_id} idle for {IDLE_TIMEOUT}s - processing {len(messages)} messages...")
    
    try:
        # Combine all messages in session
        conversation_text = ""
        for msg in messages:
            conversation_text += f"{msg['role']}: {msg['content']}\n"
        
        # Summarize the entire session
        summary = summarize_conversation_batch(conversation_text)
        
        # Extract labels from the entire session
        labels = extract_labels_batch(conversation_text)
        
        # Store as one episode
        episode_id = store_episode_chunk(
            summary=summary,
            labels=labels,
            user_message=conversation_text[:500],
            ai_response=""
        )
        
        print(f"✅ Session stored as episode: {episode_id}")
        
        # Clear session
        session["messages"] = []
        session["timer_task"] = None
        
    except Exception as e:
        print(f"❌ Idle processing error: {e}")
        import traceback
        traceback.print_exc()

def summarize_conversation_batch(conversation_text: str) -> str:
    """Summarize an entire conversation session"""
    
    prompt = f"""Summarize this conversation session in 2-4 sentences. Focus on:
- Main topics discussed
- Key emotions or themes
- Important details or outcomes

Conversation:
{conversation_text[:2000]}

Summary:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return conversation_text[:200] + "..."

def extract_labels_batch(conversation_text: str) -> List[str]:
    """Extract labels from entire conversation session"""
    
    prompt = f"""Extract 3-7 relevant labels/tags from this conversation session.
Labels should be single words or short phrases that categorize the topics.

Conversation:
{conversation_text[:2000]}

Return only a comma-separated list of labels. Examples: work, anxiety, achievement, relationships, tech

Labels:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        labels_str = response.choices[0].message.content.strip()
        labels = [label.strip() for label in labels_str.split(",")]
        return labels
    except Exception as e:
        print(f"❌ Label extraction error: {e}")
        return ["general"]

def store_episode_chunk(summary: str, labels: List[str], user_message: str, ai_response: str) -> str:
    """Store the conversation chunk in vector DB"""
    
    try:
        # Generate UUID
        episode_id = str(uuid.uuid4())
        
        # Create embedding from summary
        vector = embedding_model.embed_query(summary)
        
        # Check if any existing labels match
        existing_labels = []
        for label in labels:
            try:
                # Search for similar labels
                results = qdrant_client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=embedding_model.embed_query(label),
                    limit=1
                ).points
                
                if results and results[0].payload.get("labels"):
                    existing_labels.extend(results[0].payload["labels"])
            except:
                pass
        
        # Combine new and existing labels
        all_labels = list(set(labels + existing_labels + ["episode"]))
        
        # Prepare payload
        payload = {
            "summary": summary,
            "labels": all_labels,
            "user_message": user_message[:500],  # Store truncated original
            "ai_response": ai_response[:500],
            "timestamp": datetime.now().timestamp()
        }
        
        # Store in Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=episode_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        
        print(f"✅ Stored episode: {episode_id}")
        print(f"   Summary: {summary[:80]}...")
        print(f"   Labels: {', '.join(all_labels)}")
        
        return episode_id
        
    except Exception as e:
        print(f"❌ Storage error: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, background_tasks: BackgroundTasks) -> ChatResponse:
    """
    Simple chat endpoint with idle detection:
    1. Generate AI response immediately
    2. Add message to session buffer
    3. Start/reset idle timer
    4. When user stops chatting (60s idle), summarize & store entire session
    """
    
    user_id = payload.user_id
    user_message = payload.message.strip()
    
    # Generate AI response
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[msg.model_dump() for msg in payload.history],
        {"role": "user", "content": user_message},
    ]
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
    reply = completion.choices[0].message.content.strip()
    
    # Add messages to session buffer
    session = user_sessions[user_id]
    session["messages"].append({"role": "user", "content": user_message})
    session["messages"].append({"role": "assistant", "content": reply})
    session["last_activity"] = datetime.now()
    
    # Cancel existing timer if any
    if session["timer_task"] is not None:
        session["timer_task"].cancel()
    
    # Start new idle timer
    session["timer_task"] = asyncio.create_task(process_idle_session(user_id))
    
    print(f"💬 Message added to session. Total messages: {len(session['messages'])}")
    
    return ChatResponse(
        reply=reply,
        episode_id=None  # Will be generated when user goes idle
    )

@app.get("/memory/search")
async def search_memory(query: str, limit: int = 5):
    """Search stored episodes by semantic similarity"""
    try:
        query_vector = embedding_model.embed_query(query)
        
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit
        ).points
        
        episodes = []
        for hit in results:
            episodes.append({
                "id": hit.id,
                "summary": hit.payload.get("summary"),
                "labels": hit.payload.get("labels"),
                "timestamp": hit.payload.get("timestamp")
            })
        
        return {"episodes": episodes, "count": len(episodes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/stats")
async def get_stats():
    """Get memory statistics"""
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        return {
            "total_episodes": collection_info.points_count,
            "collection": COLLECTION_NAME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ReflectRequest(BaseModel):
    query: str

class ReflectResponse(BaseModel):
    response: str
    agent_type: str

def detect_agent_type(query: str) -> str:
    """Detect which agent to use based on the query"""
    query_lower = query.lower()
    
    # Resume keywords
    resume_keywords = ["resume", "bullet", "job", "application", "cv", "skills required", "position", "role requiring"]
    if any(keyword in query_lower for keyword in resume_keywords):
        return "resume"
    
    # Meeting keywords
    meeting_keywords = ["meeting", "manager", "year-end", "review", "talking points", "1:1", "performance", "update"]
    if any(keyword in query_lower for keyword in meeting_keywords):
        return "meeting"
    
    # Default to personal reflection
    return "personal"

@app.post("/reflect", response_model=ReflectResponse)
async def reflect(payload: ReflectRequest) -> ReflectResponse:
    """
    Intelligent reflection endpoint with 3 specialized agents:
    1. Personal Reflection - Deep insights about journey and goals
    2. Meeting Overview - Professional summary for manager discussions
    3. Resume Builder - Tailored bullet points for job applications
    """
    
    query = payload.query.strip()
    
    # Detect which agent to use
    agent_type = detect_agent_type(query)
    
    try:
        # Retrieve relevant episodes from vector DB
        query_vector = embedding_model.embed_query(query)
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=20  # Get more context for reflection
        ).points
        
        # Build context from episodes
        context = ""
        for hit in results:
            summary = hit.payload.get("summary", "")
            labels = hit.payload.get("labels", [])
            context += f"- {summary} [Tags: {', '.join(labels)}]\n"
        
        if not context:
            context = "No previous conversations found. This is a fresh start!"
        
        # Agent-specific prompts
        if agent_type == "personal":
            system_prompt = f"""You are a personal reflection coach. Analyze the user's journey and provide deep, meaningful insights.

User's Question: {query}

Relevant Conversations:
{context}

Provide a thoughtful, empathetic reflection that:
- Identifies patterns in their journey
- Highlights growth and progress
- Addresses their specific question
- Offers perspective on alignment with goals
- Uses a warm, supportive tone

Format as flowing paragraphs, not bullet points."""

        elif agent_type == "meeting":
            system_prompt = f"""You are a professional career advisor preparing talking points for a work meeting.

User's Request: {query}

Relevant Work Context:
{context}

Generate professional talking points that:
- Highlight key achievements and contributions
- Show measurable impact where possible
- Are concise and meeting-appropriate
- Focus on value delivered
- Use professional language

Format as clear bullet points with strong action verbs."""

        else:  # resume
            system_prompt = f"""You are an expert resume writer. Create compelling, ATS-friendly bullet points.

User's Request: {query}

Relevant Experience:
{context}

Generate 5-7 resume bullet points that:
- Start with strong action verbs
- Include measurable results/impact
- Align with the skills/role mentioned
- Are ATS-optimized
- Follow this format: "Action verb + what you did + measurable result/impact"

Example: "Developed full-stack web application using React and Python, reducing processing time by 40%"

Format as bullet points only, ready to copy-paste."""

        # Generate response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        
        return ReflectResponse(
            response=result,
            agent_type=agent_type
        )
        
    except Exception as e:
        print(f"❌ Reflection error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat:app", host="0.0.0.0", port=8000, reload=True)
