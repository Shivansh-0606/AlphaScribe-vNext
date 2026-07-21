import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import Link from "next/link";
import { APP_NAME } from "@/lib/config/constants";
import { AppProviders } from "@/providers/AppProviders";
import "./globals.css";

// Frozen typography (03 Typography System): IBM Plex Sans / IBM Plex Mono.
const plexSans = IBM_Plex_Sans({
  variable: "--font-plex-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

// Vision statement wording (frozen, docs/master-plan/02_Product_Vision.md) —
// used verbatim, not authored marketing copy.
const APP_DESCRIPTION =
  "AlphaScribe is an AI-native Equity Research Workspace designed to help investors " +
  "understand, analyze, compare, and monitor publicly traded companies without spending " +
  "hours searching through financial filings, earnings calls, news articles, and financial " +
  "statements.";

export const metadata: Metadata = {
  title: {
    default: APP_NAME,
    template: `%s · ${APP_NAME}`,
  },
  description: APP_DESCRIPTION,
  applicationName: APP_NAME,
};

// Single frozen light theme — no dark mode, no toggle (04.3 AD-1).
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  colorScheme: "light",
  themeColor: "#EEEAE2",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${plexSans.variable} ${plexMono.variable} h-full`}>
      <body className="flex min-h-full flex-col font-sans">
        <AppProviders>
          <a
            href="#main-content"
            className="focus:border-border focus:bg-surface focus:text-foreground sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:border focus:px-4 focus:py-2"
          >
            Skip to main content
          </a>
          <header className="border-border border-b" role="banner">
            <div className="mx-auto flex max-w-6xl items-center px-4 py-4 sm:px-6 lg:px-8">
              <Link
                href="/"
                aria-label={`${APP_NAME} home`}
                className="text-foreground font-mono text-sm font-medium tracking-tight"
              >
                {APP_NAME}
              </Link>
            </div>
          </header>
          {/* Container width/padding now lives in each template layout (PublicTemplate/
              WorkspaceTemplate) — the root shell owns only chrome placement (02.4 AD-4/AD-5). */}
          <main id="main-content" tabIndex={-1} className="flex flex-1 flex-col focus:outline-none">
            {children}
          </main>
        </AppProviders>
      </body>
    </html>
  );
}
