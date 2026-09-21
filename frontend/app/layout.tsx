import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "R & A Agent — Research & Answer Agent",
  description: "A two-agent AI research pipeline with LangGraph, LiteLLM, and FastAPI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-background text-textPrimary selection:bg-accent/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}
