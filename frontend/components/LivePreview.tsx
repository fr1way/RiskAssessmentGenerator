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
                            className="relative aspect-video bg-slate-900 rounded-lg overflow-hidden border border-slate-700 shadow-lg group"
                        >
                            {/* Header Bar */}
                            <div className="absolute top-0 left-0 right-0 h-8 bg-black/60 backdrop-blur-sm flex items-center justify-between px-3 z-10">
                                <div className="flex items-center gap-2 text-xs font-mono text-white">
                                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                    {agent.id}
                                </div>
                                <div className="text-[10px] text-slate-300 truncate max-w-[150px]">
                                    {agent.status}
                                </div>
                            </div>

                            {/* Main Preview Image */}
                            {agent.image ? (
                                <img
                                    src={agent.image}
                                    alt={`Preview ${agent.id}`}
                                    className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity"
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-slate-600">
                                    <Globe className="w-8 h-8 animate-pulse" />
                                </div>
                            )}

                            {/* URL Overlay (Bottom) */}
                            <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
                                <p className="text-[10px] text-slate-400 truncate font-mono">
                                    {agent.url}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {activeAgents.length === 0 && isActive && (
                    <div className="col-span-2 h-48 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-700 rounded-lg">
                        <Shield className="w-8 h-8 mb-2 animate-bounce" />
                        <p>Initializing Agents...</p>
                    </div>
                )}
            </div>
        </div>
    );
}
