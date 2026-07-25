import {Lock, User} from "lucide-react";
import styles from "./page.module.css";
import Spacer from "@/components/Spacer";
import Form from "next/form";
import {onSignIn} from "@/app/login/actions";


export default function Login() {
    return (
        <>
            <main className={styles.main}>
                <div className={styles.card}>
                    <h1 className={styles.bold}>Login</h1>
                    <Spacer height={10}/>
                    <Form id="login-form" action={onSignIn} className={styles.loginForm}>
                        <div className={styles.loginField}>
                            <User></User>
                            <input name="phoneNumber" placeholder="Phone number" className={styles.searchInput}/>
                        </div>
                        <div className={styles.loginField}>
                            <Lock></Lock>
                            <input name="accesCode" placeholder="Access code" className={styles.searchInput}/>
                        </div>
                    </Form>
                    <Spacer height={10}/>
                    <button type="submit" form="login-form" className={styles.submitButton}>
                        Sign in
                    </button>
                </div>
            </main>
        </>
    );
}
