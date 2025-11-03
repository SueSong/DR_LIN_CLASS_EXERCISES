'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Sparkles, Shield, Heart, Lock, Zap, Award, CheckCircle } from 'lucide-react';

export default function CoachEntryPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    try {
      localStorage.setItem('parent', JSON.stringify({ name: name.trim() }));
      await new Promise(resolve => setTimeout(resolve, 500)); // Smooth transition
      router.push('/coach/chat');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-orange-50/40 to-amber-50/60 p-6 relative overflow-hidden">
      {/* Animated Background Orbs */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-orange-200/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-amber-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>
      
      <div className="w-full max-w-xl relative z-10 animate-scale-in">
        <div className="bg-white rounded-[2.5rem] shadow-2xl border-2 border-slate-100 p-12 md:p-14">
          {/* Icon & Header */}
          <div className="text-center mb-10">
            <div className="relative inline-block mb-8">
              <div className="w-28 h-28 bg-gradient-to-br from-orange-500 via-amber-500 to-orange-600 rounded-[2rem] flex items-center justify-center shadow-2xl shadow-orange-500/50">
                <Sparkles className="w-14 h-14 text-white animate-pulse" />
              </div>
              {/* Floating Badges */}
              <div className="absolute -top-3 -right-3 w-12 h-12 bg-gradient-to-br from-rose-500 to-pink-500 rounded-full flex items-center justify-center shadow-xl animate-bounce">
                <Heart className="w-6 h-6 text-white fill-white" />
              </div>
              <div className="absolute -bottom-3 -left-3 w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-xl animate-bounce" style={{ animationDelay: '0.5s' }}>
                <Shield className="w-6 h-6 text-white" />
              </div>
            </div>
            
            <h1 className="text-5xl font-black mb-4 leading-tight">
              <span className="bg-gradient-to-r from-orange-600 via-amber-500 to-orange-600 bg-clip-text text-transparent">
                Welcome, Parent!
              </span>
            </h1>
            <p className="text-slate-600 text-xl font-semibold">
              Let's begin your <span className="text-orange-600 font-black">personalized</span> journey
            </p>
          </div>

          {/* Form */}
          <form onSubmit={submit} className="space-y-8">
            <div>
              <label className="block text-lg font-black text-slate-900 mb-4 flex items-center gap-2">
                What should we call you?
                <span className="text-orange-600 text-2xl">*</span>
              </label>
              <div className="relative">
                <input 
                  value={name} 
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-7 py-5 bg-gradient-to-br from-slate-50 to-orange-50/50 border-3 border-orange-300 rounded-2xl focus:ring-4 focus:ring-orange-500/40 focus:border-orange-500 transition-all outline-none text-slate-900 text-xl font-semibold placeholder:text-slate-400 hover:border-orange-400 shadow-inner"
                  placeholder="Enter your name"
                  required
                  autoFocus
                />
                <div className="absolute right-5 top-1/2 -translate-y-1/2">
                  {name && <CheckCircle className="w-6 h-6 text-green-500" />}
                </div>
              </div>
            </div>

            <button 
              type="submit"
              disabled={loading || !name.trim()}
              className="w-full bg-gradient-to-r from-orange-600 via-orange-500 to-amber-600 text-white rounded-2xl px-8 py-6 font-black text-2xl shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-4 group border-3 border-orange-400/50 relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-amber-400 opacity-0 group-hover:opacity-20 transition-opacity" />
              {loading ? (
                <>
                  <svg className="animate-spin h-7 w-7 relative z-10" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span className="animate-pulse relative z-10">Starting Your Session...</span>
                </>
              ) : (
                <>
                  <Zap className="w-7 h-7 fill-white animate-pulse relative z-10" />
                  <span className="relative z-10">Start Coaching Session</span>
                  <ArrowRight className="w-7 h-7 group-hover:translate-x-2 transition-transform relative z-10" />
                </>
              )}
            </button>
          </form>

          {/* Trust Badges */}
          <div className="mt-12 pt-10 border-t-2 border-slate-100">
            <p className="text-center text-sm font-bold text-slate-500 mb-6 uppercase tracking-wide">Your Privacy Matters</p>
            <div className="grid grid-cols-2 gap-5">
              <div className="flex flex-col items-center gap-3 p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-3xl border-2 border-green-200 hover:scale-105 transition-transform shadow-lg hover:shadow-xl">
                <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-xl">
                  <Lock className="w-7 h-7 text-white" />
                </div>
                <span className="text-base font-black text-green-900 text-center leading-tight">Private & Secure</span>
              </div>
              <div className="flex flex-col items-center gap-3 p-6 bg-gradient-to-br from-rose-50 to-pink-50 rounded-3xl border-2 border-rose-200 hover:scale-105 transition-transform shadow-lg hover:shadow-xl">
                <div className="w-14 h-14 bg-gradient-to-br from-rose-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-xl">
                  <Heart className="w-7 h-7 text-white fill-white" />
                </div>
                <span className="text-base font-black text-rose-900 text-center leading-tight">Judgment Free</span>
              </div>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="mt-10 pt-8 border-t-2 border-slate-100">
            <div className="bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 rounded-2xl p-6 border-2 border-orange-200/50 shadow-inner">
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-slate-700 leading-relaxed font-medium">
                  By continuing, you'll receive <span className="text-orange-700 font-black">evidence-based parenting guidance</span>. This service is not a substitute for professional medical, psychological, or therapeutic advice.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Back Link */}
        <div className="text-center mt-8">
          <a 
            href="/" 
            className="inline-flex items-center gap-2 text-base text-slate-600 hover:text-orange-600 transition-colors font-bold bg-white px-8 py-4 rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all border-2 border-slate-200 hover:border-orange-300"
          >
            <ArrowRight className="w-5 h-5 rotate-180" />
            Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
