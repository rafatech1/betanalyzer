import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: "#FF6B00",
        background: "#0D0D0D",
        foreground: "#FFFFFF",
        "ev-positive": "#16A34A",
        "ev-negative": "#DC2626",
      },
    },
  },
  plugins: [],
};

export default config;
