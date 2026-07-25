import {ArrowRight, Database, HeartHandshake} from "lucide-react";
import styles from "./page.module.css";
import TopBar from "@/components/TopBar/TopBar";
import Image from 'next/image'
import snickers from '../../public/snickers.jpg'


export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <section className={styles.intro}>
          <p className={styles.eyebrow}>Clanker therapy</p>
          <h1>Agentic AI-powered clanker therapy.</h1>
          <p>
            Dr. Snickers is SOTA—in every therapy benchmark. Honestly? This therapy will put you—ahead of everyone else—in 2026.
          </p>
        </section>

        <a className={styles.button} href="">Login</a>

        <Image
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
