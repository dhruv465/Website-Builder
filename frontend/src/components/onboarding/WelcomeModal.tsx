import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Sparkles, Rocket, Code2 } from 'lucide-react';

interface WelcomeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onStartTour: () => void;
  onSkip: () => void;
}

export function WelcomeModal({ open, onOpenChange, onStartTour, onSkip }: WelcomeModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            Welcome to AI Website Builder
          </DialogTitle>
          <DialogDescription className="text-base pt-2">
            Build your dream website in minutes using the power of AI. 
            Let us show you around to help you get started.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
            <div className="p-2 rounded-full bg-primary/10 text-primary mt-0.5">
              <Code2 className="h-4 w-4" />
            </div>
            <div>
              <h4 className="font-semibold">Natural Language Editing</h4>
              <p className="text-sm text-muted-foreground">
                Just describe what you want, and our AI will write the code for you.
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
            <div className="p-2 rounded-full bg-primary/10 text-primary mt-0.5">
              <Rocket className="h-4 w-4" />
            </div>
            <div>
              <h4 className="font-semibold">Instant Deployment</h4>
              <p className="text-sm text-muted-foreground">
                Deploy your site to the world with a single click.
              </p>
            </div>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button variant="outline" onClick={onSkip}>
            Skip Tour
          </Button>
          <Button onClick={onStartTour} className="gap-2">
            Start Tour
            <Rocket className="h-4 w-4" />
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
