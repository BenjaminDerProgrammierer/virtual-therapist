import { ArrowRight, Database, HeartHandshake } from "lucide-react";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <div className={styles.heroIcon} aria-hidden="true">
          <HeartHandshake size={30} strokeWidth={1.8} />
        </div>

        <section className={styles.intro}>
          <p className={styles.eyebrow}>Virtual therapist</p>
          <h1>Prisma and Lucide are ready to use.</h1>
          <p>
            This page renders icons from Lucide React. The example API below
            reads and creates users with Prisma and a PostgreSQL database.
          </p>
        </section>

        <section className={styles.example}>
          <div className={styles.exampleHeading}>
            <Database size={22} aria-hidden="true" />
            <div>
              <h2>Prisma API example</h2>
              <p>
                Send a GET request to list users, or POST a name and email to
                create one.
              </p>
            </div>
          </div>

          <pre>
            <code>{`fetch("/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "Alex",
    email: "alex@example.com"
  })
});`}</code>
          </pre>

          <a className={styles.primary} href="/api/users">
            View users
            <ArrowRight size={16} aria-hidden="true" />
          </a>
        </section>
      </main>
    </div>
  );
}
