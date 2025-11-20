/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React from "react";
import { motion } from "framer-motion";
import {
    Shield, AlertTriangle, CheckCircle, Building,
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
}

export default function ReportView({ data }: ReportViewProps) {
    const { companyInfo, riskReport } = data;

    if (!riskReport) return <div>Invalid Data Format</div>;

    const getRiskColor = (score: number) => {
        if (score <= 3) return "text-green-400";
        if (score <= 7) return "text-yellow-400";
        return "text-red-500";
    };

    const getRiskBg = (score: number) => {
        if (score <= 3) return "bg-green-500/20 border-green-500/30";
        if (score <= 7) return "bg-yellow-500/20 border-yellow-500/30";
        return "bg-red-500/20 border-red-500/30";
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8 pb-20">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/10 pb-6"
            >
                <div>
                    <h1 className="text-4xl font-bold gradient-text">{companyInfo.companyName}</h1>
                    <div className="flex items-center gap-2 text-muted-foreground mt-2">
                        <Building className="w-4 h-4" />
                        <span>{companyInfo.fullAddress}</span>
                        <span className="w-1 h-1 rounded-full bg-white/20" />
                        <span>{companyInfo.businessSector}</span>
                    </div>
                </div>
                <div className={cn("px-6 py-3 rounded-2xl border backdrop-blur-md flex items-center gap-3", getRiskBg(riskReport.overallRiskScore))}>
                    <Shield className={cn("w-8 h-8", getRiskColor(riskReport.overallRiskScore))} />
                    <div>
                        <div className="text-xs uppercase tracking-wider opacity-70">Risk Score</div>
                        <div className={cn("text-2xl font-bold", getRiskColor(riskReport.overallRiskScore))}>
                            {riskReport.overallRiskScore}/10
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Executive Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card title="Executive Summary" icon={<FileText className="w-5 h-5 text-indigo-400" />} className="md:col-span-2">
                    <div className="space-y-4">
                        <div>
                            <h3 className="text-sm font-medium text-green-400 mb-2 flex items-center gap-2">
                                <CheckCircle className="w-4 h-4" /> Key Positives
                            </h3>
                            <ul className="space-y-2">
                                {riskReport.executiveSummary.keyPositiveFactors.map((factor: string, i: number) => (
                                    <li key={i} className="text-sm text-white/80 pl-4 border-l-2 border-green-500/30">{factor}</li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-red-400 mb-2 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4" /> Key Risks
                            </h3>
                            <ul className="space-y-2">
                                {riskReport.executiveSummary.keyNegativeFactors.map((factor: string, i: number) => (
                                    <li key={i} className="text-sm text-white/80 pl-4 border-l-2 border-red-500/30">{factor}</li>
                                ))}
                            </ul>
                        </div>
                        {riskReport.executiveSummary.informationGaps && (
                            <div className="bg-white/5 p-3 rounded-lg text-sm text-muted-foreground">
                                <span className="font-semibold text-white">Information Gaps:</span> {riskReport.executiveSummary.informationGaps}
                            </div>
                        )}
                    </div>
                </Card>

                <Card title="Risk Matrix" icon={<TrendingUp className="w-5 h-5 text-indigo-400" />}>
                    <div className="space-y-3">
                        {Object.entries(riskReport.riskAssessmentMatrix).map(([key, value]) => (
                            <div key={key} className="flex justify-between items-center text-sm">
                                <span className="capitalize text-muted-foreground">{key.replace(/Risk$/, "").replace(/([A-Z])/g, ' $1').trim()}</span>
                                <RiskBadge level={value as string} />
                            </div>
                        ))}
                    </div>
                </Card>
            </div>

            {/* Detailed Sections */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card title="Financial Viability" icon={<TrendingUp className="w-5 h-5 text-blue-400" />}>
                    <p className="text-sm text-white/80 mb-4">{riskReport.financialViabilityAnalysis.financialMetrics.summary}</p>
                    <div className="space-y-2">
                        {riskReport.financialViabilityAnalysis.financialMetrics.metrics.map((m, i) => (
                            <div key={i} className="flex justify-between text-sm border-b border-white/5 pb-2">
                                <span className="text-muted-foreground">{m.metricName}</span>
                                <span className="font-mono">{m.value}</span>
                            </div>
                        ))}
                    </div>
                </Card>

                <Card title="Leadership & Governance" icon={<Users className="w-5 h-5 text-purple-400" />}>
                    <div className="space-y-4">
                        {riskReport.leadershipAndGovernance.executiveTeam.map((exec, i) => (
                            <div key={i} className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-xs font-bold">
                                    {exec.name.charAt(0)}
                                </div>
                                <div>
                                    <div className="font-medium">{exec.name}</div>
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
                            <div className="font-medium">{riskReport.reputationalAnalysis.mediaScan.sentiment}</div>
                            <p className="text-xs text-white/70 mt-1">{riskReport.reputationalAnalysis.mediaScan.summary}</p>
                        </div>
                        <div>
                            <div className="text-xs text-muted-foreground mb-2">Customer Reviews</div>
                            {riskReport.reputationalAnalysis.customerReviewSynthesis.map((review, i) => (
                                <div key={i} className="mb-3 last:mb-0">
                                    <div className="flex justify-between text-sm font-medium">
                                        <span>{review.platform}</span>
                                        <span>{review.overallRating}</span>
                                    </div>
                                    <ul className="mt-1 space-y-1">
                                        {review.commonComplaints.slice(0, 2).map((c: string, j: number) => (
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
                            <p className="text-sm text-white/70">{riskReport.corporateIdentityAndLegalStanding.legalAndRegulatoryActions.summary}</p>
                        </div>
                        <div>
                            <h4 className="text-sm font-medium mb-1">Permits & Licenses</h4>
                            <p className="text-sm text-white/70">{riskReport.corporateIdentityAndLegalStanding.permitsAndLicenses.summary}</p>
                        </div>
                    </div>
                </Card>
            </div>
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

function RiskBadge({ level }: { level: string }) {
    const colors = {
        Low: "bg-green-500/20 text-green-400 border-green-500/30",
        Medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        High: "bg-red-500/20 text-red-400 border-red-500/30",
        Unknown: "bg-gray-500/20 text-gray-400 border-gray-500/30"
    };

    const colorClass = colors[level as keyof typeof colors] || colors.Unknown;

    return (
        <span className={cn("px-2 py-0.5 rounded-full text-xs font-medium border", colorClass)}>
            {level}
        </span>
    );
}
