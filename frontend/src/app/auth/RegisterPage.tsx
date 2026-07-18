import * as React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { registerUser } from "@/lib/auth-api";
import { extractErrorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function RegisterPage() {
  const [username, setUsername] = React.useState("");
  const [displayName, setDisplayName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [role, setRole] = React.useState<"READER" | "AUTHOR">("READER");
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await registerUser({ username, display_name: displayName, email, password, role });
      setSuccess(true);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  if (success) {
    return (
      <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-sm flex-col justify-center px-6 text-center">
        <h1 className="mb-2 font-display text-3xl font-medium text-parchment">Check your email</h1>
        <p className="font-body text-sm text-slate-light">
          We sent a verification link to <span className="text-parchment">{email}</span>. Verify
          your address, then{" "}
          <Link to="/login" className="text-ember hover:underline">
            log in
          </Link>
          .
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-sm flex-col justify-center px-6">
      <h1 className="mb-1 font-display text-3xl font-medium text-parchment">Create an account</h1>
      <p className="mb-6 font-body text-sm text-slate-light">
        Start reading, or start publishing your own story.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {error && <Alert variant="error">{error}</Alert>}

        <div>
          <Label htmlFor="displayName">Display name</Label>
          <Input
            id="displayName"
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="username">Username</Label>
          <Input
            id="username"
            required
            pattern="[a-zA-Z0-9_]{3,50}"
            title="Letters, numbers, and underscores only"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

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
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <div>
          <Label>I&rsquo;m joining as a</Label>
          <div className="flex gap-2">
            {(["READER", "AUTHOR"] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setRole(option)}
                className={cn(
                  "flex-1 rounded border px-3 py-2 font-body text-sm capitalize transition-colors",
                  role === option
                    ? "border-ember bg-ember/10 text-parchment"
                    : "border-ink-border text-slate-light hover:text-parchment"
                )}
              >
                {option === "READER" ? "Reader" : "Author"}
              </button>
            ))}
          </div>
        </div>

        <Button type="submit" isLoading={isLoading} className="mt-2">
          Create account
        </Button>
      </form>

      <p className="mt-6 text-center font-body text-sm text-slate-light">
        Already have an account?{" "}
        <Link to="/login" className="text-ember hover:underline">
          Log in
        </Link>
      </p>
    </main>
  );
}
