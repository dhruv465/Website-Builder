import { useState } from 'react';
import AnimatedPage from '../components/shared/AnimatedPage';
import {
  AnimatedList,
  AnimatedListItem,
  AnimatedGrid,
  AnimatedGridItem,
  AnimatedCard,
  AnimatedButton,
  AnimatedSpinner,
  LoadingOverlay,
  SkeletonLoader,
  SkeletonText,
  SkeletonCard,
  ScrollReveal,
} from '../components/shared';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Sparkles, Zap, Shield, Rocket } from 'lucide-react';

export default function AnimationShowcasePage() {
  const [showOverlay, setShowOverlay] = useState(false);
  const [showSkeletons, setShowSkeletons] = useState(false);

  const features = [
    { icon: Sparkles, title: 'Feature 1', description: 'Amazing feature description' },
    { icon: Zap, title: 'Feature 2', description: 'Another great feature' },
    { icon: Shield, title: 'Feature 3', description: 'Secure and reliable' },
    { icon: Rocket, title: 'Feature 4', description: 'Fast and efficient' },
  ];

  return (
    <AnimatedPage className="container mx-auto p-6 md:p-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">Animation Showcase</h1>
        <p className="text-muted-foreground">
          Demonstrating all animation components and patterns
        </p>
      </div>

      {/* Animated Buttons */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold">Animated Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <AnimatedButton>Primary Button</AnimatedButton>
          <AnimatedButton variant="secondary">Secondary Button</AnimatedButton>
          <AnimatedButton variant="outline">Outline Button</AnimatedButton>
          <AnimatedButton variant="ghost">Ghost Button</AnimatedButton>
          <AnimatedButton variant="destructive">Destructive Button</AnimatedButton>
        </div>
      </section>

      {/* Animated Cards */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold">Animated Cards</h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatedCard enableHover>
            <CardHeader>
              <CardTitle>Hover Card</CardTitle>
              <CardDescription>Hover over me to see the animation</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                This card has hover and scale animations
              </p>
            </CardContent>
          </AnimatedCard>

          <AnimatedCard enableHover onClick={() => alert('Card clicked!')}>
            <CardHeader>
              <CardTitle>Clickable Card</CardTitle>
              <CardDescription>Click me to trigger an action</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                This card has tap animations too
              </p>
            </CardContent>
          </AnimatedCard>

          <AnimatedCard enableHover>
            <CardHeader>
              <CardTitle>Another Card</CardTitle>
              <CardDescription>With smooth animations</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                All cards respect reduced motion preferences
              </p>
            </CardContent>
          </AnimatedCard>
        </div>
      </section>

      {/* Animated Grid */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold">Animated Grid (Staggered)</h2>
        <AnimatedGrid className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <AnimatedGridItem key={index}>
              <Card>
                <CardHeader>
                  <feature.icon className="mb-2 h-8 w-8 text-primary" />
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            </AnimatedGridItem>
          ))}
        </AnimatedGrid>
      </section>

      {/* Animated List */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold">Animated List (Staggered)</h2>
        <AnimatedList className="space-y-4">
          {['First item', 'Second item', 'Third item', 'Fourth item', 'Fifth item'].map(
            (item, index) => (
              <AnimatedListItem key={index}>
                <Card>
                  <CardContent className="flex items-center gap-4 p-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{item}</p>
                      <p className="text-sm text-muted-foreground">
                        This item animates in sequence
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </AnimatedListItem>
            )
          )}
        </AnimatedList>
      </section>

      {/* Loading States */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold">Loading States</h2>
        <div className="space-y-6">
          <div>
            <h3 className="mb-2 text-lg font-medium">Spinners</h3>
            <div className="flex items-center gap-8">
              <div className="flex flex-col items-center gap-2">
                <AnimatedSpinner size="sm" />
                <span className="text-xs text-muted-foreground">Small</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <AnimatedSpinner size="md" />
                <span className="text-xs text-muted-foreground">Medium</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <AnimatedSpinner size="lg" />
                <span className="text-xs text-muted-foreground">Large</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="mb-2 text-lg font-medium">Skeleton Loaders</h3>
            <div className="space-y-4">
              <div>
                <p className="mb-2 text-sm text-muted-foreground">Text skeleton:</p>
                <SkeletonText lines={3} />
              </div>
              <div>
                <p className="mb-2 text-sm text-muted-foreground">Card skeleton:</p>
                <SkeletonCard />
              </div>
              <div>
                <p className="mb-2 text-sm text-muted-foreground">Custom skeletons:</p>
                <div className="flex gap-4">
                  <SkeletonLoader variant="circular" width="4rem" height="4rem" />
                  <div className="flex-1 space-y-2">
                    <SkeletonLoader height="1rem" width="60%" />
                    <SkeletonLoader height="0.75rem" width="80%" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="mb-2 text-lg font-medium">Loading Overlay</h3>
            <div className="flex gap-4">
              <Button onClick={() => setShowOverlay(true)}>Show Loading Overlay</Button>
              <Button onClick={() => setShowSkeletons(!showSkeletons)}>
                Toggle Skeletons
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Scroll Reveal */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold">Scroll-Triggered Animations</h2>
        <p className="mb-6 text-muted-foreground">
          Scroll down to see elements animate into view
        </p>

        <div className="space-y-12">
          <ScrollReveal direction="up">
            <Card>
              <CardHeader>
                <CardTitle>Fade Up Animation</CardTitle>
                <CardDescription>This card fades in from the bottom</CardDescription>
              </CardHeader>
            </Card>
          </ScrollReveal>

          <ScrollReveal direction="left">
            <Card>
              <CardHeader>
                <CardTitle>Slide Left Animation</CardTitle>
                <CardDescription>This card slides in from the left</CardDescription>
              </CardHeader>
            </Card>
          </ScrollReveal>

          <ScrollReveal direction="right">
            <Card>
              <CardHeader>
                <CardTitle>Slide Right Animation</CardTitle>
                <CardDescription>This card slides in from the right</CardDescription>
              </CardHeader>
            </Card>
          </ScrollReveal>

          <ScrollReveal direction="scale">
            <Card>
              <CardHeader>
                <CardTitle>Scale Animation</CardTitle>
                <CardDescription>This card scales up when visible</CardDescription>
              </CardHeader>
            </Card>
          </ScrollReveal>

          <div className="grid gap-6 sm:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <ScrollReveal key={i} direction="up" delay={i * 0.1}>
                <Card>
                  <CardHeader>
                    <CardTitle>Staggered {i}</CardTitle>
                    <CardDescription>With delay</CardDescription>
                  </CardHeader>
                </Card>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Conditional Rendering */}
      {showSkeletons && (
        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-semibold">Skeleton Loading State</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </section>
      )}

      {/* Loading Overlay */}
      <LoadingOverlay
        isLoading={showOverlay}
        message="Loading amazing content..."
      />

      {showOverlay && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center">
          <Button onClick={() => setShowOverlay(false)} variant="outline">
            Close Overlay
          </Button>
        </div>
      )}
    </AnimatedPage>
  );
}
