import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";

export default function Sidebar() {
  const router = useRouter();
  const [hoveredItem, setHoveredItem] = useState(null);

  const menuItems = [
    { icon: "🏠", label: "Dashboard", path: "/dashboard" },
    { icon: "📖", label: "Stories", path: "/stories" },
    { icon: "🎯", label: "Goals", path: "/goals" },
    { icon: "🔍", label: "Reflect", path: "/reflect" },
  ];

  const isActive = (path) => router.pathname === path;

  return (
    <div style={{
      position: "fixed",
      left: 0,
      top: 0,
      width: "280px",
      height: "100vh",
      background: "#0f0f0f",
      borderRight: "1px solid #1a1a1a",
      display: "flex",
      flexDirection: "column",
      padding: "1.5rem",
      zIndex: 1000
    }}>
      {/* Logo */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "0.75rem",
        marginBottom: "2.5rem",
        padding: "0.5rem"
      }}>
        <div style={{
          width: "40px",
          height: "40px",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          borderRadius: "10px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "1.5rem"
        }}>
          🧠
        </div>
        <span style={{
          fontSize: "1.5rem",
          fontWeight: "700",
          color: "white"
        }}>
          Gossip AI
        </span>
      </div>

      {/* Create Button */}
      <Link href="/dashboard" style={{ textDecoration: "none", marginBottom: "2rem" }}>
        <button style={{
          width: "100%",
          padding: "1rem",
          borderRadius: "12px",
          border: "none",
          background: "#7c3aed",
          color: "white",
          fontWeight: "600",
          fontSize: "0.95rem",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "0.5rem",
          transition: "all 0.2s"
        }}
        onMouseEnter={(e) => e.target.style.background = "#6d28d9"}
        onMouseLeave={(e) => e.target.style.background = "#7c3aed"}
        >
          <span style={{ fontSize: "1.2rem" }}>+</span>
          New Chat
        </button>
      </Link>

      {/* Main Menu */}
      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {menuItems.map((item) => (
          <Link
            key={item.path}
            href={item.path}
            style={{ textDecoration: "none" }}
            onMouseEnter={() => setHoveredItem(item.path)}
            onMouseLeave={() => setHoveredItem(null)}
          >
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "1rem",
              padding: "0.875rem 1rem",
              borderRadius: "10px",
              background: isActive(item.path) ? "#1a1a1a" : "transparent",
              color: isActive(item.path) ? "white" : "#666",
              cursor: "pointer",
              transition: "all 0.2s",
              ...(hoveredItem === item.path && !isActive(item.path) && {
                background: "#151515",
                color: "#999"
              })
            }}>
              <span style={{ fontSize: "1.25rem" }}>{item.icon}</span>
              <span style={{ fontSize: "0.95rem", fontWeight: "500" }}>{item.label}</span>
            </div>
          </Link>
        ))}
      </nav>
    </div>
  );
}
