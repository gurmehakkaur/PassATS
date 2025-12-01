import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";

export default function Stories() {
  const [episodes, setEpisodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState(null);

  // Fetch memory statistics
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/memory/stats");
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  // Search episodes
  const searchEpisodes = async (query = "") => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/memory/episode/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query || "recent memories",
          limit: 20,
          min_importance: 0.0
        })
      });
      const data = await response.json();
      setEpisodes(data.episodes || []);
    } catch (error) {
      console.error("Error searching episodes:", error);
      setEpisodes([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    searchEpisodes();
  }, []);

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    searchEpisodes(searchQuery);
  };

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
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ 
            fontSize: "2.5rem", 
            fontWeight: "700",
            marginBottom: "0.5rem",
            color: "white"
          }}>
            📖 Your Stories
          </h1>
          <p style={{ color: "#888", fontSize: "1rem" }}>
            Episodic memories from your conversations. Track what matters to you.
          </p>
        </div>

        {/* Stats Section */}
        {stats && (
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "1.5rem",
            marginBottom: "2.5rem"
          }}>
            <div style={{
              background: "#1a1a1a",
              padding: "1.5rem",
              borderRadius: "16px",
              border: "1px solid #2a2a2a",
              position: "relative",
              overflow: "hidden"
            }}>
              <div style={{ 
                fontSize: "0.75rem", 
                color: "#666", 
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                marginBottom: "0.75rem"
              }}>
                Total Stories
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
                Important Moments
              </div>
              <div style={{ fontSize: "2.5rem", fontWeight: "700", color: "white" }}>
                {stats.high_importance_episodes}
              </div>
              <div style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#ff6b6b"
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
                Patterns Learned
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
                background: "#ffa500"
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
                Last 30 Days
              </div>
              <div style={{ fontSize: "2.5rem", fontWeight: "700", color: "white" }}>
                {stats.recent_episodes_30d}
              </div>
              <div style={{
                position: "absolute",
                top: "1rem",
                right: "1rem",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#9b59b6"
              }} />
            </div>
          </div>
        )}

        {/* Search Bar */}
        <form onSubmit={handleSearch} style={{ marginBottom: "2.5rem" }}>
          <div style={{ display: "flex", gap: "1rem" }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your memories... (e.g., 'work', 'relationships', 'anxiety')"
              style={{
                flex: 1,
                padding: "1rem 1.5rem",
                borderRadius: "12px",
                border: "1px solid #2a2a2a",
                background: "#1a1a1a",
                color: "white",
                fontSize: "0.95rem",
                outline: "none"
              }}
              onFocus={(e) => e.target.style.borderColor = "#667eea"}
              onBlur={(e) => e.target.style.borderColor = "#2a2a2a"}
            />
            <button
              type="submit"
              style={{
                padding: "1rem 2.5rem",
                borderRadius: "12px",
                border: "none",
                background: "#7c3aed",
                color: "white",
                fontWeight: "600",
                cursor: "pointer",
                fontSize: "0.95rem",
                transition: "all 0.2s"
              }}
              onMouseEnter={(e) => e.target.style.background = "#6d28d9"}
              onMouseLeave={(e) => e.target.style.background = "#7c3aed"}
            >
              Search
            </button>
          </div>
        </form>

        {/* Episodes List */}
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem", color: "#666" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
            <div>Loading your stories...</div>
          </div>
        ) : episodes.length === 0 ? (
          <div style={{ 
            textAlign: "center", 
            padding: "4rem",
            background: "#1a1a1a",
            borderRadius: "16px",
            border: "1px solid #2a2a2a"
          }}>
            <div style={{ fontSize: "4rem", marginBottom: "1.5rem" }}>📝</div>
            <h3 style={{ color: "white", marginBottom: "0.75rem", fontSize: "1.5rem" }}>No stories yet</h3>
            <p style={{ color: "#666", fontSize: "1rem" }}>
              Start chatting to create your first episodic memory!
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {episodes.map((episode) => (
              <div
                key={episode.id}
                style={{
                  background: "#1a1a1a",
                  padding: "2rem",
                  borderRadius: "16px",
                  border: "1px solid #2a2a2a",
                  transition: "all 0.2s ease"
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
                {/* Header */}
                <div style={{ 
                  display: "flex", 
                  justifyContent: "space-between", 
                  alignItems: "center",
                  marginBottom: "1rem"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{ fontSize: "1.5rem" }}>
                      {getEmotionEmoji(episode.emotion)}
                    </span>
                    <span style={{ 
                      fontSize: "0.85rem", 
                      color: "#95a5a6",
                      textTransform: "capitalize"
                    }}>
                      {episode.emotion || "neutral"}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                    <div style={{
                      width: "8px",
                      height: "8px",
                      borderRadius: "50%",
                      background: getImportanceColor(episode.importance)
                    }} />
                    <span style={{ fontSize: "0.85rem", color: "#95a5a6" }}>
                      {formatDate(episode.timestamp)}
                    </span>
                  </div>
                </div>

                {/* Story */}
                <p style={{ 
                  color: "white", 
                  lineHeight: "1.6",
                  marginBottom: "1rem",
                  fontSize: "1rem"
                }}>
                  {episode.story}
                </p>

                {/* Tags & Entities */}
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {episode.key_entities && episode.key_entities.map((entity, idx) => (
                    <span
                      key={idx}
                      style={{
                        padding: "0.25rem 0.75rem",
                        borderRadius: "20px",
                        background: "rgba(102, 126, 234, 0.2)",
                        color: "#667eea",
                        fontSize: "0.85rem",
                        border: "1px solid rgba(102, 126, 234, 0.3)"
                      }}
                    >
                      {entity}
                    </span>
                  ))}
                  {episode.tags && episode.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      style={{
                        padding: "0.25rem 0.75rem",
                        borderRadius: "20px",
                        background: "rgba(78, 205, 196, 0.2)",
                        color: "#4ecdc4",
                        fontSize: "0.85rem",
                        border: "1px solid rgba(78, 205, 196, 0.3)"
                      }}
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                {/* User Intent */}
                {episode.user_intent && (
                  <div style={{
                    marginTop: "1rem",
                    padding: "0.75rem",
                    background: "rgba(255, 255, 255, 0.03)",
                    borderRadius: "8px",
                    borderLeft: "3px solid #667eea"
                  }}>
                    <span style={{ fontSize: "0.85rem", color: "#95a5a6" }}>
                      Intent: 
                    </span>
                    <span style={{ fontSize: "0.85rem", color: "white", marginLeft: "0.5rem" }}>
                      {episode.user_intent}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
