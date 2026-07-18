import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#15120F",
          soft: "#1E1A15",
          border: "#2C2620",
        },
        parchment: {
          DEFAULT: "#F5EFE2",
          dim: "#EBE3D0",
        },
        ember: {
          DEFAULT: "#C1502E",
          light: "#D97A5C",
          dark: "#96391F",
        },
        moss: {
          DEFAULT: "#4B6B4F",
          light: "#6B8A6E",
        },
        gold: {
          DEFAULT: "#C79A3B",
          light: "#DFC073",
        },
        slate: {
          DEFAULT: "#6B6459",
          light: "#948C7E",
        },
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "Georgia", "serif"],
        body: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-plex-mono)", "monospace"],
        reading: ["var(--font-newsreader)", "Georgia", "serif"],
      },
      borderRadius: {
        sm: "2px",
        DEFAULT: "4px",
        md: "6px",
      },
    },
  },
  plugins: [],
};

export default config;
