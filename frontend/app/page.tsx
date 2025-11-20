"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Send, ShieldCheck, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    try {
      // In a real app, we might want to parse the input first or ask for details.
      // For now, we'll assume the input is the company name and redirect to a loading/report page
      // or call the API directly.

      // Let's call the API to start the assessment
      // We'll parse the input simply for now. 
      // Ideally, we'd have a multi-step form or an agent to parse the natural language.
      // For this demo, we'll assume the user types "Company Name, Address, State" or just "Company Name"

      // For better UX, let's just pass the raw string to the backend if it could handle it,
      // but our backend expects structured data.
      // Let's make a simple parser or just ask the user for details if we were building a full chat.
      // To keep it simple and "ChatGPT-style", we'll send the input to a "parse" endpoint or just try to infer.

      // SIMPLIFICATION: We will redirect to the report page with the query param
      // and let the report page handle the API call and loading state.
      router.push(`/report?company=${encodeURIComponent(input)}`);

    } catch (error) {
      console.error("Error:", error);
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-purple-900/30 rounded-full blur-[100px]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-blue-900/30 rounded-full blur-[100px]" />

      <div className="z-10 w-full max-w-3xl flex flex-col items-center gap-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-4"
        >
          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 shadow-2xl">
              <ShieldCheck className="w-12 h-12 text-indigo-400" />
            </div>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight gradient-text">
            Risk Assessment AI
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Deep-dive diligence on any company. Powered by autonomous agents.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="w-full"
        >
          <form onSubmit={handleSubmit} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
            <div className="relative flex items-center bg-black/80 backdrop-blur-xl rounded-xl border border-white/10 p-2 shadow-2xl">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter a company name (e.g. Groma, Boston, MA)..."
                className="flex-1 bg-transparent border-none text-lg px-4 py-3 focus:ring-0 placeholder:text-white/20 text-white"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="p-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </form>
          <div className="mt-6 flex flex-wrap justify-center gap-3 text-sm text-muted-foreground">
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:bg-white/10 cursor-pointer transition">
              Groma, Boston MA
            </span>
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:bg-white/10 cursor-pointer transition">
              OpenAI, San Francisco
            </span>
            <span className="px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:bg-white/10 cursor-pointer transition">
              SpaceX, Hawthorne CA
            </span>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
