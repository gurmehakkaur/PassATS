import { useEffect, useState, useRef } from "react";
import styles from "@/styles/Dashboard.module.css";
import Navigation from "@/components/Navigation";

export default function Dashboard() {
  const [greeting, setGreeting] = useState("");
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Hey little hardworking fellow! How did your day go? I am so excited to hear!!" },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good Morning");
    else if (hour < 17) setGreeting("Good Afternoon");
    else setGreeting("Good Evening");
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setInput("");

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Got it! Want to dive deeper? 😊" },
      ]);
    }, 500);
  };

  return (
    <>
      <Navigation brand="gossip.ai" />

      <div className={styles.layout}>
        {/* SIDEBAR */}
        <aside className={styles.sidebar}>
          <h2 className={styles.sidebarTitle}>Recent Gossips</h2>

          <div className={styles.storyList}>
            <div className={styles.story}> Nailed my presentation today!</div>
            <div className={styles.story}> Tough call with client…</div>
            <div className={styles.story}> Manager appreciated my work!</div>
            <div className={styles.emptyStory}>Your next update goes here…</div>
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

            <div ref={bottomRef} />
          </div>

          <div className={styles.inputBar}>
            <input
              value={input}
              placeholder="Message gossip.ai…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              className={styles.input}
            />
            <button onClick={sendMessage} className={styles.send}>
              ➤
            </button>
          </div>
        </main>
      </div>
    </>
  );
}
