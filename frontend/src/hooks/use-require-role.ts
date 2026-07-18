import * as React from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import type { UserRole } from "@/types";

/**
 * Guards a page behind authentication AND a role check. Redirects
 * home (rather than to /login) if the user is logged in but lacks
 * permission.
 */
export function useRequireRole(allowedRoles: UserRole[]) {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => setHydrated(true), []);

  React.useEffect(() => {
    if (!hydrated) return;
    if (!user) {
      navigate("/login", { replace: true });
    } else if (!allowedRoles.includes(user.role)) {
      navigate("/", { replace: true });
    }
    // allowedRoles is expected to be a stable literal array at each call site.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated, user, navigate]);

  const isReady = hydrated && !!user && allowedRoles.includes(user.role);
  return { user, isReady };
}
