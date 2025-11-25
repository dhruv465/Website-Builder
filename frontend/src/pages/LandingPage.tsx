import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import {
  ArrowRight,
  Sparkles,
  Zap,
  Shield,
  Code2,
  Palette,
  Rocket,
  Eye,
  CheckCircle2,
  Globe,
  Wand2,
  BarChart3,
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import AnimatedPage from '../components/shared/AnimatedPage';
import { ScrollReveal } from '../components/shared/ScrollReveal';
import { motion } from 'framer-motion';

export default function LandingPage() {
  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Generation',
      description:
        'Describe your website in natural language and watch AI bring it to life instantly',
    },
    {
      icon: Zap,
      title: 'Real-Time Preview',
      description:
        'See your changes instantly with live preview and WYSIWYG editing capabilities',
    },
    {
      icon: Shield,
      title: 'Built-in Audits',
      description:
        'Ensure accessibility, SEO, and performance with comprehensive automated audits',
    },
    {
      icon: Code2,
      title: 'Code Editor',
      description:
        'Advanced Monaco editor with syntax highlighting and IntelliSense for fine-tuning',
    },
    {
      icon: Palette,
      title: 'Theme Library',
      description:
        'Choose from beautiful pre-built themes or customize your own design system',
    },
    {
      icon: Rocket,
      title: 'One-Click Deploy',
      description:
        'Deploy your website to Vercel instantly with automatic SSL and CDN',
    },
  ];

  const exampleSites = [
    {
      title: 'E-Commerce Store',
      description: 'Modern online shop with product catalog and checkout',
      framework: 'React',
      style: 'Modern',
      image: '🛍️',
    },
    {
      title: 'Portfolio Website',
      description: 'Showcase your work with elegant design and animations',
      framework: 'Next.js',
      style: 'Minimal',
      image: '💼',
    },
    {
      title: 'Landing Page',
      description: 'High-converting landing page with call-to-actions',
      framework: 'HTML',
      style: 'Corporate',
      image: '🚀',
    },
    {
      title: 'Blog Platform',
      description: 'Content-focused blog with SEO optimization',
      framework: 'Vue',
      style: 'Creative',
      image: '📝',
    },
  ];

  const benefits = [
    {
      icon: Eye,
      title: 'Visual Editing',
      description: 'Edit content directly in the preview with instant feedback',
    },
    {
      icon: CheckCircle2,
      title: 'Quality Assurance',
      description: 'Automated testing for accessibility and performance standards',
    },
    {
      icon: Globe,
      title: 'Multi-Framework',
      description: 'Support for React, Vue, Next.js, and static HTML',
    },
    {
      icon: Wand2,
      title: 'Smart Suggestions',
      description: 'AI-powered recommendations for design improvements',
    },
    {
      icon: BarChart3,
      title: 'Analytics Ready',
      description: 'Built-in tracking and performance monitoring',
    },
    {
      icon: Rocket,
      title: 'Fast Deployment',
      description: 'Go live in seconds with optimized builds',
    },
  ];

  return (
    <>
      <Helmet>
        <title>Website Builder - Create Stunning Websites with AI</title>
        <meta
          name="description"
          content="Build beautiful, functional websites using AI-powered generation. No coding required. Real-time preview, built-in audits, and one-click deployment to Vercel."
        />
        <meta
          name="keywords"
          content="website builder, AI website generator, no-code, web development, React, Next.js, Vue, WYSIWYG editor, website deployment"
        />
        <meta property="og:title" content="Website Builder - Create Stunning Websites with AI" />
        <meta
          property="og:description"
          content="Transform your ideas into beautiful websites using natural language. AI-powered generation with real-time preview and instant deployment."
        />
        <meta name="twitter:title" content="Website Builder - Create Stunning Websites with AI" />
        <meta
          name="twitter:description"
          content="Transform your ideas into beautiful websites using natural language. AI-powered generation with real-time preview and instant deployment."
        />
      </Helmet>

      <AnimatedPage className="min-h-screen">
        {/* Hero Section */}
        <section className="container mx-auto px-4 py-20 md:py-32">
          <div className="flex flex-col items-center text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mb-6"
            >
              <Badge variant="secondary" className="mb-4 px-4 py-1.5 text-sm">
                ✨ AI-Powered Website Generation
              </Badge>
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
                Build Websites with
                <span className="block bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  AI-Powered Magic
                </span>
              </h1>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-8 max-w-2xl text-lg text-muted-foreground md:text-xl"
            >
              Transform your ideas into beautiful, functional websites using natural language. No
              coding required, just describe what you want and watch AI bring it to life.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="flex flex-col gap-4 sm:flex-row"
            >
              <Button asChild size="lg" className="gap-2">
                <Link to="/dashboard">
                  Get Started Free
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/dashboard/projects">View Examples</Link>
              </Button>
            </motion.div>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-6 text-sm text-muted-foreground"
            >
              No credit card required • Deploy in seconds • Free forever
            </motion.p>
          </div>
        </section>

        {/* Features Section */}
        <section className="border-t bg-muted/50 py-20">
          <div className="container mx-auto px-4">
            <ScrollReveal direction="up" className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">Everything You Need</h2>
              <p className="text-lg text-muted-foreground">
                Powerful features to help you create amazing websites
              </p>
            </ScrollReveal>

            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {features.map((feature, index) => (
                <ScrollReveal key={feature.title} direction="up" delay={index * 0.1}>
                  <Card className="h-full border-2 transition-all hover:border-primary/50 hover:shadow-lg">
                    <CardContent className="flex flex-col items-start p-6">
                      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                        <feature.icon className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="mb-2 text-xl font-semibold">{feature.title}</h3>
                      <p className="text-muted-foreground">{feature.description}</p>
                    </CardContent>
                  </Card>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>

        {/* Example Sites Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <ScrollReveal direction="up" className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">Built with AI</h2>
              <p className="text-lg text-muted-foreground">
                See what you can create in minutes, not hours
              </p>
            </ScrollReveal>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {exampleSites.map((site, index) => (
                <ScrollReveal key={site.title} direction="up" delay={index * 0.1}>
                  <Card className="group h-full overflow-hidden transition-all hover:shadow-xl">
                    <div className="flex h-40 items-center justify-center bg-gradient-to-br from-primary/20 to-primary/5 text-6xl transition-transform group-hover:scale-110">
                      {site.image}
                    </div>
                    <CardContent className="p-6">
                      <div className="mb-2 flex gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {site.framework}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {site.style}
                        </Badge>
                      </div>
                      <h3 className="mb-2 text-lg font-semibold">{site.title}</h3>
                      <p className="text-sm text-muted-foreground">{site.description}</p>
                    </CardContent>
                  </Card>
                </ScrollReveal>
              ))}
            </div>

            <ScrollReveal direction="up" className="mt-12 text-center">
              <Button asChild variant="outline" size="lg">
                <Link to="/dashboard/projects">
                  View All Examples
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </ScrollReveal>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="border-t bg-muted/50 py-20">
          <div className="container mx-auto px-4">
            <ScrollReveal direction="up" className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">Why Choose Our Platform</h2>
              <p className="text-lg text-muted-foreground">
                Built for creators, designers, and developers
              </p>
            </ScrollReveal>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {benefits.map((benefit, index) => (
                <ScrollReveal
                  key={benefit.title}
                  direction="up"
                  delay={index * 0.1}
                  className="flex gap-4"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <benefit.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="mb-1 font-semibold">{benefit.title}</h3>
                    <p className="text-sm text-muted-foreground">{benefit.description}</p>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="py-20">
          <div className="container mx-auto px-4">
            <ScrollReveal direction="up" className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">How It Works</h2>
              <p className="text-lg text-muted-foreground">
                From idea to live website in three simple steps
              </p>
            </ScrollReveal>

            <div className="grid gap-8 md:grid-cols-3">
              {[
                {
                  step: '1',
                  title: 'Describe Your Vision',
                  description:
                    'Tell us what you want using text, chat, or voice. Be as detailed or as simple as you like.',
                },
                {
                  step: '2',
                  title: 'AI Generates Your Site',
                  description:
                    'Watch as AI creates your website in real-time. Preview and edit with our visual editor.',
                },
                {
                  step: '3',
                  title: 'Deploy Instantly',
                  description:
                    'One click to deploy to Vercel. Your site goes live with SSL and global CDN.',
                },
              ].map((item, index) => (
                <ScrollReveal key={item.step} direction="up" delay={index * 0.15}>
                  <div className="relative flex flex-col items-center text-center">
                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
                      {item.step}
                    </div>
                    <h3 className="mb-2 text-xl font-semibold">{item.title}</h3>
                    <p className="text-muted-foreground">{item.description}</p>
                    {index < 2 && (
                      <div className="absolute -right-4 top-8 hidden h-0.5 w-8 bg-primary/30 md:block lg:w-16" />
                    )}
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="border-t py-20">
          <div className="container mx-auto px-4">
            <ScrollReveal direction="scale">
              <Card className="overflow-hidden border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
                <CardContent className="flex flex-col items-center p-12 text-center">
                  <h2 className="mb-4 text-3xl font-bold md:text-4xl">
                    Ready to Start Building?
                  </h2>
                  <p className="mb-8 max-w-2xl text-lg text-muted-foreground">
                    Join thousands of creators using AI to build their dream websites. No credit
                    card required, start creating in seconds.
                  </p>
                  <div className="flex flex-col gap-4 sm:flex-row">
                    <Button asChild size="lg" className="gap-2">
                      <Link to="/dashboard">
                        Start Creating Now
                        <ArrowRight className="h-5 w-5" />
                      </Link>
                    </Button>
                    <Button asChild variant="outline" size="lg">
                      <Link to="/dashboard/settings">View Pricing</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </ScrollReveal>
          </div>
        </section>
      </AnimatedPage>
    </>
  );
}
