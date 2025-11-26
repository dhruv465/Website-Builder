import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '@/lib/context/SessionContext';
import { useWorkflow } from '@/lib/context/WorkflowContext';
import { Button } from '@/components/ui/button';
import { FeatureCard } from '@/components/ui/FeatureCard';
import { Sparkles, Zap, Code, Eye, Layers, Shield } from 'lucide-react';

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

      {/* Hero Section */}
      <main className="relative z-10 pt-20 pb-20 lg:pt-32 lg:pb-32">
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
          
        </div>
      </main>

      {/* Footer */}
      <footer className="relative bg-background h-[50vh] flex flex-col justify-end overflow-hidden border-t border-white/5">
         {/* Large Background Text */}
         <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden">
            <h1 
              className="text-[28vw] font-bold leading-none tracking-tighter text-transparent transform translate-y-[10%]" 
              style={{ 
                WebkitTextStroke: '1px rgba(255, 255, 255, 0.15)',
                maskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)',
                WebkitMaskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%)'
              }}
            >
               VELORA
            </h1>
         </div>

         <div className="container mx-auto px-6 pb-8 relative z-10 flex justify-between items-end">
            <div className="flex flex-col gap-2">
               <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-white/10 flex items-center justify-center">
                     <Sparkles className="h-4 w-4 text-white" />
                  </div>
                  <span className="font-serif text-xl font-medium tracking-tight text-white">Velora</span>
               </div>
               <p className="text-sm text-muted-foreground">Building the future of web development.</p>
            </div>
            <p className="text-xs text-muted-foreground/50">© 2025 Velora Inc.</p>
         </div>
      </footer>
    </div>
  );
}
