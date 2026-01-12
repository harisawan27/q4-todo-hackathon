import { NextResponse } from "next/server";
import { Pool } from "@neondatabase/serverless";

export async function GET() {
  const results: Record<string, unknown> = {
    timestamp: new Date().toISOString(),
    env: {
      DATABASE_URL: process.env.DATABASE_URL ? "SET" : "NOT SET",
      BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET ? "SET" : "NOT SET",
      BETTER_AUTH_URL: process.env.BETTER_AUTH_URL || "NOT SET",
    },
    database: {
      connection: "UNTESTED",
      tables: {},
    },
  };

  // Test database connection
  try {
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });

    // Test connection
    const connTest = await pool.query("SELECT NOW() as time");
    results.database = {
      connection: "OK",
      serverTime: connTest.rows[0]?.time,
      tables: {},
    };

    // Check if Better Auth tables exist
    const tables = ["user", "session", "account", "verification", "jwks"];
    const tableResults: Record<string, string> = {};

    for (const table of tables) {
      try {
        const result = await pool.query(
          `SELECT COUNT(*) as count FROM "${table}"`
        );
        tableResults[table] = `EXISTS (${result.rows[0]?.count} rows)`;
      } catch (e) {
        tableResults[table] = `MISSING: ${e instanceof Error ? e.message : "unknown error"}`;
      }
    }

    (results.database as Record<string, unknown>).tables = tableResults;

    await pool.end();
  } catch (error) {
    results.database = {
      connection: "FAILED",
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }

  return NextResponse.json(results);
}
