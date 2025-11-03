import Link from 'next/link'
import { Sparkles, Heart, Shield, Zap, ArrowRight, Check, Star, Award, Users, Clock } from 'lucide-react'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-white via-orange-50/40 to-amber-50/60 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-orange-200/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-amber-200/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-rose-200/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>
      
      <div className="relative z-10 container mx-auto px-4 py-16 md:py-24">
        {/* Hero Section */}
        <div className="max-w-6xl mx-auto text-center mb-24 animate-fade-in">
          {/* Floating Badge */}
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-500 to-amber-500 text-white px-6 py-2.5 rounded-full shadow-2xl shadow-orange-500/40 mb-10 hover:shadow-orange-500/60 hover:scale-105 transition-all duration-300 border-2 border-orange-300/50">
            <Award className="w-5 h-5 fill-white animate-pulse" />
            <span className="text-sm font-extrabold tracking-wide">TRUSTED BY 10,000+ PARENTS</span>
            <Award className="w-5 h-5 fill-white animate-pulse" />
          </div>
          
          {/* Hero Heading */}
          <h1 className="text-6xl md:text-8xl font-black mb-8 leading-tight tracking-tight">
            <span className="block text-slate-900 mb-3 drop-shadow-sm">
              Every Parent Needs
            </span>
            <span className="block bg-gradient-to-r from-orange-600 via-amber-500 to-orange-600 bg-clip-text text-transparent drop-shadow-lg animate-gradient bg-[length:200%_auto]">
              A Growth Partner
            </span>
          </h1>
          
          {/* Subheading with Colorful Keywords */}
          <p className="text-2xl md:text-3xl mb-12 max-w-4xl mx-auto leading-relaxed font-medium">
            <span className="text-slate-700">Get </span>
            <span className="text-orange-600 font-extrabold relative">
              evidence-informed
              <span className="absolute bottom-0 left-0 w-full h-1 bg-orange-400/40" />
            </span>
            <span className="text-slate-700">, </span>
            <span className="text-amber-600 font-extrabold relative">
              compassionate
              <span className="absolute bottom-0 left-0 w-full h-1 bg-amber-400/40" />
            </span>
            <span className="text-slate-700"> guidance—</span>
            <span className="text-rose-600 font-extrabold relative">
              available 24/7
              <span className="absolute bottom-0 left-0 w-full h-1 bg-rose-400/40" />
            </span>
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-5 mb-14">
            <Link 
              href="/coach" 
              className="group relative inline-flex items-center gap-3 bg-gradient-to-r from-orange-600 via-orange-500 to-amber-600 text-white px-12 py-6 rounded-3xl font-black text-xl shadow-2xl shadow-orange-500/50 hover:shadow-orange-500/70 hover:scale-110 transition-all duration-300 border-3 border-orange-400/50 overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-amber-400 opacity-0 group-hover:opacity-20 transition-opacity" />
              <Sparkles className="w-7 h-7 animate-pulse relative z-10" />
              <span className="relative z-10">Start Free Session</span>
              <ArrowRight className="w-7 h-7 group-hover:translate-x-2 transition-transform relative z-10" />
            </Link>
            <button className="group inline-flex items-center gap-3 bg-white text-orange-700 px-12 py-6 rounded-3xl font-black text-xl border-3 border-orange-300 hover:border-orange-500 hover:bg-gradient-to-r hover:from-orange-50 hover:to-amber-50 hover:shadow-2xl hover:scale-105 transition-all duration-300 shadow-xl">
              <div className="w-7 h-7 rounded-full bg-gradient-to-r from-orange-500 to-amber-500 flex items-center justify-center">
                <svg className="w-4 h-4 text-white fill-white" viewBox="0 0 20 20">
                  <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                </svg>
              </div>
              <span>Watch Demo</span>
            </button>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-5 text-base">
            <div className="flex items-center gap-2.5 bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-3 rounded-full border-2 border-green-200 shadow-lg hover:shadow-xl hover:scale-105 transition-all">
              <Check className="w-5 h-5 text-green-600 stroke-[3]" />
              <span className="text-green-800 font-bold">No Credit Card</span>
            </div>
            <div className="flex items-center gap-2.5 bg-gradient-to-r from-blue-50 to-cyan-50 px-6 py-3 rounded-full border-2 border-blue-200 shadow-lg hover:shadow-xl hover:scale-105 transition-all">
              <Shield className="w-5 h-5 text-blue-600 stroke-[3]" />
              <span className="text-blue-800 font-bold">Private & Secure</span>
            </div>
            <div className="flex items-center gap-2.5 bg-gradient-to-r from-purple-50 to-violet-50 px-6 py-3 rounded-full border-2 border-purple-200 shadow-lg hover:shadow-xl hover:scale-105 transition-all">
              <Award className="w-5 h-5 text-purple-600 stroke-[3]" />
              <span className="text-purple-800 font-bold">Evidence-Based</span>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-8 mb-24">
          <StatCard icon={<Users className="w-8 h-8" />} value="10,000+" label="Happy Parents" color="from-blue-500 to-cyan-500" />
          <StatCard icon={<Clock className="w-8 h-8" />} value="24/7" label="Always Available" color="from-orange-500 to-amber-500" />
          <StatCard icon={<Star className="w-8 h-8" />} value="4.9/5" label="Average Rating" color="from-yellow-500 to-amber-500" />
        </div>

        {/* Features Grid */}
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8 mb-24 animate-slide-up">
          <FeatureCard 
            icon={<Heart className="w-9 h-9" />}
            title="Empathy First"
            description="Warm, judgment-free support that meets you exactly where you are in your parenting journey."
            gradient="from-rose-500 via-pink-500 to-rose-600"
            bgGradient="from-rose-50 to-pink-50"
            borderColor="border-rose-200"
            delay="0"
          />
          <FeatureCard 
            icon={<Shield className="w-9 h-9" />}
            title="Research-Backed"
            description="Every recommendation grounded in developmental psychology and vetted parenting research."
            gradient="from-orange-500 via-amber-500 to-orange-600"
            bgGradient="from-orange-50 to-amber-50"
            borderColor="border-orange-200"
            delay="100"
          />
          <FeatureCard 
            icon={<Zap className="w-9 h-9" />}
            title="Always Available"
            description="24/7 instant guidance when you're in the moment and need answers that can't wait."
            gradient="from-amber-500 via-yellow-500 to-amber-600"
            bgGradient="from-amber-50 to-yellow-50"
            borderColor="border-amber-200"
            delay="200"
          />
        </div>

        {/* Topics Section */}
        <div className="max-w-6xl mx-auto bg-white rounded-[2.5rem] shadow-2xl border-2 border-slate-100 p-12 md:p-16 animate-scale-in">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-100 to-amber-100 px-5 py-2 rounded-full mb-6 border border-orange-200">
              <Sparkles className="w-4 h-4 text-orange-600" />
              <span className="text-sm font-bold text-orange-800 tracking-wide">COMPREHENSIVE SUPPORT</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-black mb-5 text-slate-900">
              Topics We Help With
            </h2>
            <p className="text-slate-600 text-xl font-semibold">From daily routines to developmental milestones</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '😴', text: 'Sleep routines & bedtime struggles', gradient: 'from-blue-500 to-indigo-600' },
              { icon: '🤝', text: 'Sibling conflicts & rivalry', gradient: 'from-purple-500 to-pink-600' },
              { icon: '📱', text: 'Screen time & tech boundaries', gradient: 'from-orange-500 to-red-600' },
              { icon: '😢', text: 'Emotional regulation & tantrums', gradient: 'from-rose-500 to-pink-600' },
              { icon: '📚', text: 'Learning motivation & focus', gradient: 'from-green-500 to-emerald-600' },
              { icon: '✋', text: 'Positive discipline strategies', gradient: 'from-amber-500 to-orange-600' },
              { icon: '🎯', text: 'Developmental milestones', gradient: 'from-cyan-500 to-blue-600' },
              { icon: '🔄', text: 'Transitions & routines', gradient: 'from-violet-500 to-purple-600' },
            ].map((topic, i) => (
              <div 
                key={i} 
                className={`group flex items-center gap-5 p-6 rounded-3xl bg-gradient-to-br ${topic.gradient} shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 border-2 border-white/50 cursor-pointer`}
              >
                <div className="text-5xl group-hover:scale-125 transition-transform drop-shadow-2xl">{topic.icon}</div>
                <span className="text-white font-bold text-lg md:text-xl leading-tight">{topic.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Final CTA */}
        <div className="max-w-4xl mx-auto text-center mt-24">
          <div className="bg-gradient-to-r from-orange-500 to-amber-500 rounded-[2.5rem] p-12 shadow-2xl border-2 border-orange-300/50">
            <h3 className="text-4xl md:text-5xl font-black text-white mb-6">Ready to Get Started?</h3>
            <p className="text-xl text-orange-50 mb-8 font-medium">Join thousands of parents getting evidence-based guidance every day</p>
            <Link 
              href="/coach"
              className="inline-flex items-center gap-3 bg-white text-orange-700 px-10 py-5 rounded-2xl font-black text-xl shadow-xl hover:shadow-2xl hover:scale-110 transition-all duration-300 border-2 border-orange-200"
            >
              <Sparkles className="w-6 h-6" />
              Start Your Free Session Now
              <ArrowRight className="w-6 h-6" />
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}

function StatCard({ icon, value, label, color }: {
  icon: React.ReactNode
  value: string
  label: string
  color: string
}) {
  return (
    <div className="bg-white rounded-3xl p-8 shadow-xl border-2 border-slate-100 hover:shadow-2xl hover:scale-105 transition-all duration-300 text-center">
      <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${color} text-white mb-4 shadow-lg`}>
        {icon}
      </div>
      <div className={`text-5xl font-black bg-gradient-to-r ${color} bg-clip-text text-transparent mb-2`}>{value}</div>
      <div className="text-slate-600 font-bold text-lg">{label}</div>
    </div>
  )
}

function FeatureCard({ icon, title, description, gradient, bgGradient, borderColor, delay }: {
  icon: React.ReactNode
  title: string
  description: string
  gradient: string
  bgGradient: string
  borderColor: string
  delay: string
}) {
  return (
    <div 
      className={`group bg-gradient-to-br ${bgGradient} rounded-3xl p-10 shadow-xl border-2 ${borderColor} hover:shadow-2xl hover:scale-105 transition-all duration-300 hover:-translate-y-2`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className={`inline-flex items-center justify-center w-18 h-18 rounded-3xl bg-gradient-to-br ${gradient} text-white mb-7 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-2xl p-4`}>
        {icon}
      </div>
      <h3 className="text-2xl font-black text-slate-900 mb-4 leading-tight">{title}</h3>
      <p className="text-slate-700 leading-relaxed font-medium text-lg">{description}</p>
    </div>
  )
}
