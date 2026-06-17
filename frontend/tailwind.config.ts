import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: "#FF6B00",
        gold: "#F0B429",
        background: "#080B14",
        surface: "#0F1624",
        "surface-hover": "#161F35",
        border: "#1E2D4A",
        foreground: "#F0F4FF",
        muted: "#8896B3",
        "ev-positive": "#00D4AA",
        "ev-negative": "#FF4D6A",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        "gradient-primary": "linear-gradient(135deg, #FF6B00 0%, #F0B429 100%)",
        "gradient-radial-glow":
          "radial-gradient(circle at 50% 0%, rgba(255,107,0,0.12), transparent 60%)",
      },
      boxShadow: {
        glow: "0 0 16px 0 rgba(255,107,0,0.35)",
        "glow-gold": "0 0 16px 0 rgba(240,180,41,0.35)",
        "glow-positive": "0 0 14px 0 rgba(0,212,170,0.35)",
        "glow-negative": "0 0 14px 0 rgba(255,77,106,0.35)",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-700px 0" },
          "100%": { backgroundPosition: "700px 0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.6s infinite linear",
        "fade-in": "fade-in 0.3s ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
