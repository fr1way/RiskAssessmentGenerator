"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Globe, Brain, CheckCircle, Loader2 } from "lucide-react";

interface LogMessage {
    type: "log" | "result" | "error";
    message: string;
    timestamp: number;
}

interface ResearchLogProps {
    logs: LogMessage[];
}

export default function ResearchLog({ logs }: ResearchLogProps) {
    // Auto-scroll to bottom logic could be added here if needed

    const getIcon = (msg: string) => {
        if (msg.includes("Searching")) return <Search className="w-4 h-4 text-blue-400" />;
        if (msg.includes("Browsing")) return <Globe className="w-4 h-4 text-green-400" />;
        if (msg.includes("Synthesizing")) return <Brain className="w-4 h-4 text-purple-400" />;
        return <CheckCircle className="w-4 h-4 text-gray-400" />;
    };

    return (
        <div className="w-full space-y-4">
            <div className="flex items-center gap-2 text-indigo-400 mb-4">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span className="font-semibold tracking-wide uppercase text-xs">AI Agent Active</span>
            </div>

            <div className="bg-black/40 backdrop-blur-md rounded-xl border border-white/10 p-4 font-mono text-sm h-[400px] overflow-y-auto custom-scrollbar">
                <div className="space-y-3">
                    <AnimatePresence initial={false}>
                        {logs.map((log) => (
                            <motion.div
                                key={log.timestamp}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-start gap-3 text-white/80"
                            >
                                <div className="mt-0.5 shrink-0">
                                    {getIcon(log.message)}
                                </div>
                                <span className="leading-relaxed">{log.message}</span>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {/* Typing indicator for "thinking" effect */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-1 pl-7 pt-2"
                    >
                        <span className="w-1.5 h-1.5 bg-white/30 rounded-full animate-pulse" />
                        <span className="w-1.5 h-1.5 bg-white/30 rounded-full animate-pulse delay-75" />
                        <span className="w-1.5 h-1.5 bg-white/30 rounded-full animate-pulse delay-150" />
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
