import Head from "next/head";
import { Geist, Geist_Mono } from "next/font/google";
import Navigation from "@/components/Navigation";
import styles from "@/styles/Dashboard.module.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function About() {
  return (
    <>
      <Head>
        <title>Gossip Characters - gossip.ai</title>
        <meta name="description" content="Discover gossip characters" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className={`${styles.container} ${geistSans.variable} ${geistMono.variable}`}>
        <Navigation />
        <section style={{ marginTop: "6rem", padding: "4rem 2rem", minHeight: "60vh" }}>
          <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
            <h1 style={{ fontSize: "32px", marginBottom: "20px" }}>Gossip Characters</h1>
            <p style={{ color: "#bbb", lineHeight: "1.6" }}>
              Coming soon... Discover interesting characters and their stories!
            </p>
          </div>
        </section>
        <footer className={styles.footer}>
          <div className={styles.footerContent}>
            <div className={styles.footerSection}>
              <h4>PassATS</h4>
              <p>AI-powered resume customization for job seekers</p>
            </div>
            <div className={styles.footerSection}>
              <h4>Product</h4>
              <a href="#">Features</a>
              <a href="#">Pricing</a>
              <a href="#">FAQ</a>
            </div>
            <div className={styles.footerSection}>
              <h4>Company</h4>
              <a href="#">About</a>
              <a href="#">Blog</a>
              <a href="#">Contact</a>
            </div>
          </div>
          <div className={styles.footerBottom}>
            <p>&copy; 2025 PassATS. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </>
  );
}
