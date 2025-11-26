import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface FeatureCardProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  image?: string;
  className?: string;
  large?: boolean;
  children?: ReactNode;
}

export function FeatureCard({ icon: Icon, title, description, image, className, large, children }: FeatureCardProps) {
  return (
    <div className={cn(
      "group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.02] p-8 transition-all duration-500 hover:bg-white/[0.04] hover:border-primary/30 hover:shadow-outer-glow",
      large ? "md:col-span-2" : "md:col-span-1",
      className
    )}>
      {/* Background Gradients */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-primary/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div className="relative z-10 flex flex-col h-full">
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 group-hover:text-white transition-colors">{title}</h3>
          <p className="text-sm text-muted-foreground group-hover:text-muted-foreground/80 transition-colors leading-relaxed">{description}</p>
        </div>

        <div className="mt-auto relative w-full">
          {children ? (
            <div className="w-full rounded-xl overflow-hidden border border-white/10 bg-black/20 backdrop-blur-sm shadow-2xl transition-transform duration-500 group-hover:scale-[1.02] group-hover:border-white/20">
              {children}
            </div>
          ) : image ? (
            <div className="rounded-lg overflow-hidden border border-white/10 shadow-2xl transform group-hover:scale-[1.02] transition-transform duration-500">
              <img src={image} alt={title} className="w-full h-auto opacity-80 group-hover:opacity-100 transition-opacity" />
            </div>
          ) : Icon ? (
            <div className="h-12 w-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-primary/20 group-hover:border-primary/30 transition-all duration-300">
              <Icon className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
