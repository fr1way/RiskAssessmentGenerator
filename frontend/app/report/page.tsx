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

    const [data, setData] = useState<FullAssessmentResponse | null>(null);
    const [logs, setLogs] = useState<any[]>([]);
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Live Preview State
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [previewImage, setPreviewImage] = useState<string | null>(null);

    useEffect(() => {
        if (!companyQuery) return;

        const fetchData = async () => {
            try {
                // Read new params
                const stateParam = searchParams.get("state") || "Unknown";
                const typeParam = searchParams.get("type") || "other";

                // Fallback for legacy URL format (comma separated) if needed, but prioritizing new params
                let name = companyQuery;
                let address = stateParam;

                if (companyQuery.includes(",")) {
                    const parts = companyQuery.split(",");
                    name = parts[0].trim();
                    // If state param wasn't provided, try to extract from legacy string
                    if (stateParam === "Unknown" && parts.length > 1) {
                        address = parts.slice(1).join(",").trim();
                    }
                }

                const response = await fetch("http://localhost:8000/api/assess", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        companyName: name,
                        companyAddress: address,
                        state: stateParam !== "Unknown" ? stateParam : address,
                        companyType: typeParam
                    })
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
                        try {
                            const msg = JSON.parse(line);
                            if (msg.type === "log") {
                                setLogs(prev => [...prev, { ...msg, timestamp: Date.now() }]);
                            } else if (msg.type === "preview") {
                                // Update Live Preview
                                setPreviewUrl(msg.url);
                                setPreviewImage(msg.image);
                            } else if (msg.type === "summary") {
                                setSummary(msg.content);
                            } else if (msg.type === "result") {
                                setData(msg.data);
                            } else if (msg.type === "error") {
                                setError(msg.message);
                            }
                        } catch (e) {
                            console.error("Error parsing stream:", e);
                        }
                    }
                }
            } catch (err) {
                console.error(err);
                setError("Failed to generate risk assessment. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [companyQuery]);

    if (!companyQuery) {
        return <div className="text-white text-center mt-20">No company specified.</div>;
    }

    if (loading || !data) {
        return (
            <div className="min-h-[80vh] flex flex-col items-center justify-center p-4">
                <div className="w-full max-w-7xl">
                    <h2 className="text-3xl font-bold text-center mb-8 gradient-text">
                        Analyzing {companyQuery}
                    </h2>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Live Preview Column (Main Stage) */}
                        <div className="lg:col-span-2">
                            <div className="sticky top-8 space-y-6">
                                <LivePreview
                                    url={previewUrl}
                                    image={previewImage}
                                    isActive={loading}
                                />
                            </div>
                        </div>

                        {/* Logs Column (Sidebar) */}
                        <div className="lg:col-span-1">
                            <ResearchLog logs={logs} />
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
