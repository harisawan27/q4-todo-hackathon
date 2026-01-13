import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { Pool } from "@neondatabase/serverless";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

/**
 * Get user's profile image
 * This endpoint exists to keep images OUT of session/JWT/cookies
 * to prevent REQUEST_HEADER_TOO_LARGE errors on Vercel
 */
export async function GET(request: NextRequest) {
  try {
    // Get the session
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.user?.id) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Fetch ONLY the image field from database
    const query = `
      SELECT image
      FROM "user"
      WHERE id = $1
    `;

    const result = await pool.query(query, [session.user.id]);

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({
      image: result.rows[0].image || null,
    });
  } catch (error) {
    console.error("Error fetching user image:", error);
    return NextResponse.json(
      { error: "Failed to fetch image" },
      { status: 500 }
    );
  }
}
