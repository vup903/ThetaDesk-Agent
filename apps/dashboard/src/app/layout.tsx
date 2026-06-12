import type { Metadata } from "next";
import "@openuidev/react-ui/components.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Theta Desk Dashboard",
  description: "Autonomous options-income research dashboard"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
