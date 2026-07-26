"use client";

import { Clipboard, ClipboardCheck } from "lucide-react";
import { useState } from "react";

export default function CopyButton({ text }: { text: string }) {
  const [state, setState] = useState<"copied" | "idle">("idle");
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setState("copied");
    setTimeout(() => setState("idle"), 2000);
  };

  return (
    <button
      aria-label="Copy phone number"
      className="copy-button"
      onClick={handleCopy}
      type="button"
    >
      {state === "copied" ? <ClipboardCheck /> : <Clipboard />}
    </button>
  );
}
