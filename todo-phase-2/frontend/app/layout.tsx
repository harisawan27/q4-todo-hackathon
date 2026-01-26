import type { Metadata, Viewport } from "next";
import { Analytics } from "@vercel/analytics/next";
import { Providers } from "@/lib/providers";
import { ChatWidgetWrapper } from "@/components/chat-widget-wrapper";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "DoneKaro - Organize Your Work, Simplify Your Life",
    template: "%s | DoneKaro",
  },
  description: "DoneKaro is a modern task management SaaS that helps you organize your work, track progress, and boost productivity. Free to get started.",
  keywords: ["task management", "productivity", "todo app", "project management", "SaaS", "collaboration"],
  authors: [{ name: "DoneKaro Team" }],
  icons: {
    icon: [
      { url: "/logo.svg", type: "image/svg+xml" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon.ico", sizes: "any" },
    ],
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
  openGraph: {
    title: "DoneKaro - Modern Task Management",
    description: "Organize your work, simplify your life with DoneKaro",
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
        <Providers>
          {children}
          <ChatWidgetWrapper />
        </Providers>
        <Analytics />
      </body>
    </html>
  );
}
