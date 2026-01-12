import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function POST(request: NextRequest) {
  try {
    // Try to get session (should return null for unauthenticated)
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    return NextResponse.json({
      success: true,
      hasSession: !!session,
      authConfigured: true,
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
    }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Just test that auth object is properly initialized
    return NextResponse.json({
      success: true,
      message: "Auth module loaded successfully",
      hasAuth: !!auth,
      hasApi: !!auth?.api,
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
    }, { status: 500 });
  }
}
