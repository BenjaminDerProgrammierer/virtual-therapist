import TopBar from "@/components/TopBar/TopBar";
import styles from "./page.module.css";

export default function Dashboard() {
  return (
    <>
      <TopBar selectedPage="/dashboard"/>
      <main className={styles.main}>

      </main>
    </>
  );
}
