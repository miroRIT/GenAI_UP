const riskClasses: Record<string, string> = {
  Low: "bg-green-50 text-green-700 border-green-200",
  Medium: "bg-yellow-50 text-yellow-700 border-yellow-200",
  High: "bg-orange-50 text-orange-700 border-orange-200",
  Critical: "bg-red-50 text-red-700 border-red-200",
};

export function RiskBadge({ level }: { level: string }) {
  return (
    <span className={`rounded-md border px-2 py-1 text-xs font-semibold ${riskClasses[level] || riskClasses.Medium}`}>
      {level}
    </span>
  );
}
