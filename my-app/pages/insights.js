import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";

export default function Goals() {
  const [semanticMemories, setSemanticMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [extracting, setExtracting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch stats
      const statsRes = await fetch("http://localhost:8000/memory/stats");
      const statsData = await statsRes.json();
      setStats(statsData);

      // Fetch semantic memories
      const semanticRes = await fetch("http://localhost:8000/memory/semantic/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: "user patterns and traits",
          limit: 50,
          min_confidence: 0.5
        })
      });
      const semanticData = await semanticRes.json();
      setSemanticMemories(semanticData.memories || []);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const triggerExtraction = async () => {
    setExtracting(true);
    try {
      const response = await fetch("http://localhost:8000/memory/semantic/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          min_episodes: 5,
          lookback_days: 30
        })
      });
      const data = await response.json();
      alert(`Extracted ${data.extracted_count} new insights!`);
      fetchData(); // Refresh data
    } catch (error) {
      console.error("Error extracting:", error);
      alert("Failed to extract insights");
    } finally {
      setExtracting(false);
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      trait: "#ff6b6b",
      preference: "#4ecdc4",
      fact: "#ffa500",
      pattern: "#9b59b6",
      relationship: "#3498db"
    };
    return colors[type] || "#666";
  };

  const getTypeIcon = (type) => {
    const icons = {
      trait: "🎭",
      preference: "❤️",
      fact: "📌",
      pattern: "🔄",
      relationship: "👥"
    };
    return icons[type] || "💡";
  };

  // Group memories by type
  const groupedMemories = semanticMemories.reduce((acc, memory) => {
    if (!acc[memory.type]) acc[memory.type] = [];
    acc[memory.type].push(memory);
    return acc;
  }, {});

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
          <span style={{ color: "white" }}>Goals</span>
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
              🎯 Your Goals & Insights
            </h1>
            <p style={{ color: "#888", fontSize: "1rem" }}>
              Track your goals and discover patterns learned from your conversations
            </p>
          </div>
          <button
            onClick={triggerExtraction}
            disabled={extracting}
            style={{
              padding: "1rem 2rem",
              borderRadius: "12px",
              border: "none",
              background: extracting ? "#444" : "#7c3aed",
              color: "white",
              fontWeight: "600",
              cursor: extracting ? "not-allowed" : "pointer",
              fontSize: "0.95rem",
              transition: "all 0.2s"
            }}
          >
            {extracting ? "Extracting..." : "Extract New Insights"}
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "1.5rem",
            marginBottom: "2.5rem"
          }}>
            <div style={{
              background: "#1a1a1a",
              padding: "1.5rem",
              borderRadius: "16px",
              border: "1px solid #2a2a2a",
              position: "relative"
            }}>
              <div style={{ 
                fontSize: "0.75rem", 
                color: "#666", 
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                marginBottom: "0.75rem"
              }}>
                Total Insights
              </div>
              <div style={{ fontSize: "2.5rem", fontWeight: "700", color: "white" }}>
                {stats.total_semantic}
              </div>
              <div style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#7c3aed"
              }} />
            </div>

            <div style={{
              background: "#1a1a1a",
              padding: "1.5rem",
              borderRadius: "16px",
              border: "1px solid #2a2a2a",
              position: "relative"
            }}>
              <div style={{ 
                fontSize: "0.75rem", 
                color: "#666", 
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                marginBottom: "0.75rem"
              }}>
                From Episodes
              </div>
              <div style={{ fontSize: "2.5rem", fontWeight: "700", color: "white" }}>
                {stats.total_episodes}
              </div>
              <div style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#4ecdc4"
              }} />
            </div>

            <div style={{
              background: "#1a1a1a",
              padding: "1.5rem",
              borderRadius: "16px",
              border: "1px solid #2a2a2a",
              position: "relative"
            }}>
              <div style={{ 
                fontSize: "0.75rem", 
                color: "#666", 
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                marginBottom: "0.75rem"
              }}>
                Avg Confidence
              </div>
              <div style={{ fontSize: "2.5rem", fontWeight: "700", color: "white" }}>
                {semanticMemories.length > 0 
                  ? Math.round((semanticMemories.reduce((sum, m) => sum + m.confidence, 0) / semanticMemories.length) * 100) + "%"
                  : "0%"
                }
              </div>
              <div style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#ffa500"
              }} />
            </div>
          </div>
        )}

        {/* Insights by Category */}
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem", color: "#666" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
            <div>Loading insights...</div>
          </div>
        ) : semanticMemories.length === 0 ? (
          <div style={{ 
            textAlign: "center", 
            padding: "4rem",
            background: "#1a1a1a",
            borderRadius: "16px",
            border: "1px solid #2a2a2a"
          }}>
            <div style={{ fontSize: "4rem", marginBottom: "1.5rem" }}>💡</div>
            <h3 style={{ color: "white", marginBottom: "0.75rem", fontSize: "1.5rem" }}>No insights yet</h3>
            <p style={{ color: "#666", fontSize: "1rem", marginBottom: "1.5rem" }}>
              Chat more to build up episodic memories, then extract insights!
            </p>
            <button
              onClick={triggerExtraction}
              style={{
                padding: "1rem 2rem",
                borderRadius: "12px",
                border: "none",
                background: "#7c3aed",
                color: "white",
                fontWeight: "600",
                cursor: "pointer"
              }}
            >
              Extract Insights Now
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            {Object.entries(groupedMemories).map(([type, memories]) => (
              <div key={type}>
                <div style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  gap: "0.75rem",
                  marginBottom: "1rem"
                }}>
                  <span style={{ fontSize: "1.5rem" }}>{getTypeIcon(type)}</span>
                  <h2 style={{ 
                    fontSize: "1.5rem", 
                    fontWeight: "600",
                    color: "white",
                    textTransform: "capitalize"
                  }}>
                    {type}s
                  </h2>
                  <span style={{
                    padding: "0.25rem 0.75rem",
                    borderRadius: "20px",
                    background: `${getTypeColor(type)}20`,
                    color: getTypeColor(type),
                    fontSize: "0.85rem",
                    fontWeight: "600"
                  }}>
                    {memories.length}
                  </span>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem" }}>
                  {memories.map((memory) => (
                    <div
                      key={memory.id}
                      style={{
                        background: "#1a1a1a",
                        padding: "1.5rem",
                        borderRadius: "16px",
                        border: "1px solid #2a2a2a",
                        borderLeft: `3px solid ${getTypeColor(memory.type)}`,
                        transition: "all 0.2s"
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "#3a3a3a";
                        e.currentTarget.style.transform = "translateY(-2px)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "#2a2a2a";
                        e.currentTarget.style.transform = "translateY(0)";
                      }}
                    >
                      <p style={{ 
                        color: "white", 
                        lineHeight: "1.6",
                        marginBottom: "1rem",
                        fontSize: "0.95rem"
                      }}>
                        {memory.content}
                      </p>

                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div style={{ display: "flex", gap: "1rem", fontSize: "0.85rem", color: "#666" }}>
                          <span>Confidence: {Math.round(memory.confidence * 100)}%</span>
                          <span>•</span>
                          <span>{memory.occurrence_count} occurrences</span>
                        </div>
                      </div>

                      {memory.tags && memory.tags.length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "1rem" }}>
                          {memory.tags.map((tag, idx) => (
                            <span
                              key={idx}
                              style={{
                                padding: "0.25rem 0.75rem",
                                borderRadius: "20px",
                                background: "rgba(255, 255, 255, 0.05)",
                                color: "#888",
                                fontSize: "0.8rem"
                              }}
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
