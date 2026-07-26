import { authClient } from "@/lib/auth-client";

export async function onSignIn(formData: FormData) {
  const enteredPhone = String(formData.get("phoneNumber") ?? "");
  const enteredCode = String(formData.get("accessCode") ?? "");

  const { error } = await authClient.signIn.phoneNumber({
    phoneNumber: enteredPhone,
    password: enteredCode,
    rememberMe: true,
  });

  if (error) throw error;


  return true;
}
