"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, AlertTriangle } from "lucide-react";
import ReportView, { FullAssessmentResponse } from "@/components/ReportView";
import ResearchLog from "@/components/ResearchLog";
import LivePreview from "@/components/LivePreview";

function ReportContent() {
    const searchParams = useSearchParams();
    const companyQuery = searchParams.get("company");
    const addressQuery = searchParams.get("address"); // Legacy fallback
    const stateQuery = searchParams.get("state");
    const typeQuery = searchParams.get("type");

    const [data, setData] = useState<FullAssessmentResponse | null>(null);
    const [logs, setLogs] = useState<any[]>([]);
    const [agents, setAgents] = useState<Record<string, any>>({}); // Multi-agent state
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showLogs, setShowLogs] = useState(false);

    useEffect(() => {
        if (!companyQuery) return;

        const fetchData = async () => {
            setLoading(true);
            setError("");
            setLogs([]);
            setAgents({});
            setSummary("");
            setData(null);
            setShowLogs(false); // Reset logs visibility on new search

            try {
                // Construct payload
                const payload = {
                    companyName: companyQuery,
                    companyAddress: addressQuery || stateQuery || "Unknown",
                    state: stateQuery || "Unknown",
                    companyType: typeQuery || "other"
                };

                const response = await fetch("http://localhost:8000/api/assess", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.body) throw new Error("No response body");

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n");
                    buffer = lines.pop() || "";

                    for (const line of lines) {
                        if (!line.trim()) continue;
                        if (line.startsWith("data: ")) {
                            try {
                                const msg = JSON.parse(line.slice(6));
                                if (msg.type === "log") {
                                    setLogs(prev => [...prev, { ...msg, timestamp: Date.now() }]);
                                } else if (msg.type === "preview") {
                                    // Update specific agent state
                                    setAgents(prev => ({
                                        ...prev,
                                        [msg.agent_id]: {
                                            id: msg.agent_id,
                                            url: msg.url,
                                            image: msg.image,
                                            status: msg.status || "Active",
                                            lastUpdate: Date.now()
                                        }
                                    }));
                                } else if (msg.type === "summary") {
                                    setSummary(prev => prev + msg.content);
                                } else if (msg.type === "result") {
                                    setData(msg.data);
                                    setLoading(false);
                                } else if (msg.type === "error") {
                                    setError(msg.message);
                                    setLoading(false);
                                }
                            } catch (e) {
                                console.error("Error parsing stream:", e);
                            }
                        }
                    }
                }
            } catch (err) {
                console.error(err);
                setError("Failed to generate risk assessment. Please try again.");
                setLoading(false);
            }
        };

        fetchData();
    }, [companyQuery, addressQuery, stateQuery, typeQuery]);

    if (!companyQuery) {
        return <div className="text-white text-center mt-20">No company specified.</div>;
    }

    if (loading || !data) {
        return (
            <div className="min-h-[80vh] flex flex-col items-center justify-center p-4">
                <div className="w-full max-w-7xl relative">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-3xl font-bold gradient-text">
                            Analyzing {companyQuery}
                        </h2>
                        <button
                            onClick={() => setShowLogs(!showLogs)}
                            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-sm font-mono transition-colors flex items-center gap-2"
                        >
                            {showLogs ? "Hide Logs" : "Show Logs"}
                            <span className="bg-slate-900 px-1.5 py-0.5 rounded text-xs text-slate-500">{logs.length}</span>
                        </button>
                    </div>

                    <div className="flex gap-8">
                        {/* Live Preview Column (Main Stage) */}
                        <div className={`transition-all duration-500 ease-in-out ${showLogs ? 'w-2/3' : 'w-full'}`}>
                            <div className="sticky top-8 space-y-6">
                                <LivePreview
                                    agents={agents}
                                    isActive={loading}
                                />
                            </div>
                        </div>

                        {/* Logs Column (Sidebar) */}
                        <div className={`transition-all duration-500 ease-in-out overflow-hidden ${showLogs ? 'w-1/3 opacity-100' : 'w-0 opacity-0'}`}>
                            <div className="w-full">
                                <ResearchLog logs={logs} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-[80vh] space-y-4 text-red-400">
                <AlertTriangle className="w-12 h-12" />
                <h2 className="text-2xl font-semibold">{error}</h2>
            </div>
        );
    }

    return <ReportView data={data} summary={summary} />;
}

export default function ReportPage() {
    return (
        <main className="min-h-screen bg-background text-foreground p-6">
            <Suspense fallback={
                <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
                    <Loader2 className="w-12 h-12 animate-spin text-indigo-500" />
                    <h2 className="text-2xl font-semibold animate-pulse">Loading...</h2>
                </div>
            }>
                <ReportContent />
            </Suspense>
        </main>
    );
}
