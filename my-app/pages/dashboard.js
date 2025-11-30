import { useEffect, useState, useRef } from "react";
import styles from "@/styles/Dashboard.module.css";
import Navigation from "@/components/Navigation";

export default function Dashboard() {
  const [greeting, setGreeting] = useState("");
  const [threads, setThreads] = useState([]);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);
  const isInitialLoad = useRef(true);

  const CHAT_API_URL =
    process.env.NEXT_PUBLIC_CHAT_API_URL || "http://localhost:8000/chat";

  const INITIAL_AI_MESSAGE = {
    sender: "ai",
    text: "Hey little hardworking fellow! How did your day go? I am so excited to hear!!",
  };

  const createThread = () => ({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    messages: [INITIAL_AI_MESSAGE],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  });

  const activeThread = threads.find((thread) => thread.id === activeThreadId) || threads[0];
  const messages = activeThread?.messages || [];

  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = window.localStorage.getItem("gossip_threads");
    if (stored) {
      const parsed = JSON.parse(stored);
      setThreads(parsed);
      setActiveThreadId(parsed[0]?.id || null);
    } else {
      const starter = createThread();
      setThreads([starter]);
      setActiveThreadId(starter.id);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (isInitialLoad.current) {
      isInitialLoad.current = false;
      return;
    }
    window.localStorage.setItem("gossip_threads", JSON.stringify(threads));
  }, [threads]);

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

  const updateThreadMessages = (threadId, transform) => {
    setThreads((prev) =>
      prev.map((thread) =>
        thread.id === threadId
          ? {
              ...thread,
              messages: transform(thread.messages),
              updatedAt: Date.now(),
            }
          : thread
      )
    );
  };

  const summarizeThread = (thread) => {
    const source =
      [...thread.messages]
        .reverse()
        .find((msg) => msg.sender === "user")?.text || thread.messages[0]?.text || "New chat";
    return source.split(/\s+/).slice(0, 4).join(" ");
  };

  const startNewChat = () => {
    const newThread = createThread();
    setThreads((prev) => [newThread, ...prev]);
    setActiveThreadId(newThread.id);
    setInput("");
    setError(null);
  };

  const switchThread = (threadId) => {
    setActiveThreadId(threadId);
    setInput("");
    setError(null);
  };

  const sendMessage = async () => {
    if (!activeThread || !input.trim() || isLoading) return;

    const userText = input.trim();
    updateThreadMessages(activeThread.id, (msgs) => [...msgs, { sender: "user", text: userText }]);
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
      updateThreadMessages(activeThread.id, (msgs) => [...msgs, { sender: "ai", text: data.reply }]);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navigation brand="gossip.ai" />

      <div className={styles.layout}>
        {/* SIDEBAR */}
        <aside className={styles.sidebar}>
          <div className={styles.sidebarHeader}>
            <h2 className={styles.sidebarTitle}>Chats</h2>
            <button className={styles.newChatBtn} onClick={startNewChat}>
              + New Chat
            </button>
          </div>

          <div className={styles.storyList}>
            {threads.length === 0 && (
              <div className={styles.emptyStory}>No chats yet. Start one!</div>
            )}
            {threads.map((thread) => (
              <button
                key={thread.id}
                className={
                  thread.id === activeThread?.id
                    ? `${styles.story} ${styles.activeStory}`
                    : styles.story
                }
                onClick={() => switchThread(thread.id)}
              >
                <div className={styles.storySummary}>{summarizeThread(thread)}</div>
                <div className={styles.storyMeta}>
                  {new Date(thread.updatedAt).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </button>
            ))}
          </div>
        </aside>

        {/* MAIN CHAT */}
        <main className={styles.main}>
          <div className={styles.header}>
            <h1 className={styles.greeting}>
              {greeting}, ready to spill the tea?
            </h1>
            <p className={styles.subtitle}>
              Tell me about your day — wins, rants, progress.
            </p>
          </div>

          <div className={styles.chatWindow}>
            {messages.map((msg, i) => (
              <div
                key={i}
                className={
                  msg.sender === "user"
                    ? styles.userBubble
                    : styles.aiBubble
                }
              >
                {msg.text}
              </div>
            ))}

            {error && (
              <div className={styles.aiBubble}>
                {error} — please try again in a bit.
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          <div className={styles.inputBar}>
            <input
              value={input}
              placeholder="Message gossip.ai…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              className={styles.input}
              disabled={isLoading}
            />
            <button onClick={sendMessage} className={styles.send} disabled={isLoading}>
              {isLoading ? "…" : "➤"}
            </button>
          </div>
        </main>
      </div>
    </>
  );
}
