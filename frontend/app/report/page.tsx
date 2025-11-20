"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import axios from "axios";
import { Loader2, AlertTriangle } from "lucide-react";
import ReportView, { FullAssessmentResponse } from "@/components/ReportView";

function ReportContent() {
    const searchParams = useSearchParams();
    const companyQuery = searchParams.get("company");

    const [data, setData] = useState<FullAssessmentResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!companyQuery) return;

        const fetchData = async () => {
            try {
                const parts = companyQuery.split(",");
                const name = parts[0].trim();
                const address = parts.length > 1 ? parts.slice(1).join(",").trim() : "";
                const state = "Unknown";

                const response = await axios.post("http://localhost:8000/api/assess", {
                    companyName: name,
                    companyAddress: address,
                    state: state,
                    companyType: "other"
                });

                setData(response.data);
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

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
                <Loader2 className="w-12 h-12 animate-spin text-indigo-500" />
                <h2 className="text-2xl font-semibold animate-pulse">Analyzing {companyQuery}...</h2>
                <p className="text-muted-foreground">Scanning public records, news, and financial data.</p>
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

    return data ? <ReportView data={data} /> : null;
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
