import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { loginUser, fetchCurrentUser } from "@/lib/auth-api";
import { useAuthStore } from "@/store/authStore";
import { extractErrorMessage } from "@/lib/api";

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const tokens = await loginUser(email, password);
      // Stash tokens first so the authenticated /users/me request below can use them.
      useAuthStore.getState().setTokens(tokens);
      const user = await fetchCurrentUser();
      setAuth(tokens, user);
      navigate("/");
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-sm flex-col justify-center px-6">
      <h1 className="mb-1 font-display text-3xl font-medium text-parchment">Welcome back</h1>
      <p className="mb-6 font-body text-sm text-slate-light">
        Log in to keep reading where you left off.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {error && <Alert variant="error">{error}</Alert>}

        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <Button type="submit" isLoading={isLoading} className="mt-2">
          Log in
        </Button>
      </form>

      <p className="mt-6 text-center font-body text-sm text-slate-light">
        New here?{" "}
        <Link to="/register" className="text-ember hover:underline">
          Create an account
        </Link>
      </p>
    </main>
  );
}
