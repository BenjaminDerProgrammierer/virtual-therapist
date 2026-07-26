import TopBar from "@/components/TopBar/TopBar";
import styles from "./page.module.css";
import { prisma } from "@/lib/prisma";
import { User, Bot } from "lucide-react";

export default async function Dashboard() {
  const messages = await prisma.message.findMany();
  const memory = (await prisma.user.findMany()).map((u) => u.memory).join("\n");
  return (
    <>
      <TopBar selectedPage="/dashboard" />
      <main className={styles.main}>
        <h1>Dashboard</h1>
        <div className={styles.container}>
          <section className={styles.conversationHistory}>
            <h2>Conversation history</h2>
            <div>
              {messages.map((m) => {
                return (
                  <div key={m.id}>
                    {m.role == "user" ? <User /> : <Bot />} {m.content}
                  </div>
                );
              })}
            </div>
          </section>
          <section className={styles.memory}>
            <h2>Memory</h2>
            <p style={{ whiteSpace: "pre-wrap" }}>{memory}</p>
          </section>
        </div>
      </main>
    </>
  );
}
