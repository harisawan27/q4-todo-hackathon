import type { Metadata, Viewport } from "next";
import { Providers } from "@/lib/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "TaskFlow - Organize Your Work, Simplify Your Life",
    template: "%s | TaskFlow",
  },
  description: "TaskFlow is a modern task management SaaS that helps you organize your work, track progress, and boost productivity. Free to get started.",
  keywords: ["task management", "productivity", "todo app", "project management", "SaaS", "collaboration"],
  authors: [{ name: "TaskFlow Team" }],
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
    ],
  },
  openGraph: {
    title: "TaskFlow - Modern Task Management",
    description: "Organize your work, simplify your life with TaskFlow",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
