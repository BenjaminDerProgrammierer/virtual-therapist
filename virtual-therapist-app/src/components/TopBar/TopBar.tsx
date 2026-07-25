import {Home} from "lucide-react";
import styles from "./TopBar.module.css";
import Spacer from "@/components/Spacer";
import LinkButton from "@/components/LinkButton/LinkButton";

export default function TopBar({ selectedPage }: { selectedPage: string }) {
    return(
        <div className={styles.topBar}>
            <Spacer width={ 10 }/>
            <LinkButton text="Home" link="/" selected={ selectedPage == "/" }/>
            <LinkButton text="Dashboard" link="/dashboard" selected={ selectedPage == "/dashboard" }/>
            <LinkButton text="Login" link={"/login"} selected={ selectedPage == "/login" }/>
        </div>
    )
}