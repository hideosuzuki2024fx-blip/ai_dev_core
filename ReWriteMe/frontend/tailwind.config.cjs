/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        background: '#F9FAFB',
        accent: '#5B9BD5',
        emotionPositive: '#FFD700',
        emotionNegative: '#C0392B'
      }
    }
  },
  plugins: []
};