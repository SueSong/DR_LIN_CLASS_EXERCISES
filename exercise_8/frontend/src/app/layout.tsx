import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata = {
  title: "Legal Document Review - Exercise 8",
  description: "HITL Contract Redlining Orchestrator",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
