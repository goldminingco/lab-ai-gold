import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta LAB AI GOLD
        gold: {
          50:  "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
        },
        dark: {
          900: "#0a0a0a",
          800: "#111111",
          700: "#1a1a1a",
          600: "#222222",
          500: "#2d2d2d",
        },
        // Prioridades dos pontos de análise
        priority: {
          high:   "#ef4444", // vermelho
          medium: "#eab308", // amarelo
          low:    "#22c55e", // verde
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backgroundImage: {
        "gold-gradient": "linear-gradient(135deg, #b45309 0%, #f59e0b 50%, #fcd34d 100%)",
        "dark-gradient": "linear-gradient(180deg, #0a0a0a 0%, #111111 100%)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow":       "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        glow: {
          from: { boxShadow: "0 0 10px #f59e0b44" },
          to:   { boxShadow: "0 0 30px #f59e0b99, 0 0 60px #f59e0b33" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
