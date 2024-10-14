"use client";

import { Inter } from "next/font/google";
import dynamic from "next/dynamic";
import "./globals.css";
import Header from "@/components/header";
import Footer from "@/components/footer";

const inter = Inter({ subsets: ["latin"] });

function InnerLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <main className="flex min-h-screen flex-col items-center px-2 lg:px-24 py-8 gap-2">
      <Header />
        <div className="z-10 w-full max-w-3xl flex flex-col gap-4 items-center justify-between">
          {children}
        </div>
      <Footer />
    </main>
  );
}

const DynamicInnerLayout = dynamic(() => Promise.resolve(InnerLayout), {
  ssr: false,
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <title>Captiv Designs: AI Chat</title>
      <body className={(inter.className = "bg-slate-200")}>
        <DynamicInnerLayout>{children}</DynamicInnerLayout>
      </body>
    </html>
  );
}

