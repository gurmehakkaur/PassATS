import { useState, useEffect } from "react";
import Sidebar from "@/components/Sidebar";

export default function Goals() {
  const [goals, setGoals] = useState([
    { id: 1, title: "Get promoted to Senior Engineer", progress: 65, category: "Career", deadline: "2024-06-30" },
    { id: 2, title: "Build a side project", progress: 30, category: "Personal", deadline: "2024-12-31" },
    { id: 3, title: "Network with 5 industry leaders", progress: 80, category: "Networking", deadline: "2024-03-31" }
  ]);
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [newGoal, setNewGoal] = useState({ title: "", category: "Career", deadline: "" });

  const addGoal = () => {
    if (!newGoal.title.trim()) return;
    
    const goal = {
      id: Date.now(),
      title: newGoal.title,
      progress: 0,
      category: newGoal.category,
      deadline: newGoal.deadline
    };
    
    setGoals([...goals, goal]);
    setNewGoal({ title: "", category: "Career", deadline: "" });
    setShowAddGoal(false);
  };

  const deleteGoal = (id) => {
    setGoals(goals.filter(g => g.id !== id));
  };

  const getCategoryColor = (category) => {
    const colors = {
      Career: "#7c3aed",
      Personal: "#4ecdc4",
      Networking: "#ffa500",
      Health: "#ff6b6b",
      Learning: "#3498db"
    };
    return colors[category] || "#666";
  };

  const getCategoryIcon = (category) => {
    const icons = {
      Career: "💼",
      Personal: "🌟",
      Networking: "🤝",
      Health: "💪",
      Learning: "📚"
    };
    return icons[category] || "🎯";
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
              🎯 My Goals
            </h1>
            <p style={{ color: "#888", fontSize: "1rem" }}>
              Track my goals and progress based on conversations
            </p>
          </div>
          <button
            onClick={() => setShowAddGoal(true)}
            style={{
              padding: "1rem 2rem",
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
            + Add Goal
          </button>
        </div>

        {/* Add Goal Modal */}
        {showAddGoal && (
          <div style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}
          onClick={() => setShowAddGoal(false)}
          >
            <div style={{
              background: "#1a1a1a",
              padding: "2rem",
              borderRadius: "16px",
              border: "1px solid #2a2a2a",
              width: "500px",
              maxWidth: "90%"
            }}
            onClick={(e) => e.stopPropagation()}
            >
              <h2 style={{ color: "white", marginBottom: "1.5rem", fontSize: "1.5rem" }}>Add New Goal</h2>
              
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ color: "#888", fontSize: "0.9rem", display: "block", marginBottom: "0.5rem" }}>Goal Title</label>
                <input
                  type="text"
                  value={newGoal.title}
                  onChange={(e) => setNewGoal({...newGoal, title: e.target.value})}
                  placeholder="e.g., Get promoted to Senior Engineer"
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "1px solid #2a2a2a",
                    background: "#0a0a0a",
                    color: "white",
                    fontSize: "1rem"
                  }}
                />
              </div>

              <div style={{ marginBottom: "1rem" }}>
                <label style={{ color: "#888", fontSize: "0.9rem", display: "block", marginBottom: "0.5rem" }}>Category</label>
                <select
                  value={newGoal.category}
                  onChange={(e) => setNewGoal({...newGoal, category: e.target.value})}
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "1px solid #2a2a2a",
                    background: "#0a0a0a",
                    color: "white",
                    fontSize: "1rem"
                  }}
                >
                  <option value="Career">💼 Career</option>
                  <option value="Personal">🌟 Personal</option>
                  <option value="Networking">🤝 Networking</option>
                  <option value="Health">💪 Health</option>
                  <option value="Learning">📚 Learning</option>
                </select>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={{ color: "#888", fontSize: "0.9rem", display: "block", marginBottom: "0.5rem" }}>Deadline (Optional)</label>
                <input
                  type="date"
                  value={newGoal.deadline}
                  onChange={(e) => setNewGoal({...newGoal, deadline: e.target.value})}
                  style={{
                    width: "100%",
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "1px solid #2a2a2a",
                    background: "#0a0a0a",
                    color: "white",
                    fontSize: "1rem"
                  }}
                />
              </div>

              <div style={{ display: "flex", gap: "1rem" }}>
                <button
                  onClick={addGoal}
                  style={{
                    flex: 1,
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "none",
                    background: "#7c3aed",
                    color: "white",
                    fontWeight: "600",
                    cursor: "pointer"
                  }}
                >
                  Add Goal
                </button>
                <button
                  onClick={() => setShowAddGoal(false)}
                  style={{
                    flex: 1,
                    padding: "0.75rem",
                    borderRadius: "8px",
                    border: "1px solid #2a2a2a",
                    background: "transparent",
                    color: "#888",
                    fontWeight: "600",
                    cursor: "pointer"
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Goals List */}
        {goals.length === 0 ? (
          <div style={{ 
            textAlign: "center", 
            padding: "4rem",
            background: "#1a1a1a",
            borderRadius: "16px",
            border: "1px solid #2a2a2a"
          }}>
            <div style={{ fontSize: "4rem", marginBottom: "1.5rem" }}>🎯</div>
            <h3 style={{ color: "white", marginBottom: "0.75rem", fontSize: "1.5rem" }}>No goals yet</h3>
            <p style={{ color: "#666", fontSize: "1rem", marginBottom: "1.5rem" }}>
              Add your first goal to start tracking progress!
            </p>
            <button
              onClick={() => setShowAddGoal(true)}
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
              + Add Goal
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {goals.map((goal) => (
              <div
                key={goal.id}
                style={{
                  background: "#1a1a1a",
                  padding: "2rem",
                  borderRadius: "16px",
                  border: "1px solid #2a2a2a",
                  borderLeft: `4px solid ${getCategoryColor(goal.category)}`,
                  transition: "all 0.2s"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "#3a3a3a";
                  e.currentTarget.style.transform = "translateX(4px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "#2a2a2a";
                  e.currentTarget.style.transform = "translateX(0)";
                }}
              >
                {/* Goal Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
                      <span style={{ fontSize: "1.5rem" }}>{getCategoryIcon(goal.category)}</span>
                      <h3 style={{ color: "white", fontSize: "1.3rem", fontWeight: "600" }}>
                        {goal.title}
                      </h3>
                    </div>
                    <div style={{ display: "flex", gap: "1rem", fontSize: "0.85rem", color: "#666" }}>
                      <span style={{
                        padding: "0.25rem 0.75rem",
                        borderRadius: "20px",
                        background: `${getCategoryColor(goal.category)}20`,
                        color: getCategoryColor(goal.category),
                        fontWeight: "600"
                      }}>
                        {goal.category}
                      </span>
                      {goal.deadline && (
                        <span>📅 {new Date(goal.deadline).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => deleteGoal(goal.id)}
                    style={{
                      padding: "0.5rem 1rem",
                      borderRadius: "8px",
                      border: "1px solid #2a2a2a",
                      background: "transparent",
                      color: "#ff6b6b",
                      cursor: "pointer",
                      fontSize: "0.85rem"
                    }}
                  >
                    Delete
                  </button>
                </div>

                {/* Progress Bar */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                    <span style={{ color: "#888", fontSize: "0.9rem" }}>Progress</span>
                    <span style={{ color: "white", fontSize: "0.9rem", fontWeight: "600" }}>{goal.progress}%</span>
                  </div>
                  <div style={{
                    width: "100%",
                    height: "12px",
                    background: "#0a0a0a",
                    borderRadius: "6px",
                    overflow: "hidden",
                    border: "1px solid #2a2a2a"
                  }}>
                    <div style={{
                      width: `${goal.progress}%`,
                      height: "100%",
                      background: `linear-gradient(90deg, ${getCategoryColor(goal.category)}, ${getCategoryColor(goal.category)}dd)`,
                      transition: "width 0.3s ease",
                      borderRadius: "6px"
                    }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
