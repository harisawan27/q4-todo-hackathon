import { NextRequest, NextResponse } from "next/server";
import { Pool } from "@neondatabase/serverless";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

/**
 * Emergency endpoint to clear all user profile images
 * This fixes the "Request headers too large" error caused by base64 images in JWT tokens
 *
 * This endpoint doesn't require auth since users can't log in when headers are too large
 */
export async function POST(request: NextRequest) {
  try {
    // Optional: accept email in body to target specific user
    const body = await request.json().catch(() => ({}));
    const { email } = body;

    let query: string;
    let values: string[] = [];

    if (email) {
      // Clear specific user's image
      query = `
        UPDATE "user"
        SET image = NULL, "updatedAt" = CURRENT_TIMESTAMP
        WHERE email = $1
        RETURNING email
      `;
      values = [email];
    } else {
      // Clear all users' images (nuclear option)
      query = `
        UPDATE "user"
        SET image = NULL, "updatedAt" = CURRENT_TIMESTAMP
        WHERE image IS NOT NULL
        RETURNING email
      `;
    }

    const result = await pool.query(query, values);

    return NextResponse.json({
      success: true,
      message: `Cleared profile images for ${result.rows.length} user(s)`,
      affectedEmails: result.rows.map((row) => row.email),
    });
  } catch (error) {
    console.error("Error clearing images:", error);
    return NextResponse.json(
      { error: "Failed to clear images" },
      { status: 500 }
    );
  }
}
