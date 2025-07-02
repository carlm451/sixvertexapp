/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Orbitron', 'sans-serif'],
      },
      colors: {
        'borg-black': '#0a0a0a',
        'neon-green': '#39ff14',
        'anomaly-blue': '#00d8ff',
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        borg: {
          "primary": "#39ff14",
          "secondary": "#00d8ff",
          "accent": "#ffffff",
          "neutral": "#0a0a0a",
          "base-100": "#1a1a1a",
          "info": "#00d8ff",
          "success": "#39ff14",
          "warning": "#ffff00",
          "error": "#ff0000",
        },
      },
    ],
  },
}
