"use client";

import { useSession } from "@/lib/auth-client";
import { ChatWidget } from "./chat-widget";

export function ChatWidgetWrapper() {
  const { data: session, isPending } = useSession();

  // Don't render chat widget while loading or if not authenticated
  if (isPending || !session?.user?.id) {
    return null;
  }

  return <ChatWidget userId={session.user.id} />;
}
