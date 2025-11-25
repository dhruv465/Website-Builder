import { describe, it, expect } from 'vitest';
import {
  pageVariants,
  modalVariants,
  listContainerVariants,
  listItemVariants,
  getTransition,
  getVariants,
  createStaggerConfig,
  createViewportConfig,
  combineVariants,
  springTransition,
} from './animations';

describe('Animation Utilities', () => {
  describe('Variant Definitions', () => {
    it('defines page transition variants', () => {
      expect(pageVariants).toHaveProperty('initial');
      expect(pageVariants).toHaveProperty('animate');
      expect(pageVariants).toHaveProperty('exit');
      expect(pageVariants.initial).toEqual({ opacity: 0, y: 20 });
    });

    it('defines modal animation variants', () => {
      expect(modalVariants).toHaveProperty('hidden');
      expect(modalVariants).toHaveProperty('visible');
      expect(modalVariants).toHaveProperty('exit');
      expect(modalVariants.hidden).toEqual({ opacity: 0, scale: 0.95 });
    });

    it('defines list container variants with stagger', () => {
      expect(listContainerVariants).toHaveProperty('hidden');
      expect(listContainerVariants).toHaveProperty('visible');
      expect(listContainerVariants.visible).toHaveProperty('transition');
    });

    it('defines list item variants', () => {
      expect(listItemVariants).toHaveProperty('hidden');
      expect(listItemVariants).toHaveProperty('visible');
      expect(listItemVariants.hidden).toEqual({ opacity: 0, x: -20 });
    });
  });

  describe('getTransition', () => {
    it('returns normal transition when motion is not reduced', () => {
      const result = getTransition(false, springTransition);
      expect(result).toEqual(springTransition);
    });

    it('returns zero duration when motion is reduced', () => {
      const result = getTransition(true, springTransition);
      expect(result).toEqual({ duration: 0 });
    });

    it('uses default spring transition when not provided', () => {
      const result = getTransition(false);
      expect(result).toHaveProperty('type', 'spring');
    });

    it('handles null preference', () => {
      const result = getTransition(null, springTransition);
      expect(result).toEqual(springTransition);
    });
  });

  describe('getVariants', () => {
    it('returns original variants when motion is not reduced', () => {
      const result = getVariants(false, pageVariants);
      expect(result).toEqual(pageVariants);
    });

    it('removes motion from variants when reduced', () => {
      const result = getVariants(true, pageVariants);
      expect(result.initial).toHaveProperty('opacity');
      expect(result.initial).not.toHaveProperty('y');
    });

    it('handles null preference', () => {
      const result = getVariants(null, pageVariants);
      expect(result).toEqual(pageVariants);
    });
  });

  describe('createStaggerConfig', () => {
    it('creates stagger config with default values', () => {
      const config = createStaggerConfig();
      expect(config).toEqual({
        staggerChildren: 0.1,
        delayChildren: 0,
      });
    });

    it('creates stagger config with custom values', () => {
      const config = createStaggerConfig(0.2, 0.5);
      expect(config).toEqual({
        staggerChildren: 0.2,
        delayChildren: 0.5,
      });
    });
  });

  describe('createViewportConfig', () => {
    it('creates viewport config with default values', () => {
      const config = createViewportConfig();
      expect(config).toEqual({
        once: true,
        amount: 0.3,
      });
    });

    it('creates viewport config with custom values', () => {
      const config = createViewportConfig(false, 0.5);
      expect(config).toEqual({
        once: false,
        amount: 0.5,
      });
    });
  });

  describe('combineVariants', () => {
    it('combines multiple variant objects', () => {
      const variants1 = { initial: { opacity: 0 } };
      const variants2 = { animate: { opacity: 1 } };
      const result = combineVariants(variants1, variants2);

      expect(result).toEqual({
        initial: { opacity: 0 },
        animate: { opacity: 1 },
      });
    });

    it('later variants override earlier ones', () => {
      const variants1 = { initial: { opacity: 0 } };
      const variants2 = { initial: { opacity: 1 } };
      const result = combineVariants(variants1, variants2);

      expect(result.initial).toEqual({ opacity: 1 });
    });

    it('handles empty array', () => {
      const result = combineVariants();
      expect(result).toEqual({});
    });
  });

  describe('Transition Presets', () => {
    it('defines spring transition', () => {
      expect(springTransition).toEqual({
        type: 'spring',
        stiffness: 300,
        damping: 30,
      });
    });
  });
});
