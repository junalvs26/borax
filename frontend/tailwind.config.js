/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'borax-bg': '#0B0913',
        'borax-surface': '#14111F',
        'borax-input': '#0F0D18',
        'borax-border': '#2B2443',
        'borax-purple': '#6D28FF',
        'borax-purple-dark': '#4B13C7',
        'borax-lilac-light': '#DFC8FF',
        'borax-gray-light': '#F4F4F6',
        'borax-gray-muted': '#B7B7C4',
      },
      backgroundImage: {
        'borax-gradient': 'linear-gradient(135deg, #5E17EB 0%, #C69BFF 100%)',
      },
      borderRadius: {
        'borax-card': '20px',
        'borax-input': '18px',
        'borax-btn': '16px',
      },
      letterSpacing: {
        'borax': '0.02em',
      },
      fontFamily: {
        sans: ['Inter', 'Geist', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
