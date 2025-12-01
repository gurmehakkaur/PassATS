import { useEffect, useState, useRef } from "react";
import Sidebar from "@/components/Sidebar";

export default function Dashboard() {
  const [greeting, setGreeting] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);
  const isInitialLoad = useRef(true);

  const CHAT_API_URL = "http://localhost:8000/chat";
  const CACHE_KEY = "gossip_chat_messages";

  const INITIAL_AI_MESSAGE = {
    sender: "ai",
    text: "Hey little hardworking fellow! How did your day go? I am so excited to hear!!",
    timestamp: Date.now()
  };

  // Load messages from localStorage on mount
  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = window.localStorage.getItem(CACHE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      setMessages(parsed);
    } else {
      setMessages([INITIAL_AI_MESSAGE]);
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (isInitialLoad.current) {
      isInitialLoad.current = false;
      return;
    }
    window.localStorage.setItem(CACHE_KEY, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning");
    else if (hour < 17) setGreeting("Good Afternoon");
    else setGreeting("Good Evening");
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const toHistory = (msgs) =>
    msgs.map((msg) => ({
      role: msg.sender === "ai" ? "assistant" : "user",
      content: msg.text,
    }));

  const clearChat = () => {
    setMessages([INITIAL_AI_MESSAGE]);
    window.localStorage.removeItem(CACHE_KEY);
    setError(null);
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    const userMessage = { sender: "user", text: userText, timestamp: Date.now() };
    
    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          history: toHistory(messages),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to reach gossip.ai");
      }

      const data = await response.json();
      const aiMessage = { 
        sender: "ai", 
        text: data.reply, 
        timestamp: Date.now(),
        episode_id: data.episode_id,
        memory_used: data.memory_used
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#0a0a0a" }}>
      <Sidebar />

      <main style={{ 
        flex: 1, 
        padding: "2rem 3rem",
        marginLeft: "280px",
        overflowY: "auto",
        display: "flex",
        flexDirection: "column"
      }}>
          {/* Breadcrumb */}
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "0.5rem",
            marginBottom: "2rem",
            color: "#666",
            fontSize: "0.9rem"
          }}>
            <span>Dashboard</span>
            <span>›</span>
            <span style={{ color: "white" }}>Chat</span>
          </div>

          {/* Header */}
          <div style={{ 
            display: "flex", 
            justifyContent: "space-between", 
            alignItems: "flex-start",
            marginBottom: "2rem" 
          }}>
            <div>
              <h1 style={{ 
                fontSize: "2.5rem", 
                fontWeight: "700",
                marginBottom: "0.5rem",
                color: "white"
              }}>
                {greeting}, <span style={{ 
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent"
                }}>Gurmehak</span>
              </h1>
              <p style={{ color: "#888", fontSize: "1rem" }}>
                Tell me about your day — wins, rants, progress. I'm here to listen.
              </p>
            </div>
            <button
              onClick={clearChat}
              style={{
                padding: "0.75rem 1.5rem",
                borderRadius: "12px",
                border: "1px solid #2a2a2a",
                background: "#1a1a1a",
                color: "#888",
                fontWeight: "600",
                cursor: "pointer",
                fontSize: "0.9rem",
                transition: "all 0.2s"
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = "#ff6b6b";
                e.target.style.color = "#ff6b6b";
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = "#2a2a2a";
                e.target.style.color = "#888";
              }}
            >
              🗑️ Clear Chat
            </button>
          </div>

          {/* Chat Window */}
          <div style={{
            flex: 1,
            overflowY: "auto",
            marginBottom: "2rem",
            display: "flex",
            flexDirection: "column",
            gap: "1rem"
          }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: msg.sender === "user" ? "flex-end" : "flex-start"
                }}
              >
                <div style={{
                  maxWidth: "70%",
                  padding: "1rem 1.5rem",
                  borderRadius: "16px",
                  background: msg.sender === "user" ? "#7c3aed" : "#1a1a1a",
                  color: "white",
                  border: msg.sender === "user" ? "none" : "1px solid #2a2a2a",
                  lineHeight: "1.6"
                }}>
                  {msg.text}
                </div>
              </div>
            ))}

            {error && (
              <div style={{
                display: "flex",
                justifyContent: "flex-start"
              }}>
                <div style={{
                  maxWidth: "70%",
                  padding: "1rem 1.5rem",
                  borderRadius: "16px",
                  background: "#ff6b6b20",
                  color: "#ff6b6b",
                  border: "1px solid #ff6b6b40",
                  lineHeight: "1.6"
                }}>
                  {error} — please try again in a bit.
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input Bar */}
          <div style={{
            display: "flex",
            gap: "1rem",
            padding: "1.5rem",
            background: "#1a1a1a",
            borderRadius: "16px",
            border: "1px solid #2a2a2a"
          }}>
            <input
              value={input}
              placeholder="Message gossip.ai…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={isLoading}
              style={{
                flex: 1,
                padding: "0.75rem",
                background: "transparent",
                border: "none",
                color: "white",
                fontSize: "1rem",
                outline: "none"
              }}
            />
            <button 
              onClick={sendMessage} 
              disabled={isLoading}
              style={{
                padding: "0.75rem 2rem",
                borderRadius: "12px",
                border: "none",
                background: isLoading ? "#444" : "#7c3aed",
                color: "white",
                fontWeight: "600",
                cursor: isLoading ? "not-allowed" : "pointer",
                fontSize: "1.5rem",
                transition: "all 0.2s"
              }}
              onMouseEnter={(e) => !isLoading && (e.target.style.background = "#6d28d9")}
              onMouseLeave={(e) => !isLoading && (e.target.style.background = "#7c3aed")}
            >
              {isLoading ? "⏳" : "➤"}
            </button>
          </div>
        </main>
    </div>
  );
}
