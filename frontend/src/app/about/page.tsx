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
  Briefcase,
  ArrowDown,
  ArrowRight,
  GitBranch,
  Zap,
  Bot,
  Database,
  Sparkles,
  ShieldCheck,
  XCircle,
  Share2
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
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 100 } }
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
        {/* Modern Architecture Flow Diagram */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-24 space-y-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-zinc-800/80 gap-2">
            <div>
              <h2 className="text-2xl font-medium text-white tracking-tight flex items-center gap-2">
                <Share2 className="w-5 h-5 text-zinc-400" />
                LangGraph Execution Pipeline
              </h2>
              <p className="text-sm text-zinc-500 mt-1">Real-time modular orchestration across 7 intelligent BDR micro-agents</p>
            </div>
            <span className="text-xs font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-3 py-1.5 rounded-full w-fit flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
              Parallel DAG Workflow
            </span>
          </div>

          <div className="bg-[#101012] border border-zinc-800/80 rounded-2xl p-6 lg:p-10 relative overflow-hidden">
            {/* Ambient glows inside box */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

            <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
              
              {/* Step 1: Input & Intake */}
              <div className="w-full sm:w-80 bg-[#161619] border border-zinc-700/60 rounded-xl p-5 shadow-lg text-center relative hover:border-zinc-500 transition-colors">
                <div className="w-9 h-9 bg-zinc-800/80 border border-zinc-700 rounded-lg flex items-center justify-center mx-auto mb-3 text-white">
                  <Bot className="w-5 h-5 text-indigo-400" />
                </div>
                <div className="text-xs font-mono text-zinc-500 mb-1">AGENT 01</div>
                <h3 className="text-base font-medium text-white">Lead Intake & Normalization</h3>
                <p className="text-xs text-zinc-400 mt-2 leading-relaxed">Parses raw form inputs into standardized schema & validates emails</p>
              </div>

              {/* Connector Arrow */}
              <div className="flex flex-col items-center my-3 text-zinc-600">
                <div className="w-0.5 h-6 bg-gradient-to-b from-zinc-700 to-zinc-600"></div>
                <ArrowDown className="w-4 h-4 -mt-1 text-zinc-500" />
              </div>

              {/* Parallel Processing Badge */}
              <div className="bg-zinc-900/90 border border-zinc-700/80 text-zinc-300 text-xs px-3.5 py-1 rounded-full font-mono flex items-center gap-2 mb-4 shadow-sm">
                <GitBranch className="w-3.5 h-3.5 text-amber-400 rotate-180" />
                <span>Simultaneous Execution</span>
              </div>

              {/* Step 2 & 3: Parallel Agents */}
              <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-4 my-2 relative">
                {/* Connecting branch lines for Desktop */}
                <div className="hidden md:block absolute -top-4 left-1/4 right-1/4 h-4 border-t border-x border-zinc-700/60 rounded-t-xl z-0"></div>

                <div className="bg-[#161619] border border-zinc-700/60 rounded-xl p-5 shadow-lg hover:border-zinc-500 transition-colors z-10 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono text-zinc-500">AGENT 02</span>
                      <span className="text-[11px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono flex items-center gap-1">
                        <Zap className="w-3 h-3" /> Live Web Search
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <Search className="w-5 h-5 text-blue-400" />
                      <h3 className="text-base font-medium text-white">Account Research</h3>
                    </div>
                    <p className="text-xs text-zinc-400 leading-relaxed">Runs real-time web search via Tavily to build comprehensive profile, news & pain hypotheses.</p>
                  </div>
                </div>

                <div className="bg-[#161619] border border-zinc-700/60 rounded-xl p-5 shadow-lg hover:border-zinc-500 transition-colors z-10 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono text-zinc-500">AGENT 03</span>
                      <span className="text-[11px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
                        Persona Matrix
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-5 h-5 text-purple-400" />
                      <h3 className="text-base font-medium text-white">Contact Intelligence</h3>
                    </div>
                    <p className="text-xs text-zinc-400 leading-relaxed">Analyzes buyer job title, seniority hierarchy, responsibilities, and decision-making authority.</p>
                  </div>
                </div>

                <div className="hidden md:block absolute -bottom-4 left-1/4 right-1/4 h-4 border-b border-x border-zinc-700/60 rounded-b-xl z-0"></div>
              </div>

              {/* Connector Arrow */}
              <div className="flex flex-col items-center mt-5 mb-3 text-zinc-600">
                <div className="w-0.5 h-6 bg-gradient-to-b from-zinc-700 to-zinc-600"></div>
                <ArrowDown className="w-4 h-4 -mt-1 text-zinc-500" />
              </div>

              {/* Step 4: Qualification & Deterministic Scoring */}
              <div className="w-full sm:w-96 bg-[#161619] border-2 border-emerald-500/30 rounded-xl p-6 shadow-lg text-center relative hover:border-emerald-500/60 transition-colors">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-emerald-500 text-black text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full">
                  Deterministic Core
                </div>
                <div className="w-10 h-10 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center justify-center mx-auto my-2">
                  <ShieldCheck className="w-6 h-6 text-emerald-400" />
                </div>
                <div className="text-xs font-mono text-zinc-500 mb-1">AGENT 04</div>
                <h3 className="text-lg font-medium text-white">Qualification & Lead Scoring</h3>
                <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
                  Calculates 0-100 score & letter grade using pure Python evaluation rules. Zero LLM score hallucination.
                </p>
              </div>

              {/* Decision Branch */}
              <div className="w-full max-w-2xl mt-6 pt-6 border-t border-dashed border-zinc-800 flex flex-col sm:flex-row items-stretch sm:items-start justify-between gap-6">
                
                {/* Left Branch: Qualified (Score >= 40) */}
                <div className="flex-1 flex flex-col items-center bg-emerald-950/10 border border-emerald-500/20 rounded-xl p-5">
                  <div className="inline-flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-medium mb-4">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Score ≥ 40: Qualified Pipeline
                  </div>
                  
                  <div className="space-y-3 w-full">
                    <div className="bg-[#161619] border border-zinc-800 p-3.5 rounded-lg flex items-center gap-3">
                      <div className="p-2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
                        <Database className="w-4 h-4" />
                      </div>
                      <div className="text-left">
                        <div className="text-[11px] font-mono text-zinc-500">AGENT 05</div>
                        <div className="text-xs font-medium text-white">Case Study RAG Retrieval</div>
                      </div>
                    </div>

                    <div className="flex justify-center"><ArrowDown className="w-3.5 h-3.5 text-zinc-600" /></div>

                    <div className="bg-[#161619] border border-zinc-800 p-3.5 rounded-lg flex items-center gap-3">
                      <div className="p-2 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 shrink-0">
                        <Mail className="w-4 h-4" />
                      </div>
                      <div className="text-left">
                        <div className="text-[11px] font-mono text-zinc-500">AGENT 06</div>
                        <div className="text-xs font-medium text-white">GTM Routing & Email Generation</div>
                      </div>
                    </div>

                    <div className="flex justify-center"><ArrowDown className="w-3.5 h-3.5 text-zinc-600" /></div>

                    <div className="bg-gradient-to-r from-emerald-900/30 to-[#161619] border border-emerald-500/40 p-3.5 rounded-lg flex items-center gap-3 shadow-md">
                      <div className="p-2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">
                        <Briefcase className="w-4 h-4" />
                      </div>
                      <div className="text-left">
                        <div className="text-[11px] font-mono text-zinc-400">AGENT 07</div>
                        <div className="text-xs font-medium text-white">Account Executive Handoff Brief</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Branch: Disqualified (Score < 40) */}
                <div className="w-full sm:w-64 flex flex-col items-center bg-rose-950/10 border border-rose-500/20 rounded-xl p-5 text-center">
                  <div className="inline-flex items-center gap-1.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 px-3 py-1 rounded text-xs font-medium mb-4">
                    <XCircle className="w-3.5 h-3.5" /> Score &lt; 40: Disqualified
                  </div>
                  <p className="text-xs text-zinc-400 mb-4 leading-relaxed">
                    Lead misses ideal customer profile requirements. Exits expensive AE loop automatically.
                  </p>
                  <div className="bg-[#161619] border border-rose-500/20 p-3.5 rounded-lg w-full text-zinc-300 text-xs font-medium flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4 text-rose-400" />
                    Route to Auto-Nurture
                  </div>
                </div>
              </div>

            </div>
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
