import * as React from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

/**
 * Guards a page behind authentication. Waits one tick for the
 * persisted Zustand store to settle before deciding to redirect, so a
 * logged-in user isn't bounced to /login for a frame on page load.
 */
export function useRequireAuth() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => setHydrated(true), []);

  React.useEffect(() => {
    if (hydrated && !user) {
      navigate("/login", { replace: true });
    }
  }, [hydrated, user, navigate]);

  return { user, isReady: hydrated && !!user };
}
