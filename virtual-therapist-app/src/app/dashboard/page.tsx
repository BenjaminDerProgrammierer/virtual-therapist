import TopBar from "@/components/TopBar/TopBar";
import styles from "./page.module.css";

export default function Dashboard() {
  return (
    <>
      <TopBar selectedPage="/dashboard" />
      <main className={styles.main}>
        <h1>Dashboard</h1>
        <div className={styles.container}>
          <section className={styles.conversationHistory}>
            <h2>Conversation history</h2>
            <p>
              User: Testing 1 2 3<br />
              Dr. Snickers: Testing 4 5 6
            </p>
          </section>
          <section className={styles.memory}>
            <h2>Memory</h2>
            <p>
              - Testing 1 2 3<br />- Testing 4 5 6
            </p>
          </section>
        </div>
      </main>
    </>
  );
}
