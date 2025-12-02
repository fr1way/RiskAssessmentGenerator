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
      const form = e.target as HTMLFormElement;
      const state = (form.elements.namedItem("state") as HTMLInputElement).value;
      const type = (form.elements.namedItem("type") as HTMLInputElement).value;

      // Construct query string with all parameters
      const params = new URLSearchParams({
        company: input,
        state: state,
        type: type
      });

      router.push(`/report?${params.toString()}`);

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
          <form onSubmit={handleSubmit} className="relative group w-full max-w-2xl mx-auto space-y-4">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />

            <div className="relative flex flex-col gap-3 bg-black/80 backdrop-blur-xl rounded-xl border border-white/10 p-4 shadow-2xl">
              <div className="flex flex-col md:flex-row gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Company Name (e.g. Groma)"
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-white/20 text-white outline-none transition-all"
                  disabled={loading}
                  required
                />
                <input
                  type="text"
                  name="state"
                  id="stateInput"
                  placeholder="State/Location (e.g. Boston, MA)"
                  className="md:w-1/3 bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-white/20 text-white outline-none transition-all"
                  disabled={loading}
                  required
                />
              </div>

              <div className="flex gap-3">
                <input
                  type="text"
                  name="type"
                  id="typeInput"
                  placeholder="Business Type (e.g. Real Estate, Tech)"
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-white/20 text-white outline-none transition-all"
                  disabled={loading}
                  required
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <span>Start</span>
                      <Send className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
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
