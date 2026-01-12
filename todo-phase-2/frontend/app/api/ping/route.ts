import { NextRequest, NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ method: "GET", status: "ok", timestamp: Date.now() });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return NextResponse.json({
      method: "POST",
      status: "ok",
      received: body,
      timestamp: Date.now()
    });
  } catch (error) {
    return NextResponse.json({
      method: "POST",
      status: "error",
      error: error instanceof Error ? error.message : "Unknown"
    }, { status: 400 });
  }
}
