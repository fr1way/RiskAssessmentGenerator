import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Globe, Shield } from 'lucide-react';

interface AgentState {
    id: string;
    url: string;
    image: string | null;
    status: string;
    lastUpdate: number;
}

interface LivePreviewProps {
    agents: Record<string, AgentState>;
    isActive: boolean;
}

export default function LivePreview({ agents, isActive }: LivePreviewProps) {
    const activeAgents = Object.values(agents).filter(a => Date.now() - a.lastUpdate < 10000); // Hide stale agents > 10s

    if (!isActive && activeAgents.length === 0) return null;

    return (
        <div className="w-full space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-400 animate-pulse" />
                    <h3 className="text-lg font-semibold text-white">Live Agent Command Center</h3>
                </div>
                <div className="text-xs text-slate-400">
                    {activeAgents.length} Active Agents
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AnimatePresence>
                    {activeAgents.map((agent) => (
                        <motion.div
                            key={agent.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="relative aspect-video bg-slate-900 rounded-xl overflow-hidden border border-slate-700 shadow-2xl group"
                        >
                            {/* Header Bar */}
                            <div className="absolute top-0 left-0 right-0 h-10 bg-black/70 backdrop-blur-md flex items-center justify-between px-4 z-10 border-b border-white/10">
                                <div className="flex items-center gap-3">
                                    <div className="flex items-center gap-2 text-sm font-mono text-white font-bold">
                                        <span className="relative flex h-3 w-3">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                        </span>
                                        {agent.id}
                                    </div>
                                    <div className="px-2 py-0.5 rounded bg-white/10 text-[10px] text-slate-300 font-mono">
                                        LIVE | 20 FPS
                                    </div>
                                </div>
                                <div className="text-xs text-slate-300 truncate max-w-[200px] flex items-center gap-2">
                                    <Activity className="w-3 h-3 text-indigo-400" />
                                    {agent.status}
                                </div>
                            </div>

                            {/* Main Preview Image */}
                            {agent.image ? (
                                <img
                                    src={agent.image}
                                    alt={`Preview ${agent.id}`}
                                    className="w-full h-full object-cover opacity-100 transition-none" // Remove transition for instant FPS updates
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-slate-600 bg-slate-950">
                                    <Globe className="w-12 h-12 animate-pulse" />
                                </div>
                            )}

                            {/* URL Overlay (Bottom) */}
                            <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent">
                                <p className="text-xs text-slate-300 truncate font-mono bg-black/40 inline-block px-2 py-1 rounded">
                                    {agent.url}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {activeAgents.length === 0 && isActive && (
                    <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/50">
                        <Shield className="w-12 h-12 mb-4 animate-bounce text-indigo-500" />
                        <p className="text-lg font-medium">Deploying Agents...</p>
                        <p className="text-sm text-slate-600">Establishing secure high-speed connection</p>
                    </div>
                )}
            </div>
        </div>
    );
}
