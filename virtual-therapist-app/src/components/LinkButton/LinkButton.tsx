import { DetailedHTMLProps, HTMLAttributes } from "react";
import styles from "./LinkButton.module.css";

export default function LinkButton({
  text,
  link,
  selected,
  ...props
}: {
  text: string;
  link: string;
  selected: boolean;
} & DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement>) {
  if (selected)
    return (
      <u className={styles.linkButton} {...props}>
        <b>
          <a href={link}>{text}</a>
        </b>
      </u>
    );
  else
    return (
      <div className={styles.linkButton} {...props}>
        <a href={link}>{text}</a>
      </div>
    );
}
