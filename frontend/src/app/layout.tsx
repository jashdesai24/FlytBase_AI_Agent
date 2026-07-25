import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "FlytBase Inbound BDR AI Agent",
  description: "Agentic multi-agent BDR pipeline that autonomously researches accounts, qualifies leads, retrieves case studies, and drafts personalized GTM outreach.",
  keywords: ["BDR", "AI Agent", "LangGraph", "Lead Qualification", "FlytBase", "Sales Automation"],
  openGraph: {
    title: "FlytBase Inbound BDR AI Agent",
    description: "7 Specialized AI Agents · Deterministic Scoring · Real-Time Research · Semantic RAG",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>" />
      </head>
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
