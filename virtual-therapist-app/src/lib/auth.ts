import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { phoneNumber } from "better-auth/plugins";
import { prisma } from "@/lib/prisma";

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  emailAndPassword: {
    enabled: true,
  },
  advanced: {
    database: {
      generateId: (options) => {
        if (options.model === "user") {
          return false;
        }
        return crypto.randomUUID();
      },
    },
  },
  plugins: [
    phoneNumber({
      sendOTP: async () => {
        throw new Error("SMS delivery is not configured.");
      },
    }),
  ],
});
