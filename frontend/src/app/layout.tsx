import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Banco Ágil — Assistente Financeiro Inteligente",
  description:
    "Assistente virtual multi-agente do Banco Ágil. Serviços de crédito, câmbio e análise financeira com segurança e agilidade.",
  keywords: ["banco", "financeiro", "crédito", "câmbio", "assistente virtual", "IA"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
