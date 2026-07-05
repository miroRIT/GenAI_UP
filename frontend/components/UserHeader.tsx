"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type StoredUser = {
  email: string;
  full_name: string;
  role: string;
  department?: string | null;
  district_id?: string | null;
};

export function UserHeader() {
  const [user, setUser] = useState<StoredUser | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("civiciq_user");
    setUser(stored ? JSON.parse(stored) : null);
  }, []);

  function logout() {
    window.localStorage.removeItem("civiciq_token");
    window.localStorage.removeItem("civiciq_user");
    setUser(null);
  }

  if (!user) {
    return (
      <Link className="rounded-md bg-civic-blue px-3 py-2 text-sm font-semibold text-white" href="/login">
        Login
      </Link>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
      <span className="rounded-md bg-slate-100 px-2 py-1 font-medium text-slate-800">{user.role}</span>
      {user.department ? <span>{user.department}</span> : null}
      {user.district_id ? <span>{user.district_id}</span> : null}
      <button className="rounded-md border border-slate-200 px-2 py-1 hover:bg-slate-50" onClick={logout} type="button">
        Logout
      </button>
    </div>
  );
}
