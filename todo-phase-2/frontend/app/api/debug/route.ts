import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    timestamp: new Date().toISOString(),
    env: {
      DATABASE_URL: process.env.DATABASE_URL ? "SET" : "NOT SET",
      BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET ? "SET" : "NOT SET",
      BETTER_AUTH_URL: process.env.BETTER_AUTH_URL || "NOT SET",
    },
  });
}
