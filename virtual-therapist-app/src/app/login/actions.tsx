"use server";
import {GET} from "@/app/api/users/route";
import {redirect} from "next/navigation";

export async function onSignIn(formData: FormData) {
    'use server';
    const users = await GET()
    console.log(users);
    console.log(formData);
    redirect("/api/users")
}