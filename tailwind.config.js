/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        head: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
      colors: {
        base:    '#080a0f',
        surface: '#0f1117',
        card:    '#161922',
        'card-hover': '#1d2130',
        input:   '#1a1e2a',
        accent:  '#00e5b0',
        blue:    '#4f8ef7',
        danger:  '#ff4d6d',
        warn:    '#fbbf24',
        't-primary':   '#eef0f5',
        't-secondary': '#8b92a8',
        't-muted':     '#4e5568',
        border:        'rgba(255,255,255,0.07)',
        'border-hover':'rgba(255,255,255,0.14)',
      },
      borderRadius: {
        sm: '8px', md: '12px', lg: '18px', xl: '24px',
      },
      animation: {
        'fade-up': 'fadeUp 0.5s ease both',
        'pulse-dot': 'pulseDot 1.5s ease-in-out infinite',
        'shimmer': 'shimmer 1.4s linear infinite',
        'spin-slow': 'spin 2s linear infinite',
      },
      keyframes: {
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        pulseDot: {
          '0%,100%': { transform: 'scale(1)', opacity: '1' },
          '50%':     { transform: 'scale(1.5)', opacity: '0.5' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-800px 0' },
          '100%': { backgroundPosition: '800px 0' },
        },
      },
      boxShadow: {
        card: '0 4px 24px rgba(0,0,0,0.4)',
        glow: '0 0 32px rgba(0,229,176,0.3)',
      },
      backdropBlur: { nav: '20px' },
    },
  },
  plugins: [],
}
