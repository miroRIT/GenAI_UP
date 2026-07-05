import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        civic: {
          ink: "#18212F",
          surface: "#F6F8FB",
          line: "#DCE3EC",
          blue: "#2563EB",
          green: "#059669",
          yellow: "#CA8A04",
          orange: "#EA580C",
          red: "#DC2626",
        },
      },
    },
  },
  plugins: [],
};

export default config;
