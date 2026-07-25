import styles from "./LinkButton.module.css";

export default function LinkButton({ text, link, selected }: { text: string, link: string, selected: boolean }) {
    if(selected)
        return (
            <u className={styles.linkButton}>
                <b><a href={link}>{text}</a></b>
            </u>
        )
    else
        return (
            <div className={styles.linkButton}>
                <a href={link}>{text}</a>
            </div>
        )
}