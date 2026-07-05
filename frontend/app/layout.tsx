import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CivicIQ",
  description: "AI Decision Intelligence Platform for Community Well-being",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
