import Link from "next/link";
import { useState, useEffect } from "react";
import styles from "@/styles/Dashboard.module.css";

export default function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav className={`${styles.navbar} ${isScrolled ? styles.scrolled : ""}`}>
      <div className={styles.navContent}>
        <div className={styles.leftStack}>
          <div className={styles.logoContainer}>
            <Link href="/dashboard" className={styles.logo}>
              <img
                src="/image.png"
                alt="gossip.ai logo"
                className={styles.logoImg}
              />
              <span className={styles.logoText}>gossip.ai</span>
            </Link>
          </div>
          <div className={styles.navLinks}>
            <Link href="/dashboard" className={styles.navLink}>
              Work Bestie
            </Link>
            <Link href="/Goals" className={styles.navLink}>
              Goals
            </Link>
            <Link href="/reflect" className={styles.navLink}>
              Reflect
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
