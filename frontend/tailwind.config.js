/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: { DEFAULT: '#0E1726', soft: '#1B2740' },
        paper: '#EEF1F5',
        steel: '#5B6577',
        line: '#D5DBE4',
        signal: { DEFAULT: '#D8312B', dark: '#B22520' }, // tail-light red
        teal: { DEFAULT: '#0F8B8D', dark: '#0B6B6D' },   // indicator green-blue
        amber: { DEFAULT: '#F2A516' },                   // dashboard-warning amber
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        sans: ['"Instrument Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        road: { from: { backgroundPosition: '0 0' }, to: { backgroundPosition: '-96px 0' } },
        pop: { from: { opacity: 0, transform: 'translateY(8px) scale(.98)' }, to: { opacity: 1, transform: 'none' } },
      },
      animation: { road: 'road 2.4s linear infinite', pop: 'pop .22s ease-out' },
    },
  },
  plugins: [],
}
