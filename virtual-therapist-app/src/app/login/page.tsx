"use client";

import { Lock, User } from "lucide-react";
import Form from "next/form";
import { toast } from "sonner";
import Spacer from "@/components/Spacer";
import TopBar from "@/components/TopBar/TopBar";
import { onSignIn } from "./actions";
import styles from "./page.module.css";

export default function Login() {
  return (
    <>
      <TopBar selectedPage={"/login"} />
      <main className={styles.main}>
        <div className={styles.card}>
          <h1 className={styles.bold}>Login</h1>
          <Spacer height={10} />

          <Form
            id="login-form"
            action={async (formData) => {
              try {
                await onSignIn(formData);
                toast.success("Logged in!");
              } catch (err) {
                toast.error(`Error while logging in: ${err}`);
              }
            }}
            className={styles.loginForm}
          >
            <div className={styles.loginField}>
              <User />
              <input
                name="phoneNumber"
                placeholder="Phone number"
                className={styles.searchInput}
              />
            </div>

            <div className={styles.loginField}>
              <Lock />
              <input
                name="accessCode"
                placeholder="Access code"
                className={styles.searchInput}
              />
            </div>
          </Form>

          <Spacer height={10} />
          <button
            type="submit"
            form="login-form"
            className={styles.submitButton}
          >
            Sign in
          </button>
        </div>
      </main>
    </>
  );
}
