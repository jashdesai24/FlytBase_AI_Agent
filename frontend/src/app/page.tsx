"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Brain, Zap, Target, Database, Workflow, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 100 },
    },
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-300 overflow-hidden relative selection:bg-zinc-800">
      
      {/* Subtle Grid Background */}
      <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      
      {/* Soft gradient fade at top - VERY subtle */}
      <div className="fixed top-0 left-0 right-0 h-[500px] bg-gradient-to-b from-zinc-800/10 to-transparent z-0 pointer-events-none blur-3xl"></div>

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto border-b border-white/5">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-2"
        >
          <div className="w-8 h-8 rounded border border-zinc-800 bg-zinc-900 flex items-center justify-center shadow-sm">
            <Brain className="w-4 h-4 text-zinc-300" />
          </div>
          <span className="text-lg font-medium text-white tracking-tight">
            FlytBase AI
          </span>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-6"
        >
          <Link 
            href="/about"
            className="text-sm font-medium text-zinc-400 hover:text-white transition-colors"
          >
            About
          </Link>
          <Link 
            href="/dashboard"
            className="px-4 py-2 rounded-md text-sm font-medium bg-white text-black hover:bg-zinc-200 transition-colors shadow-[0_0_15px_rgba(255,255,255,0.05)]"
          >
            Launch Console
          </Link>
        </motion.div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-4 pt-28 pb-32 text-center max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-400 shadow-sm"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-zinc-400 opacity-50"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-zinc-500"></span>
          </span>
          Agentic BDR Pipeline v2.0
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl md:text-7xl font-medium tracking-tight mb-6 leading-tight text-white"
        >
          Automate your <br className="hidden md:block"/>
          Inbound Sales.
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl leading-relaxed"
        >
          A deterministic multi-agent LangGraph pipeline that autonomously researches accounts, qualifies leads, retrieves case studies, and drafts personalized GTM outreach.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Link 
            href="/dashboard"
            className="group flex items-center justify-center gap-2 px-6 py-3 bg-white text-black rounded-lg font-medium text-sm hover:bg-zinc-200 transition-colors shadow-sm"
          >
            Start Processing Leads
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link 
            href="/about"
            className="flex items-center justify-center gap-2 px-6 py-3 bg-[#121214] border border-zinc-800 text-white rounded-lg font-medium text-sm hover:bg-zinc-900 transition-colors"
          >
            View Architecture
          </Link>
        </motion.div>
      </main>

      {/* Features Grid */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 pb-32">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {[
            {
              icon: <Zap className="w-5 h-5 text-zinc-400" />,
              title: "Instant Normalization",
              desc: "Cleans and normalizes lead data using LLM extraction to ensure pristine CRM records."
            },
            {
              icon: <Target className="w-5 h-5 text-zinc-400" />,
              title: "Deep Account Research",
              desc: "Autonomous web agents crawl for technographics, drone usage, and BVLOS signals."
            },
            {
              icon: <Database className="w-5 h-5 text-zinc-400" />,
              title: "Case Study RAG",
              desc: "Vector-searches FlytBase's knowledge base to match the exact industry use case."
            },
            {
              icon: <Brain className="w-5 h-5 text-zinc-400" />,
              title: "Smart Qualification",
              desc: "Scores leads based on ideal customer profile matching and strategic context."
            },
            {
              icon: <Workflow className="w-5 h-5 text-zinc-400" />,
              title: "Parallel Execution",
              desc: "Built on LangGraph. Agents execute concurrently with robust state management."
            },
            {
              icon: <ShieldCheck className="w-5 h-5 text-zinc-400" />,
              title: "AE Handoff Briefs",
              desc: "Synthesizes all intelligence into a succinct, actionable briefing for Account Executives."
            }
          ].map((feature, i) => (
            <motion.div 
              key={i}
              variants={itemVariants}
              className="p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors"
            >
              <div className="mb-6">
                {feature.icon}
              </div>
              <h3 className="text-lg font-medium text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                {feature.desc}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 border-t border-zinc-800/50 py-8 mt-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-xs text-zinc-500">
            Built with LangGraph · Gemini · Tavily · ChromaDB · Next.js
          </div>
          <div className="text-xs text-zinc-600">
            7 Agents · Deterministic Scoring · Semantic RAG · SSE Streaming
          </div>
        </div>
      </footer>

    </div>
  );
}
