import { Nav } from "@/components/Nav";
import { WardTable } from "@/components/WardTable";
import { getWards } from "@/lib/api";

export default async function WardsPage() {
  const wards = await getWards();
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">Ward Intelligence</p>
          <h1 className="text-3xl font-bold text-civic-ink">Risk Factors by Ward</h1>
        </header>
        <WardTable wards={wards} />
      </div>
    </main>
  );
}
