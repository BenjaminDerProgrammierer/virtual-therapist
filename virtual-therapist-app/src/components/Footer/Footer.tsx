import Spacer from "@/components/Spacer";
import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <div className={styles.footer}>
      <Spacer width={10} />
      <p>© 2026 Dr. Snickers. All rights reserved.</p>
    </div>
  );
}
