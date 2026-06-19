/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: '#FF9900', dark: '#E68A00', light: '#FFB84D' },
      },
    },
  },
  plugins: [],
}
