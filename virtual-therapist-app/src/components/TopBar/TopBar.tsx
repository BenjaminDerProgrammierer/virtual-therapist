import {Home} from "lucide-react";
import styles from "./TopBar.module.css";
import Spacer from "@/components/Spacer";
import LinkButton from "@/components/LinkButton/LinkButton";

export default function TopBar() {
    return(
        <div className={styles.topBar}>
            <Spacer width={ 10 }/>
            <a href="/">
                <Home></Home>
            </a>
            <LinkButton text="Dashboard" link="/dashboard" selected={ false }/>
            <LinkButton text="Login" link={"/login"} selected={ false }/>
        </div>
    )
}