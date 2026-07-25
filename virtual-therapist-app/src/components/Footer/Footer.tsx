import {Home} from "lucide-react";
import styles from "./Footer.module.css";
import Spacer from "@/components/Spacer";
import LinkButton from "@/components/LinkButton/LinkButton";

export default function TopBar({ selectedPage }: { selectedPage: string }) {
    return(
        <div className={styles.footer}>
            <Spacer width={ 10 }/>
            <p>© 2026 Dr. Snickers. All rights reserved.</p>
        </div>
    )
}