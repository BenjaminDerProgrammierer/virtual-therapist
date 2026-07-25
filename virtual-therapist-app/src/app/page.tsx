import {ArrowRight, Database, HeartHandshake} from "lucide-react";
import layout from "./layout.module.css";
import styles from "./page.module.css";
import Image from 'next/image'
import snickers from '../../public/snickers.jpg'


export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <section className={styles.intro}>
          <p className={styles.eyebrow}>Clanker therapy</p>
          <h1>Agentic <span className="underline">AI-powered</span> hamster therapy.</h1>
          <p>
            Dr. Snickers is SOTA—in every therapy benchmark. Honestly? This not just another therapist—this will put you—ahead of everyone else—in 2026.
          </p>
          <a className={styles.button} href="/login">Login</a>
        </section>

        <Image
          className={layout.border}
          src={snickers}
          width="1000"
          height="1000"
          alt="Dr. Snickers"
          style={{width: "100%"}}
        />
      </main>
    </div>
  );
}
