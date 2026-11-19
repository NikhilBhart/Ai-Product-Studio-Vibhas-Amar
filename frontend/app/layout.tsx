import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'AI Product Studio', description: 'Turn a product idea into a designed, documented, tested application.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
