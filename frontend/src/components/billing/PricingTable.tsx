import { useState } from 'react';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api/client';

interface PricingTier {
  name: string;
  price: string;
  priceId: string;
  features: string[];
  popular?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    name: 'Free',
    price: '$0',
    priceId: '',
    features: [
      '1 website',
      'Basic templates',
      'Community support',
      '100 MB storage',
    ],
  },
  {
    name: 'Pro',
    price: '$19',
    priceId: 'price_pro_monthly',
    popular: true,
    features: [
      '10 websites',
      'Premium templates',
      'Priority support',
      '10 GB storage',
      'Custom domain',
      'AI editing',
    ],
  },
  {
    name: 'Enterprise',
    price: '$99',
    priceId: 'price_enterprise_monthly',
    features: [
      'Unlimited websites',
      'All templates',
      '24/7 support',
      '100 GB storage',
      'Custom domain',
      'AI editing',
      'White-label',
      'API access',
    ],
  },
];

export function PricingTable() {
  const [loading, setLoading] = useState<string | null>(null);

  const handleSubscribe = async (priceId: string) => {
    if (!priceId) return; // Free tier

    setLoading(priceId);
    try {
      const response = await apiClient.post('/billing/checkout', {
        email: 'user@example.com', // TODO: Get from auth context
        price_id: priceId,
        success_url: `${window.location.origin}/dashboard?success=true`,
        cancel_url: `${window.location.origin}/pricing?canceled=true`,
      });

      // Redirect to Stripe checkout
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Error creating checkout session:', error);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4">Choose Your Plan</h2>
        <p className="text-muted-foreground text-lg">
          Select the perfect plan for your needs
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {pricingTiers.map((tier) => (
          <Card
            key={tier.name}
            className={`relative ${
              tier.popular
                ? 'border-primary shadow-lg scale-105'
                : 'border-border'
            }`}
          >
            {tier.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
            )}

            <CardHeader>
              <CardTitle className="text-2xl">{tier.name}</CardTitle>
              <CardDescription>
                <span className="text-4xl font-bold text-foreground">
                  {tier.price}
                </span>
                <span className="text-muted-foreground">/month</span>
              </CardDescription>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-primary flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>

            <CardFooter>
              <Button
                className="w-full"
                variant={tier.popular ? 'default' : 'outline'}
                onClick={() => handleSubscribe(tier.priceId)}
                disabled={loading === tier.priceId}
              >
                {loading === tier.priceId
                  ? 'Loading...'
                  : tier.priceId
                  ? 'Subscribe'
                  : 'Get Started'}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
