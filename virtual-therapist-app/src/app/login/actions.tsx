"use server";
import {redirect} from "next/navigation";
import {prisma} from "@/lib/prisma";

async function getUsers() {
    return await prisma.user.findMany({
        orderBy: {
            createdAt: "desc",
        },
    });
}

export async function onSignIn(formData: FormData) {
    'use server';
    const users = await getUsers();
    const enteredPhone = formData.get("phoneNumber") as string;
    const enteredCode = formData.get("accessCode") as string;
    const userExists = users.find(item => item.phone_number == enteredPhone && item.access_code == enteredCode);
    console.log(userExists);
    redirect("/api/users")
}