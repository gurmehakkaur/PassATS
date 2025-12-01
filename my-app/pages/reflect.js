import { useState } from "react";
import Sidebar from "@/components/Sidebar";

export default function Reflect() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [detectedAgent, setDetectedAgent] = useState(null);

  const handleReflect = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setDetectedAgent(null);

    try {
      const response = await fetch("http://localhost:8000/reflect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() })
      });

      const data = await response.json();
      setResult(data.response);
      setDetectedAgent(data.agent_type);
    } catch (error) {
      console.error("Reflection error:", error);
      setResult("Failed to generate reflection. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const agentInfo = {
    personal: {
      icon: "",
      title: "Personal Reflection",
      color: "#8b5cf6",
      description: "Deep insights about your journey and goals"
    },
    meeting: {
      icon: "",
      title: "Meeting Overview",
      color: "#3b82f6",
      description: "Professional summary for manager discussions"
    },
    resume: {
      icon: "",
      title: "Resume Builder",
      color: "#10b981",
      description: "Tailored bullet points for job applications"
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#0a0a0a" }}>
      <Sidebar />
      
      <main style={{ 
        flex: 1, 
        padding: "2rem 3rem",
        marginLeft: "280px",
        overflowY: "auto"
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
          <span style={{ color: "white" }}>Reflect</span>
        </div>

        {/* Header */}
        <div style={{ marginBottom: "3rem" }}>
          <h1 style={{ 
            fontSize: "2.5rem", 
            fontWeight: "700",
            marginBottom: "0.5rem",
            color: "white"
          }}>
            🔍 Reflect & Generate
          </h1>
          <p style={{ color: "#888", fontSize: "1rem" }}>
            Ask anything - I'll automatically choose the right format for you
          </p>
        </div>

        {/* Agent Cards */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "1.5rem",
          marginBottom: "3rem"
        }}>
          {Object.entries(agentInfo).map(([key, info]) => (
            <div
              key={key}
              style={{
                background: "#1a1a1a",
                border: `2px solid ${detectedAgent === key ? info.color : "#2a2a2a"}`,
                borderRadius: "16px",
                padding: "1.5rem",
                transition: "all 0.3s"
              }}
            >
              <div style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>
                {info.icon}
              </div>
              <h3 style={{ 
                color: "white", 
                fontSize: "1.1rem", 
                fontWeight: "600",
                marginBottom: "0.5rem"
              }}>
                {info.title}
              </h3>
              <p style={{ color: "#888", fontSize: "0.9rem", lineHeight: "1.5" }}>
                {info.description}
              </p>
            </div>
          ))}
        </div>

        {/* Input Section */}
        <div style={{
          background: "#1a1a1a",
          border: "1px solid #2a2a2a",
          borderRadius: "16px",
          padding: "2rem",
          marginBottom: "2rem"
        }}>
          <label style={{
            display: "block",
            color: "#888",
            fontSize: "0.9rem",
            marginBottom: "1rem",
            fontWeight: "500"
          }}>
            What do you need?
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Examples:\n• How am I progressing towards my career goals?\n• Give me talking points for my year-end review\n• Generate resume bullets for a software engineering role requiring React and Python"
            style={{
              width: "100%",
              minHeight: "120px",
              background: "#0a0a0a",
              border: "1px solid #2a2a2a",
              borderRadius: "12px",
              padding: "1rem",
              color: "white",
              fontSize: "1rem",
              fontFamily: "inherit",
              resize: "vertical",
              outline: "none"
            }}
            onFocus={(e) => e.target.style.borderColor = "#7c3aed"}
            onBlur={(e) => e.target.style.borderColor = "#2a2a2a"}
          />
          <button
            onClick={handleReflect}
            disabled={loading || !query.trim()}
            style={{
              marginTop: "1rem",
              padding: "1rem 2rem",
              background: loading || !query.trim() ? "#444" : "#7c3aed",
              color: "white",
              border: "none",
              borderRadius: "12px",
              fontSize: "1rem",
              fontWeight: "600",
              cursor: loading || !query.trim() ? "not-allowed" : "pointer",
              transition: "all 0.2s"
            }}
            onMouseEnter={(e) => {
              if (!loading && query.trim()) e.target.style.background = "#6d28d9";
            }}
            onMouseLeave={(e) => {
              if (!loading && query.trim()) e.target.style.background = "#7c3aed";
            }}
          >
            {loading ? "✨ Generating..." : "🚀 Generate"}
          </button>
        </div>

        {/* Result Section */}
        {result && (
          <div style={{
            background: "#1a1a1a",
            border: `2px solid ${detectedAgent ? agentInfo[detectedAgent]?.color : "#2a2a2a"}`,
            borderRadius: "16px",
            padding: "2rem",
            animation: "fadeIn 0.3s ease-in"
          }}>
            {detectedAgent && (
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "1.5rem",
                paddingBottom: "1rem",
                borderBottom: "1px solid #2a2a2a"
              }}>
                <span style={{ fontSize: "1.5rem" }}>
                  {agentInfo[detectedAgent].icon}
                </span>
                <div>
                  <div style={{ 
                    color: agentInfo[detectedAgent].color, 
                    fontSize: "0.85rem",
                    fontWeight: "600",
                    textTransform: "uppercase",
                    letterSpacing: "0.5px"
                  }}>
                    {agentInfo[detectedAgent].title}
                  </div>
                </div>
              </div>
            )}
            <div style={{
              color: "#e5e5e5",
              fontSize: "1rem",
              lineHeight: "1.8",
              whiteSpace: "pre-wrap"
            }}>
              {result}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
