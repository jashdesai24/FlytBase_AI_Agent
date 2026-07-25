"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowLeft, 
  Layers, 
  Search, 
  Users, 
  CheckCircle2, 
  FileText, 
  Mail, 
  Briefcase 
} from "lucide-react";

export default function AboutPage() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100 } }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-300 font-sans selection:bg-indigo-500/30">
      {/* Subtle grid background */}
      <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      
      {/* Soft gradient fade at top - VERY subtle, not "AI-ish" */}
      <div className="fixed top-0 left-0 right-0 h-[500px] bg-gradient-to-b from-zinc-800/10 to-transparent z-0 pointer-events-none blur-3xl"></div>

      <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto border-b border-white/5">
        <Link 
          href="/" 
          className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">Back to Home</span>
        </Link>
        <Link 
          href="/dashboard"
          className="px-4 py-2 rounded-md text-sm font-medium bg-white text-black hover:bg-zinc-200 transition-colors shadow-[0_0_15px_rgba(255,255,255,0.05)]"
        >
          Launch Console
        </Link>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-8 py-20 pb-32">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mb-24"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-400">
            <span className="flex h-2 w-2 rounded-full bg-zinc-500"></span>
            Architecture Overview
          </div>
          <h1 className="text-4xl md:text-5xl font-medium tracking-tight text-white mb-6 leading-tight">
            Built for determinism.<br className="hidden md:block"/>
            Powered by multi-agent orchestration.
          </h1>
          <p className="text-lg text-zinc-400 leading-relaxed">
            The FlytBase Inbound BDR pipeline leverages a Directed Acyclic Graph (DAG) of 7 specialized AI agents. Unlike a single monolithic prompt, this architecture ensures strict data contracts, allows parallel execution, and evaluates leads without LLM hallucination.
          </p>
        </motion.div>

        {/* Architecture Diagram */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-20 bg-[#121214] rounded-2xl border border-zinc-800/80 p-8 overflow-x-auto"
        >
          <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-6">Pipeline Flow</div>
          <div className="font-mono text-sm text-zinc-400 leading-loose whitespace-pre">
{`  ┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
  │  Inbound     │     │  Agent 2:        │     │                  │
  │  Lead Form   │────▶│  Account         │──┐  │  Agent 4:        │
  └─────────────┘     │  Research ⚡      │  ├─▶│  Qualification   │
         │            └──────────────────┘  │  │  & Scoring 🎯     │
         │                                  │  └────────┬─────────┘
         ▼            ┌──────────────────┐  │           │
  ┌─────────────┐     │  Agent 3:        │  │     ┌─────┴─────┐
  │  Agent 1:   │────▶│  Contact         │──┘     │ Qualified? │
  │  Intake &   │     │  Intelligence 👤 │        └─────┬─────┘
  │  Normalize  │     └──────────────────┘          YES │  NO
  └─────────────┘            ▲ parallel ▲               │   │
                                                        ▼   ▼
                      ┌──────────────────┐         ┌─────────────┐
                      │  Agent 5:        │◀────────│  Nurture    │
                      │  Case Study RAG  │         │  Sequence   │
                      └────────┬─────────┘         └─────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  Agent 6:        │
                      │  GTM + Email 📧  │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  Agent 7:        │
                      │  AE Handoff 📋   │
                      └──────────────────┘`}
          </div>
        </motion.div>

        <motion.div 
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {/* Bento Box Grid Items */}
          <motion.div variants={item} className="md:col-span-2 p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors">
            <Layers className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 1: Intake & Normalization</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Instantly parses unstructured or noisy lead data, enforcing strict typing via Pydantic schemas. It sets the baseline state for the rest of the DAG, ensuring all downstream agents receive standardized JSON payloads.
            </p>
          </motion.div>

          <motion.div variants={item} className="p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors">
            <Search className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 2: Live Research</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Executes autonomous web searches to capture real-time company intelligence and market positioning.
            </p>
          </motion.div>

          <motion.div variants={item} className="p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors">
            <Users className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 3: Contact Context</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Analyzes the lead's role and seniority to determine buying power and map out the broader decision-making committee.
            </p>
          </motion.div>

          <motion.div variants={item} className="md:col-span-2 p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors flex flex-col justify-center">
            <CheckCircle2 className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 4: Deterministic Scoring</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              We separate analysis from math. AI extracts signals from the research, but purely deterministic Python algorithms assign the final ICP score (A, B, C, D). This eliminates scoring hallucination entirely.
            </p>
          </motion.div>

          <motion.div variants={item} className="p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors">
            <FileText className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 5: Case Study RAG</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Uses semantic vector search across local ChromaDB to surface the most relevant past successes for the lead.
            </p>
          </motion.div>

          <motion.div variants={item} className="p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors">
            <Mail className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 6: Sequence Engine</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Drafts a highly personalized, context-aware 3-step email sequence referencing the matched case studies.
            </p>
          </motion.div>

          <motion.div variants={item} className="p-8 rounded-2xl bg-[#121214] border border-zinc-800/80 hover:border-zinc-700 transition-colors">
            <Briefcase className="w-5 h-5 text-zinc-400 mb-6" />
            <h3 className="text-lg font-medium text-white mb-2">Agent 7: AE Handoff</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Compiles all research, scoring logic, and drafted communications into a structured brief for the Account Executive.
            </p>
          </motion.div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mt-32 pt-8 border-t border-zinc-800/50 flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <div className="text-sm text-zinc-500">
            Engineered with LangGraph • Next.js • TailwindCSS
          </div>
          <div className="text-xs font-mono text-zinc-500 bg-zinc-900 px-3 py-1.5 rounded border border-zinc-800">
            Status: Production Ready
          </div>
        </motion.div>
      </main>
    </div>
  );
}
