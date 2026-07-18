import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { logoutUser } from "@/lib/auth-api";

export function Header() {
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();

  // Zustand's persist middleware rehydrates from localStorage just after
  // first paint, so we hold off rendering auth-dependent UI for one tick
  // to avoid a flash of the logged-out state.
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  async function handleLogout() {
    try {
      await logoutUser();
    } finally {
      clearAuth();
      navigate("/");
    }
  }

  return (
    <header className="border-b border-ink-border bg-ink">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="font-display text-xl font-medium text-parchment">
          TaleDrop<span className="text-ember">·</span>Novellaire
        </Link>

        <nav className="flex items-center gap-6 font-body text-sm">
          <Link to="/novels" className="text-slate-light hover:text-parchment">
            Browse
          </Link>
          <Link to="/search" className="text-slate-light hover:text-parchment">
            Search
          </Link>

          {!mounted ? null : user ? (
            <>
              <Link to="/library" className="text-slate-light hover:text-parchment">
                Library
              </Link>
              <Link to="/payments/history" className="text-slate-light hover:text-parchment">
                Purchases
              </Link>
              {(user.role === "AUTHOR" || user.role === "ADMIN") && (
                <Link to="/author/dashboard" className="text-slate-light hover:text-parchment">
                  Author Dashboard
                </Link>
              )}
              <Link to="/profile" className="text-slate-light hover:text-parchment">
                {user.display_name}
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-slate-light hover:text-parchment">
                Log in
              </Link>
              <Button size="sm" onClick={() => navigate("/register")}>
                Sign up
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
