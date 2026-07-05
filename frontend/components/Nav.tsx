import Link from "next/link";
import { UserHeader } from "./UserHeader";

const links = [
  ["Dashboard", "/dashboard"],
  ["Demo", "/demo"],
  ["Map", "/map"],
  ["Districts", "/districts"],
  ["Alerts", "/alerts"],
  ["Assigned", "/alerts/assigned"],
  ["AI Assistant", "/assistant"],
  ["Operations", "/operations"],
  ["Exports", "/exports"],
  ["Anomalies", "/anomalies"],
  ["Forecasting", "/forecasting"],
  ["Upload", "/upload"],
  ["Admin", "/admin/data-refresh"],
  ["Providers", "/admin/providers"],
];

export function Nav() {
  return (
    <nav className="border-b border-civic-line bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <Link className="text-xl font-bold text-civic-ink" href="/">
          CivicIQ
        </Link>
        <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
          <div className="flex flex-wrap gap-2">
            {links.map(([label, href]) => (
              <Link className="rounded-md px-3 py-2 hover:bg-slate-100" href={href} key={href}>
                {label}
              </Link>
            ))}
          </div>
          <UserHeader />
        </div>
      </div>
    </nav>
  );
}
