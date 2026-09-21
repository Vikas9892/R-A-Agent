import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0d1117",
        surface: "#161b22",
        "surface-hover": "#21262d",
        border: "#30363d",
        primary: "#238636",
        "primary-hover": "#2ea043",
        accent: "#58a6ff",
        textPrimary: "#f0f6fc",
        textSecondary: "#8b949e",
      },
    },
  },
  plugins: [],
};
export default config;
