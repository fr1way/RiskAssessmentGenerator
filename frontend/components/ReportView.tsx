/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
    Shield, AlertTriangle, CheckCircle2, Building2,
    TrendingUp, Users, Globe, Lock, FileText
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface CompanyInfo {
    companyName: string;
    fullAddress: string;
    businessSector: string;
    state: string;
}

export interface ExecutiveSummary {
    overallRiskRating: string;
    keyPositiveFactors: string[];
    keyNegativeFactors: string[];
    informationGaps: string;
}

export interface RiskAssessmentMatrix {
    [key: string]: string;
}

export interface FinancialMetric {
    metricName: string;
    value: string;
    period: string;
    sourceURL?: string;
}

export interface FinancialMetrics {
    summary: string;
    metrics: FinancialMetric[];
}

export interface FinancialViabilityAnalysis {
    companyType: string;
    financialMetrics: FinancialMetrics;
    signsOfDistress: { summary: string; sourceURL?: string };
}

export interface Executive {
    name: string;
    title: string;
    backgroundSummary: string;
    negativeNews?: any;
}

export interface LeadershipAndGovernance {
    executiveTeam: Executive[];
    executiveTurnover: { summary: string; sourceURL?: string };
    corporateGovernanceStructure: { summary: string; boardIndependence: string; governanceIssues: string; sourceURL?: string };
}

export interface Review {
    platform: string;
    overallRating: string;
    commonComplaints: string[];
}

export interface ReputationalAnalysis {
    mediaScan: { summary: string; sentiment: string; sourceURL?: string };
    customerReviewSynthesis: Review[];
    socialResponsibilityControversies: { summary: string; sourceURL?: string };
    digitalFootprint: { summary: string; sentiment: string; viralIssues: string; sourceURL?: string };
}

export interface LegalAndRegulatoryActions {
    summary: string;
    findings: any[];
}

export interface CorporateIdentityAndLegalStanding {
    businessRegistration: { status: string; summary: string; sourceURL?: string };
    legalAndRegulatoryActions: LegalAndRegulatoryActions;
    permitsAndLicenses: { summary: string; sourceURL?: string };
}

export interface RiskReport {
    overallRiskScore: number;
    executiveSummary: ExecutiveSummary;
    riskAssessmentMatrix: RiskAssessmentMatrix;
    corporateIdentityAndLegalStanding: CorporateIdentityAndLegalStanding;
    financialViabilityAnalysis: FinancialViabilityAnalysis;
    leadershipAndGovernance: LeadershipAndGovernance;
    marketAndOperationalRisk: any;
    reputationalAnalysis: ReputationalAnalysis;
}

export interface FullAssessmentResponse {
    companyInfo: CompanyInfo;
    riskReport: RiskReport;
}

interface ReportViewProps {
    data: FullAssessmentResponse;
    summary?: string;
}

