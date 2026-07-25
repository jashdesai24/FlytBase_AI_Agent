"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { 
  Bot, User, Building2, Briefcase, Mail, Phone, MessageSquare, 
  Globe, Send, CheckCircle2, Loader2, FileText, BarChart3, 
  Target, GraduationCap, XCircle, ChevronRight, ArrowLeft,
  HardHat, Shield, Zap, UserMinus, AlertTriangle, Info
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type AgentState = "idle" | "running" | "completed" | "error";

interface ProcessState {
  intake: AgentState;
  research: AgentState;
  contact: AgentState;
  qualification: AgentState;
  case_study: AgentState;
  email: AgentState;
  handoff: AgentState;
}

const AGENTS = [
  { id: "intake", label: "Agent 1: Lead Intake & Normalization" },
  { id: "research", label: "Agent 2: Account Research" },
  { id: "contact", label: "Agent 3: Contact Intelligence" },
  { id: "qualification", label: "Agent 4: Qualification & Scoring" },
  { id: "case_study", label: "Agent 5: Case Study RAG" },
  { id: "email", label: "Agent 6: GTM & Email Generation" },
  { id: "handoff", label: "Agent 7: AE Handoff Briefing" },
];

export default function Dashboard() {
  const [formData, setFormData] = useState({
    first_name: "Sarah",
    last_name: "Chen",
    email: "sarah.chen@bhp.com",
    job_title: "VP Operations",
    company_name: "BHP",
    phone: "",
    message: "We're looking to scale our drone inspection program from 1 pilot site to 23 mine sites across Australia. Currently evaluating Skydio but concerned about vendor lock-in. Budget approved for FY2027.",
    page_visited: "pricing",
  });

  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [agentStates, setAgentStates] = useState<ProcessState>({
    intake: "idle",
    research: "idle",
    contact: "idle",
    qualification: "idle",
    case_study: "idle",
    email: "idle",
    handoff: "idle",
  });
  
  const [results, setResults] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("qualification");
  const [logs, setLogs] = useState<string[]>([]);
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const setDemoLead = (type: "mining" | "security" | "energy" | "lowfit") => {
    switch (type) {
      case "mining":
        setFormData({
          first_name: "Sarah", last_name: "Chen", email: "sarah.chen@bhp.com",
          job_title: "VP Operations", company_name: "BHP", phone: "",
          message: "We're looking to scale our drone inspection program from 1 pilot site to 23 mine sites across Australia. Currently evaluating Skydio but concerned about vendor lock-in. Budget approved for FY2027.",
          page_visited: "pricing"
        });
        break;
      case "security":
        setFormData({
          first_name: "James", last_name: "Rivera", email: "jrivera@securitas.com",
          job_title: "Director of Technology", company_name: "Securitas", phone: "",
          message: "Interested in autonomous drone patrols for our commercial security clients. Need 24/7 coverage for large industrial sites.",
          page_visited: "case-studies/mining"
        });
        break;
      case "energy":
        setFormData({
          first_name: "Hans", last_name: "Weber", email: "hans.weber@enel.com",
          job_title: "Director of Digital Innovation", company_name: "Enel Green Power", phone: "",
          message: "Exploring autonomous drone inspections for our solar farm portfolio across Europe. Currently using manual pilots.",
          page_visited: "product/fleet-management"
        });
        break;
      case "lowfit":
        setFormData({
          first_name: "Alex", last_name: "Kim", email: "alex@university.edu",
          job_title: "Research Student", company_name: "MIT", phone: "",
          message: "I'm writing a thesis on drone fleet management.",
          page_visited: "blog"
        });
        break;
    }
  };

  const processLead = async () => {
    setIsRunning(true);
    setResults(null);
    setLogs([]);
    setProgress(0);
    setPipelineError(null);
    setAgentStates({
      intake: "idle", research: "idle", contact: "idle", 
      qualification: "idle", case_study: "idle", email: "idle", handoff: "idle"
    });

    try {
      const res = await fetch(`${API_URL}/api/process-lead`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let finalState: any = {};
      let allLogs: string[] = [];

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // Keep the last (potentially incomplete) line in buffer
        buffer = lines.pop() || "";
        
        for (const line of lines) {
          if (line.startsWith("data:")) {
            const dataStr = line.slice(5).trim();
            if (!dataStr || dataStr === "{}") continue;
            
            try {
              const payload = JSON.parse(dataStr);
              const { node, output } = payload;
              
              // Accumulate execution logs (deltas from reducer)
              if (output.execution_log && Array.isArray(output.execution_log)) {
                allLogs = [...allLogs, ...output.execution_log];
                setLogs([...allLogs]);
              }

              // Merge other state fields (overwrite per key)
              const { execution_log, agent_errors, ...rest } = output;
              finalState = { ...finalState, ...rest };
              if (agent_errors) {
                finalState.agent_errors = { ...(finalState.agent_errors || {}), ...agent_errors };
              }
              
              // Update agent progress indicators
              setAgentStates(prev => {
                const next = { ...prev };
                const nodeIdx = AGENTS.findIndex(a => a.id === node);
                if (nodeIdx > 0) {
                   for (let i = 0; i < nodeIdx; i++) {
                     if (next[AGENTS[i].id as keyof ProcessState] !== "completed") {
                        next[AGENTS[i].id as keyof ProcessState] = "completed";
                     }
                   }
                }
                
                if (node === "end_disqualified") {
                  next.qualification = "completed";
                } else if (node in next) {
                  next[node as keyof ProcessState] = "running";
                  setProgress(Math.max(10, Math.floor(((nodeIdx + 1) / AGENTS.length) * 100)));
                }
                return next;
              });
              
            } catch (e) {
              console.error("Error parsing SSE JSON:", e, "line:", line);
            }
          }
        }
      }
      
      // Complete all running
      setAgentStates(prev => {
        const next = { ...prev };
        Object.keys(next).forEach(k => {
          if (next[k as keyof ProcessState] === "running") next[k as keyof ProcessState] = "completed";
        });
        return next;
      });
      setProgress(100);
      setResults(finalState);
      
    } catch (error: any) {
      console.error("Pipeline failed", error);
      const msg = error?.message || "Unknown error";
      if (msg.includes("Failed to fetch")) {
        setPipelineError("Cannot connect to backend. Make sure the FastAPI server is running on port 8000.");
      } else {
        setPipelineError(`Pipeline failed: ${msg}`);
      }
    } finally {
      setIsRunning(false);
    }
  };

  const getScoreColor = (grade: string) => {
    switch (grade) {
      case "A": return "text-emerald-400";
      case "B": return "text-blue-400";
      case "C": return "text-amber-400";
      case "D": return "text-rose-400";
      default: return "text-zinc-400";
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-300 font-sans selection:bg-zinc-800">
      
      {/* Navigation Header */}
      <nav className="border-b border-zinc-800/80 bg-[#09090b]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-zinc-500 hover:text-white transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="flex items-center gap-2 border-l border-zinc-800 pl-4">
              <div className="w-6 h-6 rounded border border-zinc-800 bg-[#121214] flex items-center justify-center">
                <Bot className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-medium text-white">Agentic BDR Console</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/about" className="text-sm text-zinc-500 hover:text-white transition-colors hidden sm:block">
              About
            </Link>
            <div className="text-xs font-mono text-zinc-500 bg-zinc-900 px-2 py-1 rounded border border-zinc-800">
              v2.0.1
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Sidebar / Left Column (5 cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Quick Demo Leads */}
            <div className="bg-[#121214] rounded-xl border border-zinc-800/80 overflow-hidden shadow-sm">
              <div className="px-5 py-4 border-b border-zinc-800/80 flex items-center gap-2">
                <Target className="w-4 h-4 text-zinc-400" />
                <h2 className="text-sm font-medium text-white">Quick Demo Scenarios</h2>
              </div>
              <div className="p-5 grid grid-cols-2 gap-3">
                <button onClick={() => setDemoLead('mining')} className="px-3 py-2 text-xs font-medium text-zinc-300 bg-[#09090b] hover:bg-zinc-800 hover:text-white rounded border border-zinc-800 transition-colors text-left flex items-center gap-2"><HardHat className="w-4 h-4 text-zinc-400" /> Mining VP</button>
                <button onClick={() => setDemoLead('security')} className="px-3 py-2 text-xs font-medium text-zinc-300 bg-[#09090b] hover:bg-zinc-800 hover:text-white rounded border border-zinc-800 transition-colors text-left flex items-center gap-2"><Shield className="w-4 h-4 text-zinc-400" /> Security</button>
                <button onClick={() => setDemoLead('energy')} className="px-3 py-2 text-xs font-medium text-zinc-300 bg-[#09090b] hover:bg-zinc-800 hover:text-white rounded border border-zinc-800 transition-colors text-left flex items-center gap-2"><Zap className="w-4 h-4 text-zinc-400" /> Energy Dir</button>
                <button onClick={() => setDemoLead('lowfit')} className="px-3 py-2 text-xs font-medium text-zinc-300 bg-[#09090b] hover:bg-zinc-800 hover:text-white rounded border border-zinc-800 transition-colors text-left flex items-center gap-2"><UserMinus className="w-4 h-4 text-zinc-400" /> Low-fit</button>
              </div>
            </div>

            {/* Lead Input Form */}
            <div className="bg-[#121214] rounded-xl border border-zinc-800/80 overflow-hidden shadow-sm">
               <div className="px-5 py-4 border-b border-zinc-800/80 flex items-center gap-2">
                <FileText className="w-4 h-4 text-zinc-400" />
                <h2 className="text-sm font-medium text-white">Raw Lead Data</h2>
              </div>
              <div className="p-5 space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-400">First Name</label>
                    <div className="relative">
                      <User className="w-4 h-4 absolute left-3 top-2.5 text-zinc-600" />
                      <input 
                        type="text" 
                        value={formData.first_name} 
                        onChange={e => setFormData({...formData, first_name: e.target.value})}
                        className="w-full bg-[#09090b] border border-zinc-800 rounded-md py-2 pl-9 pr-3 text-sm text-white focus:border-zinc-500 focus:outline-none transition-colors"
                      />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-400">Last Name</label>
                    <input 
                      type="text" 
                      value={formData.last_name} 
                      onChange={e => setFormData({...formData, last_name: e.target.value})}
                      className="w-full bg-[#09090b] border border-zinc-800 rounded-md py-2 px-3 text-sm text-white focus:border-zinc-500 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400">Email Address</label>
                  <div className="relative">
                    <Mail className="w-4 h-4 absolute left-3 top-2.5 text-zinc-600" />
                    <input 
                      type="email" 
                      value={formData.email} 
                      onChange={e => setFormData({...formData, email: e.target.value})}
                      className="w-full bg-[#09090b] border border-zinc-800 rounded-md py-2 pl-9 pr-3 text-sm text-white focus:border-zinc-500 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400">Job Title</label>
                  <div className="relative">
                    <Briefcase className="w-4 h-4 absolute left-3 top-2.5 text-zinc-600" />
                    <input 
                      type="text" 
                      value={formData.job_title} 
                      onChange={e => setFormData({...formData, job_title: e.target.value})}
                      className="w-full bg-[#09090b] border border-zinc-800 rounded-md py-2 pl-9 pr-3 text-sm text-white focus:border-zinc-500 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400">Company</label>
                  <div className="relative">
                    <Building2 className="w-4 h-4 absolute left-3 top-2.5 text-zinc-600" />
                    <input 
                      type="text" 
                      value={formData.company_name} 
                      onChange={e => setFormData({...formData, company_name: e.target.value})}
                      className="w-full bg-[#09090b] border border-zinc-800 rounded-md py-2 pl-9 pr-3 text-sm text-white focus:border-zinc-500 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400">Inbound Message</label>
                  <div className="relative">
                    <MessageSquare className="w-4 h-4 absolute left-3 top-3 text-zinc-600" />
                    <textarea 
                      value={formData.message} 
                      onChange={e => setFormData({...formData, message: e.target.value})}
                      rows={4}
                      className="w-full bg-[#09090b] border border-zinc-800 rounded-md py-2 pl-9 pr-3 text-sm text-white focus:border-zinc-500 focus:outline-none transition-colors resize-none"
                    />
                  </div>
                </div>

                <button 
                  onClick={processLead}
                  disabled={isRunning}
                  className="w-full flex items-center justify-center gap-2 bg-white hover:bg-zinc-200 text-black font-medium py-2.5 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                >
                  {isRunning ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
                  ) : (
                    <><Send className="w-4 h-4" /> Run Pipeline</>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Main Content / Right Column (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* Error Banner */}
            {pipelineError && (
              <div className="flex items-start gap-3 bg-rose-500/5 border border-rose-500/20 rounded-xl p-5">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-rose-300 mb-1">Pipeline Error</div>
                  <div className="text-sm text-zinc-400 leading-relaxed">{pipelineError}</div>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!isRunning && !results && !pipelineError && (
              <div className="h-full min-h-[400px] border border-zinc-800/50 border-dashed rounded-xl flex flex-col items-center justify-center text-center p-8 bg-[#121214]/30">
                <div className="w-12 h-12 bg-zinc-900 rounded-full flex items-center justify-center mb-4 border border-zinc-800">
                  <Bot className="w-6 h-6 text-zinc-500" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Ready to Process</h3>
                <p className="text-sm text-zinc-500 max-w-sm">
                  Select a demo lead or enter custom details in the sidebar, then run the pipeline to see the multi-agent system in action.
                </p>
              </div>
            )}

            {/* Pipeline Tracker */}
            {(isRunning || results) && (
              <div className="bg-[#121214] rounded-xl border border-zinc-800/80 overflow-hidden shadow-sm">
                <div className="px-5 py-4 flex justify-between items-center bg-[#09090b]/50">
                  <h2 className="text-sm font-medium text-white flex items-center gap-2">
                    Execution State
                  </h2>
                  <span className="text-xs font-mono text-zinc-400">
                    {progress}%
                  </span>
                </div>
                
                {/* Thin sleek progress bar */}
                <div className="h-0.5 w-full bg-zinc-900">
                  <div 
                    className="h-full bg-white transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                
                <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8">
                  {AGENTS.map((agent) => {
                    const state = agentStates[agent.id as keyof ProcessState];
                    return (
                      <div key={agent.id} className="flex items-center gap-3">
                        {state === "completed" ? (
                          <CheckCircle2 className="w-4 h-4 text-zinc-300 flex-shrink-0" />
                        ) : state === "running" ? (
                          <div className="w-4 h-4 rounded-full border-2 border-zinc-400 border-t-white animate-spin flex-shrink-0" />
                        ) : state === "error" ? (
                          <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                        ) : (
                          <div className="w-4 h-4 rounded-full border-2 border-zinc-800 flex-shrink-0" />
                        )}
                        <span className={`text-sm ${state === "running" ? "text-white font-medium animate-pulse" : state === "completed" ? "text-zinc-400" : "text-zinc-600"}`}>
                          {agent.label}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Execution Logs */}
                <div className="bg-[#09090b] border-t border-zinc-800/80 p-5 h-32 overflow-y-auto font-mono text-[11px] text-zinc-500 space-y-1.5 leading-relaxed">
                  {logs.length === 0 ? "Initializing agents..." : logs.map((log, i) => (
                    <div key={i} className="flex gap-3">
                      <span className="text-zinc-700 select-none">›</span>
                      <span>{log}</span>
                    </div>
                  ))}
                  <div ref={logEndRef} />
                </div>
              </div>
            )}

            {/* Results Area */}
            {results && results.qualification && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                
                {/* Score Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-[#121214] rounded-xl border border-zinc-800/80 p-6 flex flex-col justify-center relative overflow-hidden">
                    <div className="text-xs text-zinc-500 font-medium mb-3 uppercase tracking-wider">Lead Grade</div>
                    <div className={`text-5xl font-medium ${getScoreColor(results.qualification.grade)} tracking-tight`}>
                      {results.qualification.grade}
                    </div>
                  </div>
                  
                  <div className="bg-[#121214] rounded-xl border border-zinc-800/80 p-6 flex flex-col justify-center">
                    <div className="text-xs text-zinc-500 font-medium mb-3 uppercase tracking-wider">Total Score</div>
                    <div className="text-4xl font-medium text-white tracking-tight flex items-baseline gap-1">
                      {results.qualification.total_score} <span className="text-lg text-zinc-600 font-normal">/100</span>
                    </div>
                  </div>
                  
                  <div className="bg-[#121214] rounded-xl border border-zinc-800/80 p-6 flex flex-col justify-center">
                    <div className="text-xs text-zinc-500 font-medium mb-3 uppercase tracking-wider">Disposition</div>
                    {(results.qualification.disposition === 'qualified_hot' || results.qualification.disposition === 'qualified_warm') ? (
                      <div className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded text-sm font-medium w-fit">
                        <CheckCircle2 className="w-4 h-4" /> Qualified
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-2 bg-rose-500/10 text-rose-400 border border-rose-500/20 px-3 py-1.5 rounded text-sm font-medium w-fit">
                        <XCircle className="w-4 h-4" /> Disqualified
                      </div>
                    )}
                  </div>
                </div>

                {/* Tabs Area */}
                <div className="bg-[#121214] rounded-xl border border-zinc-800/80 overflow-hidden">
                  <div className="flex border-b border-zinc-800/80 overflow-x-auto hide-scrollbar bg-[#09090b]/50">
                    {['qualification', 'research', 'emails', 'handoff'].map((tab) => {
                      if (!(results.qualification.disposition === 'qualified_hot' || results.qualification.disposition === 'qualified_warm') && ['emails', 'handoff'].includes(tab)) {
                        return null;
                      }
                      return (
                        <button
                          key={tab}
                          onClick={() => setActiveTab(tab)}
                          className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap capitalize ${
                            activeTab === tab 
                              ? 'border-white text-white' 
                              : 'border-transparent text-zinc-500 hover:text-zinc-300 hover:border-zinc-700'
                          }`}
                        >
                          {tab}
                        </button>
                      )
                    })}
                  </div>

                  <div className="p-6">
                    {activeTab === 'qualification' && (
                      <div className="space-y-6">
                        <div className="space-y-3">
                          {results.qualification.scoring_breakdown && Object.entries(results.qualification.scoring_breakdown).map(([key, value]: [string, any]) => (
                            <div key={key} className="bg-[#09090b] rounded-lg p-4 border border-zinc-800 flex justify-between items-start md:items-center flex-col md:flex-row gap-4">
                              <div>
                                <div className="text-sm font-medium text-zinc-200 capitalize">{key.replace(/_/g, ' ')}</div>
                                <div className="text-xs text-zinc-500 mt-1 leading-relaxed">{value.reason}</div>
                              </div>
                              <div className="text-sm font-mono text-white bg-zinc-800 px-2.5 py-1 rounded border border-zinc-700 shrink-0">
                                +{value.value}<span className="text-zinc-500">/{value.max_value}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {activeTab === 'research' && results.account_research && (
                      <div className="space-y-6">
                        <div className="bg-[#09090b] rounded-lg p-5 border border-zinc-800">
                          <h4 className="text-sm text-zinc-300 font-medium mb-3">Company Profile</h4>
                          <div className="grid grid-cols-2 gap-3 text-sm">
                            <div><span className="text-zinc-500">Industry:</span> <span className="text-zinc-300 capitalize">{results.account_research.company_profile?.industry}</span></div>
                            <div><span className="text-zinc-500">Employees:</span> <span className="text-zinc-300">{results.account_research.company_profile?.employee_count?.toLocaleString() || 'Unknown'}</span></div>
                            <div><span className="text-zinc-500">HQ:</span> <span className="text-zinc-300">{results.account_research.company_profile?.hq_location || 'Unknown'}</span></div>
                            <div><span className="text-zinc-500">Revenue:</span> <span className="text-zinc-300">{results.account_research.company_profile?.revenue_estimate || 'Unknown'}</span></div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-[#09090b] rounded-lg p-5 border border-zinc-800">
                            <h4 className="text-sm text-zinc-300 font-medium mb-3">Pain Hypotheses</h4>
                            <ul className="space-y-2">
                              {results.account_research.pain_hypotheses?.map((p:any, i:number) => (
                                <li key={i} className="text-sm text-zinc-500 flex gap-2"><span className="text-zinc-700">-</span> <span>{p.pain} <span className="text-zinc-600">({(p.confidence * 100).toFixed(0)}% confidence)</span></span></li>
                              ))}
                            </ul>
                          </div>
                          <div className="bg-[#09090b] rounded-lg p-5 border border-zinc-800">
                            <h4 className="text-sm text-zinc-300 font-medium mb-3">Competitive Landscape</h4>
                            <ul className="space-y-2">
                              {results.account_research.strategic_context?.competitor_landscape?.map((p:string, i:number) => (
                                <li key={i} className="text-sm text-zinc-500 flex gap-2"><span className="text-zinc-700">-</span> <span>{p}</span></li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}

                    {activeTab === 'emails' && results.gtm_and_email && (
                      <div className="space-y-6">
                        <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                          <h3 className="text-sm font-medium text-zinc-300">Generated Outreach</h3>
                          <div className="text-xs text-zinc-500">
                            Strategy: <span className="text-zinc-300 font-medium">{results.gtm_and_email.gtm_decision?.motion}</span>
                          </div>
                        </div>
                        
                        <div className="space-y-6">
                          {results.gtm_and_email.email_sequence?.emails?.map((email: any, i: number) => (
                            <div key={i} className="bg-[#09090b] rounded-lg border border-zinc-800 overflow-hidden">
                              <div className="bg-zinc-900/50 px-5 py-3 border-b border-zinc-800 flex justify-between items-center">
                                <span className="text-xs font-medium text-zinc-400">Step {i + 1}: {email.goal}</span>
                              </div>
                              <div className="p-5">
                                <div className="text-sm font-medium text-zinc-200 mb-4 pb-4 border-b border-zinc-800">
                                  <span className="text-zinc-500 mr-2">Subject:</span> {email.subject}
                                </div>
                                <div className="text-sm text-zinc-400 whitespace-pre-wrap font-sans leading-relaxed">
                                  {email.body}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {activeTab === 'handoff' && results.handoff_brief && (
                      <div className="space-y-6">
                         
                         <div className="bg-[#09090b] rounded-lg p-6 border border-zinc-800">
                           <h4 className="text-sm font-medium text-zinc-300 mb-3">Summary</h4>
                           <p className="text-sm text-zinc-400 leading-relaxed">{results.handoff_brief.one_line_summary}</p>
                         </div>

                         <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            <div className="bg-[#09090b] rounded-lg p-6 border border-zinc-800">
                              <h4 className="text-sm font-medium text-zinc-300 mb-4">Strategic Talking Points</h4>
                              <ul className="space-y-3">
                                {results.handoff_brief.talking_points?.map((point:string, i:number) => (
                                  <li key={i} className="flex gap-3 text-sm text-zinc-400">
                                    <ChevronRight className="w-4 h-4 text-zinc-600 shrink-0 mt-0.5" /> 
                                    <span className="leading-relaxed">{point}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            
                            <div className="bg-[#09090b] rounded-lg p-6 border border-zinc-800">
                              <h4 className="text-sm font-medium text-zinc-300 mb-4">Objection Handlers</h4>
                              <ul className="space-y-4">
                                {results.handoff_brief.objection_handlers?.map((obj:any, i:number) => (
                                  <li key={i} className="text-sm border-l-2 border-zinc-800 pl-4">
                                    <div className="font-medium text-zinc-300 mb-1">"{obj.objection}"</div>
                                    <div className="text-zinc-500 leading-relaxed">{obj.response}</div>
                                  </li>
                                ))}
                              </ul>
                            </div>
                         </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
