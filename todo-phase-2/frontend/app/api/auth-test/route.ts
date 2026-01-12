import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { Pool } from "@neondatabase/serverless";

export async function POST(request: NextRequest) {
  const steps: Record<string, unknown> = {};

  try {
    // Step 1: Parse request body
    steps.step1_parseBody = "starting";
    const body = await request.json();
    steps.step1_parseBody = { success: true, hasEmail: !!body.email, hasPassword: !!body.password };

    // Step 2: Test database connection
    steps.step2_dbConnection = "starting";
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    const dbTest = await pool.query("SELECT 1 as test");
    steps.step2_dbConnection = { success: true, result: dbTest.rows[0] };

    // Step 3: Check if user exists
    steps.step3_userLookup = "starting";
    const userResult = await pool.query(
      'SELECT id, email, name FROM "user" WHERE email = $1',
      [body.email]
    );
    steps.step3_userLookup = {
      success: true,
      userFound: userResult.rows.length > 0,
      userCount: userResult.rows.length
    };

    // Step 4: Check account table
    steps.step4_accountLookup = "starting";
    if (userResult.rows.length > 0) {
      const accountResult = await pool.query(
        'SELECT id, "providerId" FROM "account" WHERE "userId" = $1',
        [userResult.rows[0].id]
      );
      steps.step4_accountLookup = {
        success: true,
        accountFound: accountResult.rows.length > 0,
        providerId: accountResult.rows[0]?.providerId
      };
    } else {
      steps.step4_accountLookup = { skipped: true, reason: "no user found" };
    }

    await pool.end();

    // Step 5: Try calling auth.api.signInEmail directly
    steps.step5_authSignIn = "starting";
    try {
      // Note: This won't work directly, but will show if auth is configured
      const signInResult = await auth.api.signInEmail({
        body: {
          email: body.email,
          password: body.password,
        },
      });
      steps.step5_authSignIn = { success: true, hasResult: !!signInResult };
    } catch (authError) {
      steps.step5_authSignIn = {
        success: false,
        error: authError instanceof Error ? authError.message : "Unknown error",
        stack: authError instanceof Error ? authError.stack?.split("\n").slice(0, 5) : undefined
      };
    }

    return NextResponse.json({ success: true, steps });
  } catch (error) {
    return NextResponse.json({
      success: false,
      steps,
      error: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack?.split("\n").slice(0, 10) : undefined,
    }, { status: 500 });
  }
}

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      message: "Auth module loaded successfully",
      hasAuth: !!auth,
      hasApi: !!auth?.api,
      methods: auth?.api ? Object.keys(auth.api).slice(0, 10) : [],
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
    }, { status: 500 });
  }
}