export default function ReportView({ data, summary }: ReportViewProps) {
    const [activeTab, setActiveTab] = useState<"findings" | "report">("findings");
    const { companyInfo, riskReport } = data;

    if (!riskReport) return <div>Invalid Data Format</div>;

    return (
        <div className="max-w-7xl mx-auto space-y-8 pb-20">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight text-white">{companyInfo.companyName}</h1>
                    <div className="flex items-center gap-2 text-muted-foreground mt-2">
                        <Building2 className="w-4 h-4" />
                        <span>{companyInfo.state} • {companyInfo.businessSector}</span>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className={`px-4 py-2 rounded-lg border ${riskReport.overallRiskScore <= 3 ? "bg-green-500/10 border-green-500/20 text-green-400" :
                        riskReport.overallRiskScore <= 7 ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-400" :
                            "bg-red-500/10 border-red-500/20 text-red-400"
                        }`}>
                        <div className="text-xs uppercase font-semibold tracking-wider opacity-80">Risk Score</div>
                        <div className="text-2xl font-bold flex items-center gap-2">
                            <Shield className="w-6 h-6" />
                            {riskReport.overallRiskScore}/10
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-4 border-b border-white/10">
                <button
                    onClick={() => setActiveTab("findings")}
                    className={`px-4 py-2 text-sm font-medium transition-colors relative ${activeTab === "findings" ? "text-white" : "text-muted-foreground hover:text-white"
                        }`}
                >
                    Research Findings
                    {activeTab === "findings" && (
                        <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />
                    )}
                </button>
                <button
                    onClick={() => setActiveTab("report")}
                    className={`px-4 py-2 text-sm font-medium transition-colors relative ${activeTab === "report" ? "text-white" : "text-muted-foreground hover:text-white"
                        }`}
                >
                    Risk Report
                    {activeTab === "report" && (
                        <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />
                    )}
                </button>
            </div>

            {/* Content */}
            {activeTab === "findings" ? (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-8"
                >
                    <div className="prose prose-invert max-w-none">
                        {summary ? (
                            <div className="whitespace-pre-wrap leading-relaxed text-gray-300">
                                {summary}
                            </div>
                        ) : (
                            <div className="text-muted-foreground italic">No summary available.</div>
                        )}
                    </div>
                </motion.div>
            ) : (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                >
                    {/* Executive Summary */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <FileText className="w-5 h-5 text-indigo-400" />
                                Executive Summary
                            </h3>

                            <div className="space-y-4">
                                <div>
                                    <div className="text-sm font-medium text-green-400 mb-2 flex items-center gap-2">
                                        <CheckCircle2 className="w-4 h-4" /> Key Positives
                                    </div>
                                    <ul className="space-y-2">
                                        {riskReport?.executiveSummary?.keyPositiveFactors?.map((factor, i) => (
                                            <li key={i} className="text-sm text-gray-400 pl-4 border-l-2 border-green-500/20">
                                                {factor}
                                            </li>
                                        )) || <li className="text-sm text-gray-500">No data available</li>}
                                    </ul>
                                </div>

                                <div>
                                    <div className="text-sm font-medium text-red-400 mb-2 flex items-center gap-2">
                                        <AlertTriangle className="w-4 h-4" /> Key Risks
                                    </div>
                                    <ul className="space-y-2">
                                        {riskReport?.executiveSummary?.keyNegativeFactors?.map((factor, i) => (
                                            <li key={i} className="text-sm text-gray-400 pl-4 border-l-2 border-red-500/20">
                                                {factor}
                                            </li>
                                        )) || <li className="text-sm text-gray-500">No data available</li>}
                                    </ul>
                                </div>

                                {riskReport?.executiveSummary?.informationGaps && (
                                    <div className="mt-4 p-3 bg-white/5 rounded-lg border border-white/5">
                                        <span className="text-xs font-bold text-white uppercase tracking-wider">Information Gaps:</span>
                                        <span className="text-xs text-gray-400 ml-2">{riskReport.executiveSummary.informationGaps}</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Risk Matrix */}
                        <div className="bg-black/40 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-indigo-400" />
                                Risk Matrix
                            </h3>
                            <div className="space-y-3">
                                {riskReport?.riskAssessmentMatrix && Object.entries(riskReport.riskAssessmentMatrix).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between group">
                                        <span className="text-sm text-gray-400 capitalize group-hover:text-white transition-colors">
                                            {key.replace(/([A-Z])/g, ' $1').trim()}
                                        </span>
                                        <span className={`text-xs px-2 py-1 rounded-full font-medium border ${value === "Low" ? "bg-green-500/10 border-green-500/20 text-green-400" :
                                            value === "Medium" ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-400" :
                                                "bg-red-500/10 border-red-500/20 text-red-400"
                                            }`}>
                                            {value}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Detailed Sections */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Card title="Financial Viability" icon={<TrendingUp className="w-5 h-5 text-blue-400" />}>
                            <p className="text-sm text-white/80 mb-4">{riskReport?.financialViabilityAnalysis?.financialMetrics?.summary || "No data"}</p>
                            <div className="space-y-2">
                                {riskReport?.financialViabilityAnalysis?.financialMetrics?.metrics?.map((m, i) => (
                                    <div key={i} className="flex justify-between text-sm border-b border-white/5 pb-2">
                                        <span className="text-muted-foreground">{m.metricName}</span>
                                        <span className="font-mono">{m.value}</span>
                                    </div>
                                ))}
                            </div>
                        </Card>

                        <Card title="Leadership & Governance" icon={<Users className="w-5 h-5 text-purple-400" />}>
                            <div className="space-y-4">
                                {riskReport?.leadershipAndGovernance?.executiveTeam?.map((exec, i) => (
                                    <div key={i} className="flex items-start gap-3">
                                        <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-xs font-bold">
                                            {exec.name?.charAt(0) || "?"}
                                        </div>
                                        <div>
                                            <div className="font-medium">{exec.name || "Unknown Executive"}</div>
                                            <div className="text-xs text-muted-foreground">{exec.title}</div>
                                            <p className="text-xs text-white/60 mt-1 line-clamp-2">{exec.backgroundSummary}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Card>

                        <Card title="Reputational Analysis" icon={<Globe className="w-5 h-5 text-pink-400" />}>
                            <div className="space-y-4">
                                <div className="bg-white/5 p-3 rounded-lg">
                                    <div className="text-xs text-muted-foreground mb-1">Media Sentiment</div>
                                    <div className="font-medium">{riskReport?.reputationalAnalysis?.mediaScan?.sentiment || "N/A"}</div>
                                    <p className="text-xs text-white/70 mt-1">{riskReport?.reputationalAnalysis?.mediaScan?.summary}</p>
                                </div>
                                <div>
                                    <div className="text-xs text-muted-foreground mb-2">Customer Reviews</div>
                                    {riskReport?.reputationalAnalysis?.customerReviewSynthesis?.map((review, i) => (
                                        <div key={i} className="mb-3 last:mb-0">
                                            <div className="flex justify-between text-sm font-medium">
                                                <span>{review.platform}</span>
                                                <span>{review.overallRating}</span>
                                            </div>
                                            <ul className="mt-1 space-y-1">
                                                {review.commonComplaints?.slice(0, 2).map((c: string, j: number) => (
                                                    <li key={j} className="text-xs text-red-300/80">• {c}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </Card>

                        <Card title="Legal & Compliance" icon={<Lock className="w-5 h-5 text-orange-400" />}>
                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-sm font-medium mb-1">Legal Actions</h4>
                                    <p className="text-sm text-white/70">{riskReport?.corporateIdentityAndLegalStanding?.legalAndRegulatoryActions?.summary || "No data"}</p>
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium mb-1">Permits & Licenses</h4>
                                    <p className="text-sm text-white/70">{riskReport?.corporateIdentityAndLegalStanding?.permitsAndLicenses?.summary || "No data"}</p>
                                </div>
                            </div>
                        </Card>
                    </div>
                </motion.div>
            )}
        </div>
    );
}

function Card({ title, icon, children, className }: { title: string, icon: React.ReactNode, children: React.ReactNode, className?: string }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className={cn("glass-panel rounded-2xl p-6", className)}
        >
            <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-4">
                {icon}
                <h2 className="text-lg font-semibold">{title}</h2>
            </div>
            {children}
        </motion.div>
    );
}
