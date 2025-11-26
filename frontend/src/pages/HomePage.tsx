import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '@/lib/context/SessionContext';
import { useWorkflow } from '@/lib/context/WorkflowContext';
import { Button } from '@/components/ui/button';
import { FeatureCard } from '@/components/ui/FeatureCard';
import { PricingCard } from '@/components/ui/PricingCard';
import { Sparkles, Zap, Code, Eye, Layers, Shield, Play } from 'lucide-react';

export default function HomePage() {
  const { session } = useSession();
  const { startCreateWorkflow } = useWorkflow();
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    if (!session) {
      console.error('No active session');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await startCreateWorkflow({
        session_id: session.id,
        requirements: prompt,
      });

      if (response) {
        navigate('/builder');
      }
    } catch (error) {
      console.error('Failed to start workflow:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary/30 font-sans">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[120px] animate-pulse-glow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-accent/20 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay" />
      </div>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <span className="font-serif text-2xl font-medium tracking-tight">Velora</span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors uppercase tracking-widest text-[10px]">Features</a>
            <a href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors uppercase tracking-widest text-[10px]">Pricing</a>
            <a href="#resources" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors uppercase tracking-widest text-[10px]">Resources</a>
          </nav>
          <div className="flex items-center gap-4">
            <Button variant="ghost" className="hidden sm:flex">Sign In</Button>
            <Button variant="pill" size="sm" className="shadow-outer-glow">Start for Free</Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 pt-32 pb-20 lg:pt-48 lg:pb-32">
        <div className="container mx-auto px-6">
          {/* Hero Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center mb-32">
            {/* Visual - Left Side (Swapped) */}
            <div className="lg:col-span-6 relative order-2 lg:order-1 flex justify-center">
               <div className="relative w-full max-w-[500px] aspect-square">
                  {/* Main Glow */}
                  <div className="absolute inset-0 bg-gradient-to-tr from-primary/40 via-accent/20 to-transparent rounded-full blur-[100px] animate-pulse-glow" />
                  
                  {/* Glass Stack Visual */}
                  <div className="absolute inset-0 flex items-center justify-center">
                     {/* Back Card */}
                     <div className="absolute w-3/4 h-3/4 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-md transform -rotate-6 translate-y-4 opacity-60 animate-float" style={{ animationDelay: '0s' }} />
                     
                     {/* Middle Card */}
                     <div className="absolute w-3/4 h-3/4 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-md transform rotate-3 translate-y-2 opacity-80 animate-float" style={{ animationDelay: '1s' }} />
                     
                     {/* Front Card */}
                     <div className="relative w-3/4 h-3/4 bg-black/40 border border-white/10 rounded-3xl backdrop-blur-xl shadow-2xl flex flex-col overflow-hidden animate-float" style={{ animationDelay: '2s' }}>
                        {/* Mock Header */}
                        <div className="h-12 border-b border-white/10 flex items-center px-4 gap-2">
                           <div className="flex gap-1.5">
                              <div className="h-2.5 w-2.5 rounded-full bg-red-500/50" />
                              <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/50" />
                              <div className="h-2.5 w-2.5 rounded-full bg-green-500/50" />
                           </div>
                        </div>
                        {/* Mock Content */}
                        <div className="flex-1 p-6 space-y-4">
                           <div className="h-8 w-3/4 bg-white/10 rounded-lg" />
                           <div className="space-y-2">
                              <div className="h-4 w-full bg-white/5 rounded" />
                              <div className="h-4 w-5/6 bg-white/5 rounded" />
                              <div className="h-4 w-4/6 bg-white/5 rounded" />
                           </div>
                           <div className="flex gap-3 pt-2">
                              <div className="h-20 flex-1 bg-primary/10 rounded-lg border border-primary/20" />
                              <div className="h-20 flex-1 bg-white/5 rounded-lg border border-white/5" />
                           </div>
                        </div>
                        
                        {/* Floating Badge */}
                        <div className="absolute bottom-6 right-6 px-3 py-1.5 bg-primary text-white text-xs font-medium rounded-full shadow-lg shadow-primary/30 flex items-center gap-1.5">
                           <Sparkles className="h-3 w-3" />
                           <span>AI Generated</span>
                        </div>
                     </div>
                  </div>
               </div>
            </div>

            {/* Content - Right Side (Swapped) */}
            <div className="lg:col-span-6 space-y-8 text-center lg:text-left order-1 lg:order-2">
              <div className="space-y-4">
                <h1 className="font-serif text-hero font-light tracking-tight leading-[1.05]">
                  Where <span className="italic font-normal bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_auto] animate-gradient">imagination</span> <br />
                  becomes code
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto lg:mx-0 font-light leading-relaxed">
                  Building with Velora is as simple as having a conversation. Just describe your idea, and watch it turn into a real product.
                </p>
              </div>

              {/* Input Area - Glass Capsule */}
              <div className="max-w-2xl mx-auto lg:mx-0 relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-accent rounded-full blur opacity-30 group-hover:opacity-60 transition duration-500" />
                <div className="relative bg-black/60 backdrop-blur-xl rounded-full border border-white/10 p-2 shadow-2xl flex items-center">
                  <div className="pl-6 pr-4 py-2 flex-1">
                    <input
                      type="text"
                      placeholder="Tell us what you want..."
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleGenerate();
                      }}
                      className="w-full bg-transparent border-none text-lg placeholder:text-white/30 focus:outline-none focus:ring-0 text-white"
                    />
                  </div>
                  <Button 
                    onClick={handleGenerate}
                    disabled={!prompt.trim() || isGenerating}
                    className="rounded-full px-8 py-6 bg-white text-black hover:bg-white/90 hover:scale-105 transition-all duration-300 shadow-lg shadow-white/10"
                  >
                    {isGenerating ? (
                      <Zap className="h-5 w-5 animate-pulse" />
                    ) : (
                      <span className="font-medium">Generate</span>
                    )}
                  </Button>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto lg:mx-0 pt-4">
                 <div className="flex-1 p-4 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-colors">
                    <h3 className="font-medium mb-1 flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-primary" />
                      AI builds your foundation
                    </h3>
                    <p className="text-sm text-muted-foreground">React + TypeScript + Supabase ready in seconds.</p>
                 </div>
                 <div className="flex-1 p-4 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-colors">
                    <h3 className="font-medium mb-1 flex items-center gap-2">
                      <Code className="h-4 w-4 text-accent" />
                      Clean Code Export
                    </h3>
                    <p className="text-sm text-muted-foreground">Production-ready code you can actually read.</p>
                 </div>
              </div>

            </div>
          </div>

          {/* Features Section */}
          <div id="features" className="mt-48">
             <div className="text-center mb-20 space-y-4">
                <h2 className="font-serif text-5xl">Features that <span className="italic">speed up</span> <br /> your workflow</h2>
                <p className="text-muted-foreground max-w-2xl mx-auto">Everything you need to go from idea to production without the setup, boilerplate, or headaches.</p>
             </div>
             
             <div className="flex flex-wrap justify-center gap-8">
                {/* Chat to Build */}
                <FeatureCard 
                   title="Chat to build"
                   description="Describe screens, flows, or changes. Create a modern analytics dashboard tracking website performance."
                   className="w-full md:w-[calc(33.333%-1.5rem)]"
                >
                   <div className="p-4 space-y-3">
                      <div className="flex justify-end">
                         <div className="bg-white/10 backdrop-blur-md rounded-2xl rounded-tr-sm px-4 py-2 text-xs text-white/90 max-w-[80%] border border-white/5">
                            Create a modern analytics dashboard...
                         </div>
                      </div>
                      <div className="flex justify-start">
                         <div className="bg-primary/20 backdrop-blur-md rounded-2xl rounded-tl-sm px-4 py-3 text-xs text-white/90 max-w-[90%] border border-primary/20 shadow-lg shadow-primary/5">
                            <div className="flex items-center gap-2 mb-2 opacity-50">
                               <Sparkles className="h-3 w-3" />
                               <span>Velora AI</span>
                            </div>
                            I'll create a modern analytics dashboard with beautiful charts, key metrics, and a professional dark theme design.
                         </div>
                      </div>
                      <div className="relative mt-4">
                         <div className="h-10 w-full bg-white/5 rounded-full border border-white/10 flex items-center px-4 text-xs text-white/30">
                            Ask me anything...
                         </div>
                         <div className="absolute right-1 top-1 h-8 w-8 bg-primary rounded-full flex items-center justify-center shadow-lg shadow-primary/20">
                            <Sparkles className="h-4 w-4 text-white" />
                         </div>
                      </div>
                   </div>
                </FeatureCard>

                {/* Live Preview */}
                <FeatureCard 
                   title="Live preview"
                   description="See updates in seconds. Watch your app come to life as you type."
                   className="w-full md:w-[calc(33.333%-1.5rem)]"
                >
                   <div className="relative h-48 w-full bg-black/40 flex items-center justify-center overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-10" />
                      
                      {/* Abstract Dashboard UI */}
                      <div className="w-[90%] h-[90%] bg-white/5 rounded-xl border border-white/10 p-3 space-y-3 transform rotate-x-12 perspective-1000">
                         <div className="flex gap-2">
                            <div className="h-2 w-2 rounded-full bg-red-500/50" />
                            <div className="h-2 w-2 rounded-full bg-yellow-500/50" />
                            <div className="h-2 w-2 rounded-full bg-green-500/50" />
                         </div>
                         <div className="grid grid-cols-2 gap-2">
                            <div className="h-16 rounded-lg bg-white/5 border border-white/5" />
                            <div className="h-16 rounded-lg bg-white/5 border border-white/5" />
                            <div className="h-16 rounded-lg bg-white/5 border border-white/5" />
                            <div className="h-16 rounded-lg bg-white/5 border border-white/5" />
                         </div>
                      </div>

                      {/* Floating Prompt */}
                      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 bg-black/80 backdrop-blur-xl border border-white/10 px-4 py-2 rounded-full flex items-center gap-2 shadow-2xl">
                         <span className="text-[10px] text-white/80">Create modern analytics...</span>
                         <Zap className="h-3 w-3 text-primary animate-pulse" />
                      </div>
                   </div>
                </FeatureCard>

                {/* Edit in Place */}
                <FeatureCard 
                   title="Edit in place"
                   description="Click components to refine instantly. Direct manipulation for pixel-perfect control."
                   className="w-full md:w-[calc(33.333%-1.5rem)]"
                >
                   <div className="p-4 relative">
                      <div className="grid grid-cols-2 gap-3 opacity-50">
                         <div className="h-20 rounded-lg bg-white/5 border border-white/5" />
                         <div className="h-20 rounded-lg bg-white/5 border border-white/5" />
                      </div>
                      
                      {/* Selection Overlay */}
                      <div className="absolute top-4 left-4 w-[calc(50%-12px)] h-20 rounded-lg border-2 border-primary shadow-[0_0_20px_rgba(111,43,220,0.3)] z-10 flex items-end justify-end p-2">
                         <div className="bg-primary text-white text-[10px] px-2 py-0.5 rounded-md font-medium">Card</div>
                      </div>

                      {/* Toolbar */}
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/90 border border-white/10 rounded-lg p-1.5 flex gap-2 shadow-xl">
                         <div className="h-6 w-6 rounded bg-white/10 hover:bg-primary/50 transition-colors flex items-center justify-center"><Layers className="h-3 w-3" /></div>
                         <div className="h-6 w-6 rounded bg-white/10 hover:bg-primary/50 transition-colors flex items-center justify-center"><Eye className="h-3 w-3" /></div>
                         <div className="h-6 w-6 rounded bg-white/10 hover:bg-primary/50 transition-colors flex items-center justify-center"><Code className="h-3 w-3" /></div>
                      </div>
                   </div>
                </FeatureCard>
             
                {/* Clean Code */}
                <FeatureCard 
                   title="Clean code export"
                   description="Human-readable, production-ready. No vendor lock-in."
                   className="w-full md:w-[calc(33.333%-1.5rem)]"
                >
                   <div className="relative h-full min-h-[160px] bg-[#0A0A0A] rounded-xl border border-white/5 p-4 font-mono text-xs overflow-hidden">
                      <div className="flex gap-1.5 mb-4">
                         <div className="h-2.5 w-2.5 rounded-full bg-[#FF5F56]" />
                         <div className="h-2.5 w-2.5 rounded-full bg-[#FFBD2E]" />
                         <div className="h-2.5 w-2.5 rounded-full bg-[#27C93F]" />
                      </div>
                      <div className="space-y-1 text-white/50">
                         <div className="flex"><span className="text-primary mr-2">import</span> <span className="text-white">React</span> <span className="text-primary mx-2">from</span> <span className="text-accent">'react'</span>;</div>
                         <div className="flex"><span className="text-primary mr-2">import</span> <span className="text-white">{'{'} Button {'}'}</span> <span className="text-primary mx-2">from</span> <span className="text-accent">'@/components/ui/button'</span>;</div>
                         <div className="h-2" />
                         <div className="flex"><span className="text-primary mr-2">export default function</span> <span className="text-yellow-400">Dashboard</span>() {'{'}</div>
                         <div className="flex pl-4"><span className="text-primary mr-2">return</span> (</div>
                         <div className="flex pl-8"><span className="text-white">{'<'}div className="p-6 bg-background"{'>'}</span></div>
                         <div className="flex pl-12"><span className="text-white">{'<'}h1{'>'}Analytics{'<'}/h1{'>'}</span></div>
                         <div className="flex pl-8"><span className="text-white">{'<'}/div{'>'}</span></div>
                         <div className="flex pl-4">);</div>
                         <div>{'}'}</div>
                      </div>
                      <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#0A0A0A] to-transparent" />
                   </div>
                </FeatureCard>

                {/* Safe Changes */}
                <FeatureCard 
                   title="Safe changes"
                   description="Review diffs before applying. Version control built-in."
                   className="w-full md:w-[calc(33.333%-1.5rem)]"
                >
                   <div className="relative h-full min-h-[160px] flex items-center justify-center">
                      <div className="w-full max-w-sm bg-black/40 border border-white/10 rounded-xl p-4 backdrop-blur-md">
                         <div className="flex items-center justify-between mb-4">
                            <span className="text-xs font-medium text-white/60">Website Settings</span>
                            <div className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                         </div>
                         <div className="space-y-3">
                            <div className="space-y-1">
                               <div className="text-[10px] text-white/40">Title</div>
                               <div className="h-8 bg-white/5 rounded border border-white/5 flex items-center px-3 text-xs text-white/80">
                                  My Awesome Project
                               </div>
                            </div>
                            <div className="space-y-1">
                               <div className="text-[10px] text-white/40">Domain</div>
                               <div className="flex gap-2">
                                  <div className="h-8 flex-1 bg-white/5 rounded border border-white/5 flex items-center px-3 text-xs text-white/80">
                                     project-alpha.velora.app
                                  </div>
                                  <div className="h-8 w-8 bg-primary rounded flex items-center justify-center shadow-lg shadow-primary/20">
                                     <Shield className="h-3 w-3 text-white" />
                                  </div>
                               </div>
                            </div>
                         </div>
                      </div>
                   </div>
                </FeatureCard>
             </div>
          </div>
          
          {/* CTA Section */}
          <div className="mt-48 relative rounded-3xl overflow-hidden">
             <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent opacity-20" />
             <div className="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay" />
             <div className="relative z-10 py-32 px-8 text-center space-y-8">
                <h2 className="font-serif text-5xl md:text-6xl">Your idea deserves <span className="italic">better</span> <br /> than <span className="italic">boilerplate</span></h2>
                <p className="text-muted-foreground max-w-xl mx-auto">Don't waste weeks on boilerplate. From the very first prompt, Velora gives you clean code, instant previews, and full control.</p>
                <div className="flex items-center justify-center gap-4">
                   <Button variant="pill" size="lg" className="shadow-xl shadow-primary/20">Start for Free</Button>
                   <Button variant="ghost" className="gap-2"><Play className="h-4 w-4" /> Watch Demo</Button>
                </div>
             </div>
          </div>
          
          {/* Pricing Section */}
          <div id="pricing" className="mt-48 mb-32">
             <div className="text-center mb-20 space-y-4">
                <h2 className="font-serif text-5xl">The <span className="italic">future</span> of building, <br /> priced simply</h2>
                <p className="text-muted-foreground">Start free, scale as you grow. No hidden fees, no lock-in.</p>
             </div>
             
             <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                <PricingCard 
                   name="Free"
                   price="$0"
                   description="For starters and explorers"
                   features={["3 active projects", "Community support", "Public previews"]}
                />
                <PricingCard 
                   name="Starter"
                   price="$25"
                   description="For builders who want unlimited freedom"
                   features={["Unlimited projects", "Real-time dashboard", "Private repositories", "Custom domains", "Priority support"]}
                   popular
                   ctaText="Start for Free"
                />
                <PricingCard 
                   name="Team"
                   price="$99"
                   description="For growing teams who build together"
                   features={["All Pro features", "Multi-user collaboration", "Role-based access control", "SSO & audit logs", "Dedicated support"]}
                   ctaText="Contact Sales"
                />
             </div>
          </div>
          
        </div>
      </main>
      
      {/* Footer */}
      {/* Footer */}
      <footer className="relative border-t border-white/5 bg-black pt-20 pb-10 overflow-hidden">
         {/* Large Background Text */}
         <div className="absolute bottom-0 left-0 right-0 pointer-events-none select-none flex justify-center overflow-hidden">
            <h1 className="text-[20vw] font-bold leading-none text-white/[0.02] tracking-tighter translate-y-[30%]">
               VELORA
            </h1>
         </div>

         <div className="container mx-auto px-6 relative z-10">
            {/* Top Bar */}
            <div className="flex justify-between items-start mb-20">
               <div className="p-2 bg-white/5 rounded-lg border border-white/10">
                  <Layers className="h-6 w-6 text-white" />
               </div>
               <div className="flex gap-6">
                  <a href="#" className="text-muted-foreground hover:text-white transition-colors"><span className="sr-only">X</span><svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M13.6823 10.6218L20.2391 3H18.6854L12.9921 9.61788L8.44486 3H3.2002L10.0765 13.0074L3.2002 21H4.75404L10.7663 14.0113L15.5685 21H20.8131L13.6819 10.6218ZM11.5541 13.0956L10.8574 12.0991L5.31391 4.16971H7.70053L12.1742 10.5689L12.8709 11.5655L18.6861 19.8835H16.2995L11.5541 13.096V13.0956Z" /></svg></a>
                  <a href="#" className="text-muted-foreground hover:text-white transition-colors"><span className="sr-only">Instagram</span><svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.468 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd" /></svg></a>
               </div>
            </div>

            {/* Links Grid */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-24">
               {/* Product */}
               <div className="space-y-4">
                  <h4 className="font-medium text-white">Product</h4>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                     <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Student discount</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Solutions</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Connections</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Import from Figma</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Change Log</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
                  </ul>
               </div>

               {/* Company */}
               <div className="space-y-4">
                  <h4 className="font-medium text-white">Company</h4>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                     <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Press & Media</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Enterprise</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Trust Center</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Partnership</a></li>
                  </ul>
               </div>

               {/* Resources */}
               <div className="space-y-4">
                  <h4 className="font-medium text-white">Resources</h4>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                     <li><a href="#" className="hover:text-white transition-colors">Learn</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">How to Guide</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Videos</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Launched</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                  </ul>
               </div>

               {/* Legal */}
               <div className="space-y-4">
                  <h4 className="font-medium text-white">Legal</h4>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                     <li><a href="#" className="hover:text-white transition-colors">Cookie Settings</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Platform Rules</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Report Abuse</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Report Security Concerns</a></li>
                  </ul>
               </div>

               {/* Community */}
               <div className="space-y-4">
                  <h4 className="font-medium text-white">Community</h4>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                     <li><a href="#" className="hover:text-white transition-colors">Become a Partner</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Hire a Partner</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Affiliates</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Customer Success</a></li>
                     <li><a href="#" className="hover:text-white transition-colors">Templates</a></li>
                  </ul>
               </div>
            </div>
            
            {/* Bottom Bar */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8">
               <div className="flex items-center gap-2 text-sm text-white/80">
                  <span className="text-lg">🇺🇸</span>
                  <span>United States</span>
                  <svg className="h-4 w-4 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
               </div>
               <p className="text-sm text-muted-foreground">© Velora 2025. All Rights Reserved</p>
            </div>
         </div>
      </footer>
    </div>
  );
}
