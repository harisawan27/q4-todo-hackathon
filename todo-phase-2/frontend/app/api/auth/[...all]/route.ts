import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest, NextResponse } from "next/server";

const handler = toNextJsHandler(auth);

export async function GET(request: NextRequest) {
  try {
    console.log("[Auth API] GET request:", request.nextUrl.pathname);
    return await handler.GET(request);
  } catch (error) {
    console.error("[Auth API] GET error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log("[Auth API] POST request:", request.nextUrl.pathname);
    console.log("[Auth API] Origin:", request.headers.get("origin"));
    return await handler.POST(request);
  } catch (error) {
    console.error("[Auth API] POST error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
