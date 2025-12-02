"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Eye, Globe, Loader2 } from "lucide-react";

interface LivePreviewProps {
    url: string | null;
    image: string | null;
    isActive: boolean;
}

export default function LivePreview({ url, image, isActive }: LivePreviewProps) {
    if (!isActive && !image) return null;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-xl overflow-hidden border border-white/10 bg-black/40 backdrop-blur-md shadow-2xl"
        >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-b border-white/5">
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                        <div className="absolute inset-0 w-2 h-2 rounded-full bg-red-500 animate-ping opacity-75" />
                    </div>
                    <span className="text-xs font-bold text-white uppercase tracking-wider">Live Agent Feed</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Eye className="w-3 h-3" />
                    <span>Monitoring</span>
                </div>
            </div>

            {/* Content */}
            <div className="relative aspect-video bg-black/60 flex items-center justify-center">
                <AnimatePresence mode="wait">
                    {image ? (
                        <motion.img
                            key={url} // Re-animate on URL change
                            src={image}
                            alt="Live Agent View"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="w-full h-full object-cover"
                        />
                    ) : (
                        <div className="flex flex-col items-center gap-3 text-muted-foreground">
                            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
                            <span className="text-sm">Waiting for visual feed...</span>
                        </div>
                    )}
                </AnimatePresence>

                {/* URL Overlay */}
                {url && (
                    <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 to-transparent">
                        <div className="flex items-center gap-2 text-xs text-white/80 font-mono truncate">
                            <Globe className="w-3 h-3 flex-shrink-0 text-indigo-400" />
                            <span className="truncate">{url}</span>
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
