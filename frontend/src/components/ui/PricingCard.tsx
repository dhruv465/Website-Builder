import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PricingCardProps {
  name: string;
  price: string;
  description: string;
  features: string[];
  popular?: boolean;
  ctaText?: string;
  onCtaClick?: () => void;
}

export function PricingCard({ name, price, description, features, popular, ctaText = "Start for Free", onCtaClick }: PricingCardProps) {
  return (
    <div className={cn(
      "relative rounded-3xl border p-8 transition-all duration-300 hover:scale-[1.02] flex flex-col h-full",
      popular 
        ? "bg-gradient-to-b from-[#6f2bdc] to-[#9346ff] border-transparent shadow-2xl shadow-primary/30 text-white" 
        : "bg-black/40 border-white/10 hover:bg-white/[0.02] hover:border-white/20 backdrop-blur-sm"
    )}>
      {popular && (
        <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-black/20 border border-white/10 text-xs font-medium text-white backdrop-blur-sm">
          Most Popular
        </div>
      )}

      <div className="mb-8">
        <h3 className={cn("text-lg font-medium mb-2", popular ? "text-white/90" : "text-white")}>{name}</h3>
        <div className="flex items-baseline gap-1 mb-4">
          <span className="text-5xl font-bold tracking-tight">{price}</span>
          {price !== 'Free' && <span className={cn("text-sm", popular ? "text-white/80" : "text-muted-foreground")}>/month</span>}
        </div>
        <p className={cn("text-sm leading-relaxed", popular ? "text-white/80" : "text-muted-foreground")}>{description}</p>
      </div>

      <Button 
        variant={popular ? "secondary" : "outline"} 
        className={cn(
          "w-full mb-8 h-12 text-base font-medium transition-all", 
          popular 
            ? "bg-white text-primary hover:bg-white/90 border-none shadow-lg" 
            : "border-white/10 bg-white/5 hover:bg-white/10 hover:text-white hover:border-white/20"
        )}
        onClick={onCtaClick}
      >
        {ctaText}
      </Button>

      <div className={cn("h-px w-full mb-8", popular ? "bg-white/20" : "bg-white/10")} />

      <ul className="space-y-4 mt-auto">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-3 text-sm">
            <Check className={cn("h-5 w-5 shrink-0 mt-0.5", popular ? "text-white" : "text-white/60")} />
            <span className={cn(popular ? "text-white/90" : "text-muted-foreground")}>{feature}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
