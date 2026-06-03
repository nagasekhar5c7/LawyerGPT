import type { ReactNode } from "react";

interface AppLayoutProps {
  sidebar: ReactNode;
  children: ReactNode;
}

export default function AppLayout({ sidebar, children }: AppLayoutProps) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-50">
      <aside className="hidden md:flex w-72 flex-col bg-gray-900 text-white">
        {sidebar}
      </aside>
      <main className="flex flex-1 flex-col min-w-0">{children}</main>
    </div>
  );
}
