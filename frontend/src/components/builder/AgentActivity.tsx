import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, Brain } from 'lucide-react';
import { cn } from '@/lib/utils';

export type AgentStep = {
  id: string;
  label: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  icon?: React.ElementType;
};

interface AgentActivityProps {
  steps: AgentStep[];
  isVisible: boolean;
}

export function AgentActivity({ steps, isVisible }: AgentActivityProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20, height: 0 }}
          animate={{ opacity: 1, y: 0, height: 'auto' }}
          exit={{ opacity: 0, y: 20, height: 0 }}
          className="overflow-hidden"
        >
          <div className="rounded-xl bg-black/40 border border-white/10 backdrop-blur-md p-4 space-y-4 shadow-2xl">
            <div className="flex items-center gap-2 text-primary/80 pb-2 border-b border-white/5">
              <Brain className="h-4 w-4" />
              <span className="text-xs font-medium uppercase tracking-wider">AI Processing</span>
            </div>
            
            <div className="space-y-3">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center gap-3">
                  <div className="relative flex items-center justify-center">
                    {step.status === 'completed' && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="h-5 w-5 rounded-full bg-green-500/20 flex items-center justify-center"
                      >
                        <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                      </motion.div>
                    )}
                    {step.status === 'running' && (
                      <div className="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center relative">
                        <Loader2 className="h-3.5 w-3.5 text-primary animate-spin" />
                        <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
                      </div>
                    )}
                    {step.status === 'pending' && (
                      <div className="h-5 w-5 rounded-full bg-white/5 flex items-center justify-center">
                        <Circle className="h-3.5 w-3.5 text-muted-foreground" />
                      </div>
                    )}
                    {step.status === 'failed' && (
                      <div className="h-5 w-5 rounded-full bg-red-500/20 flex items-center justify-center">
                        <div className="h-2 w-2 rounded-full bg-red-500" />
                      </div>
                    )}
                    
                    {/* Connector Line */}
                    {index < steps.length - 1 && (
                      <div className={cn(
                        "absolute top-6 left-1/2 w-px h-3 -translate-x-1/2",
                        step.status === 'completed' ? "bg-green-500/30" : "bg-white/5"
                      )} />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className={cn(
                      "text-sm font-medium transition-colors",
                      step.status === 'running' ? "text-white" : 
                      step.status === 'completed' ? "text-white/60" : "text-muted-foreground"
                    )}>
                      {step.label}
                    </p>
                  </div>
                  
                  {step.icon && (
                    <step.icon className={cn(
                      "h-4 w-4 transition-colors",
                      step.status === 'running' ? "text-primary" : "text-white/10"
                    )} />
                  )}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
