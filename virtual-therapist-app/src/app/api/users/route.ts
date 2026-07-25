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
  };

  if (!body.name || !body.phoneNumber) {
    return Response.json(
      { error: "Both name and phone number are required." },
      { status: 400 },
    );
  }

  const user = await prisma.user.create({
    data: {
      name: body.name,
      phoneNumber: body.phoneNumber,
    },
  });

  return Response.json(user, { status: 201 });
}
