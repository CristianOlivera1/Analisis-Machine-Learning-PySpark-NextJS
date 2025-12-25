import { SidebarProvider } from "@/components/ui/sidebar";
import AppSidebar from "../components/app-sidebar"; // Ajusta la ruta
import { Header } from "../components/header";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </SidebarProvider>
  );
}