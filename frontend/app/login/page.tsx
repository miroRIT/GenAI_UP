import { AuthPanel } from "@/components/AuthPanel";
import { Nav } from "@/components/Nav";

export default function LoginPage() {
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-xl px-5 py-8">
        <AuthPanel />
      </div>
    </main>
  );
}
