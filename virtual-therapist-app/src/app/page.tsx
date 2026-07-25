import {ArrowRight, Database, HeartHandshake} from "lucide-react";
import layout from "./layout.module.css";
import styles from "./page.module.css";
import Image from 'next/image'
import snickers from '../../public/snickers.jpg'
import {Sparkles} from "lucide-react";


export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <section className={styles.intro}>
          <p className={styles.eyebrow}>Clanker therapy</p>
          <h1>Agentic <Sparkles className={styles.aiaiai}/>AI-powered<Sparkles className={styles.aiaiai}/> hamster therapy.</h1>
          <p>
            Dr. Snickers is SOTA—in every therapy benchmark. Honestly? This not just another therapist—this will put you—ahead of everyone else—in 2026.
          </p>
          <div className={styles.phone}>
            <p className={styles.phonep1}>Call Dr. Snickers</p>
            <p className={styles.phonep2}>+44 221 596 196 054</p>
          </div>
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
