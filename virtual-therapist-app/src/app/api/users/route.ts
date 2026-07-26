import { authClient } from "@/lib/auth-client";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const users = await prisma.user.findMany({
    orderBy: {
      createdAt: "desc",
    },
  });

  return Response.json(users);
}

export async function POST(request: Request) {
  const body = (await request.json()) as {
    name?: string;
    phoneNumber?: string;
    password?: string;
  };

  if (!body.name || !body.phoneNumber || !body.password) {
    return Response.json(
      { error: "Name, phone number and password are all required." },
      { status: 400 },
    );
  }

  const { data, error } = await authClient.signUp.email({
    email: `${body.phoneNumber}@example.com`,
    password: body.password,
    name: body.name,
    phoneNumber: body.phoneNumber,
    callbackURL: "/dashboard",
  });

  if (error) {
    return Response.json({ error: error.message }, { status: error.status });
  }

  return Response.json(data, { status: 201 });
}
