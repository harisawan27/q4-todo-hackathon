import { auth } from "@/lib/auth";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { idToken } = body;

    if (!idToken) {
      return NextResponse.json(
        { error: "Missing ID token" },
        { status: 400 }
      );
    }

    // Use better-auth's signInWithIdToken for social providers
    const result = await auth.api.signInSocial({
      body: {
        provider: "google",
        idToken: {
          token: idToken,
        },
      },
      headers: request.headers,
    });

    // Convert the result to a proper NextResponse
    if (result && typeof result === 'object') {
      if ('redirect' in result && result.redirect) {
        return NextResponse.json({
          success: true,
          redirect: result.url,
          user: 'user' in result ? result.user : null,
        });
      }
      return NextResponse.json({ success: true, ...result });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Native Google auth error:", error);
    return NextResponse.json(
      { error: "Authentication failed" },
      { status: 500 }
    );
  }
}
