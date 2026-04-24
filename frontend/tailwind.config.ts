import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: "#10B981",
        sanctuary: "#020617",
        surface: "rgba(255,255,255,0.05)",
        "text-primary": "#F8FAFC",
        "text-muted": "rgba(248,250,252,0.5)",
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "sans-serif"],
      },
      borderRadius: {
        zen: "48px",
        button: "24px",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulse_brand: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(16,185,129,0)" },
          "50%": { boxShadow: "0 0 0 8px rgba(16,185,129,0.15)" },
        },
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out forwards",
        pulse_brand: "pulse_brand 2s infinite",
      },
    },
  },
  plugins: [],
};

export default config;
