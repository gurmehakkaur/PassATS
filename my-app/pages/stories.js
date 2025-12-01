import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";

export default function Stories() {
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedJournals, setExpandedJournals] = useState(new Set());

  // Expand all journals by default
  useEffect(() => {
    if (journals.length > 0 && expandedJournals.size === 0) {
      setExpandedJournals(new Set(journals.map(j => j.label)));
    }
  }, [journals]);

  // Fetch journals
  const fetchJournals = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/memory/journals");
      const data = await response.json();
      setJournals(data.journals || []);
    } catch (error) {
      console.error("Error fetching journals:", error);
      setJournals([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchJournals();
  }, []);

  // Format date
  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  // Get emotion emoji
  const getEmotionEmoji = (emotion) => {
    const emojiMap = {
      happy: "😊",
      sad: "😢",
      anxious: "😰",
      excited: "🎉",
      frustrated: "😤",
      neutral: "😐",
      confused: "😕",
      proud: "🏆"
    };
    return emojiMap[emotion] || "💭";
  };

  // Get importance color
  const getImportanceColor = (importance) => {
    if (importance >= 0.8) return "#ff6b6b";
    if (importance >= 0.6) return "#ffa500";
    if (importance >= 0.4) return "#4ecdc4";
    return "#95a5a6";
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
          <span style={{ color: "white" }}>Stories</span>
        </div>

        {/* Header */}
        <div style={{ marginBottom: "3rem" }}>
          <h1 style={{ 
            fontSize: "2.5rem", 
            fontWeight: "700",
            marginBottom: "0.5rem",
            color: "white"
          }}>
            📖 My Journal
          </h1>
          <p style={{ color: "#888", fontSize: "1rem", marginBottom: "1rem" }}>
            My conversations organized by topic. Each card is a journal entry.
          </p>
          {!loading && journals.length > 0 && (
            <div style={{ 
              display: "inline-block",
              padding: "0.5rem 1rem",
              background: "#1a1a1a",
              border: "1px solid #2a2a2a",
              borderRadius: "8px",
              color: "#888",
              fontSize: "0.9rem"
            }}>
              📚 {journals.length} {journals.length === 1 ? 'journal' : 'journals'}
            </div>
          )}
        </div>

        {/* Journal Cards */}
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem", color: "#666" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
            <div>Loading my journal...</div>
          </div>
        ) : journals.length === 0 ? (
          <div style={{ 
            textAlign: "center", 
            padding: "4rem",
            background: "#1a1a1a",
            borderRadius: "16px",
            border: "1px solid #2a2a2a"
          }}>
            <div style={{ fontSize: "4rem", marginBottom: "1.5rem" }}>📝</div>
            <h3 style={{ color: "white", marginBottom: "0.75rem", fontSize: "1.5rem" }}>I haven't written anything yet</h3>
            <p style={{ color: "#666", fontSize: "1rem" }}>
              Start chatting to create my first journal entry!
            </p>
          </div>
        ) : (
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
            gap: "1.5rem" 
          }}>
            {journals.map((journal) => {
              const isExpanded = expandedJournals.has(journal.label);
              const toggleExpand = () => {
                const newExpanded = new Set(expandedJournals);
                if (isExpanded) {
                  newExpanded.delete(journal.label);
                } else {
                  newExpanded.add(journal.label);
                }
                setExpandedJournals(newExpanded);
              };

              return (
              <div
                key={journal.label}
                onClick={toggleExpand}
                style={{
                  background: "#1a1a1a",
                  padding: "2rem",
                  borderRadius: "16px",
                  border: isExpanded ? "2px solid #7c3aed" : "1px solid #2a2a2a",
                  transition: "all 0.2s ease",
                  cursor: "pointer"
                }}
                onMouseEnter={(e) => {
                  if (!isExpanded) {
                    e.currentTarget.style.borderColor = "#3a3a3a";
                  }
                  e.currentTarget.style.transform = "translateY(-4px)";
                }}
                onMouseLeave={(e) => {
                  if (!isExpanded) {
                    e.currentTarget.style.borderColor = "#2a2a2a";
                  }
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                {/* Journal Header */}
                <div style={{ marginBottom: isExpanded ? "1.5rem" : "0" }}>
                  <h3 style={{ 
                    color: "white", 
                    fontSize: "1.3rem", 
                    fontWeight: "600",
                    marginBottom: "0.5rem"
                  }}>
                    📔 {journal.label}
                  </h3>
                  <div style={{ 
                    fontSize: "0.85rem", 
                    color: "#888",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem"
                  }}>
                    <span>{journal.entry_count} {journal.entry_count === 1 ? 'entry' : 'entries'}</span>
                    <span>•</span>
                    <span>{formatDate(journal.entries[0]?.timestamp * 1000)}</span>
                  </div>
                </div>

                {/* Show all entries when expanded */}
                {isExpanded && (
                  <div style={{ 
                    marginTop: "1.5rem",
                    paddingTop: "1.5rem",
                    borderTop: "1px solid #2a2a2a"
                  }}>
                    <h4 style={{ 
                      color: "white", 
                      fontSize: "0.9rem", 
                      fontWeight: "600",
                      marginBottom: "1rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px"
                    }}>
                      My Entries
                    </h4>
                    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                      {journal.entries.map((entry, idx) => (
                        <div
                          key={entry.id}
                          style={{
                            padding: "1rem",
                            background: "rgba(255, 255, 255, 0.03)",
                            borderRadius: "8px",
                            borderLeft: `3px solid ${getImportanceColor(entry.importance)}`
                          }}
                        >
                          <div style={{ 
                            display: "flex", 
                            justifyContent: "space-between",
                            marginBottom: "0.5rem"
                          }}>
                            <span style={{ fontSize: "1.2rem" }}>
                              {getEmotionEmoji(entry.emotion)}
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "#666" }}>
                              {formatDate(entry.timestamp * 1000)}
                            </span>
                          </div>
                          <p style={{ 
                            color: "#e5e5e5", 
                            fontSize: "0.9rem",
                            lineHeight: "1.5"
                          }}>
                            {entry.story}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* View More Button */}
                <div style={{ 
                  marginTop: "1rem",
                  textAlign: "center",
                  color: "#7c3aed",
                  fontSize: "0.85rem",
                  fontWeight: "600"
                }}>
                  {isExpanded ? "▲ Collapse" : `▼ View all ${journal.entry_count} entries`}
                </div>
              </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
