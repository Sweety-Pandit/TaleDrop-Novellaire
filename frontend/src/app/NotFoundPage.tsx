import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  return (
    <main className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
      <p className="font-mono text-xs uppercase tracking-[0.3em] text-ember">404</p>
      <h1 className="font-display text-3xl font-medium text-parchment">Page not found</h1>
      <p className="max-w-sm font-body text-sm text-slate-light">
        The page you&rsquo;re looking for doesn&rsquo;t exist or may have been moved.
      </p>
      <Link to="/">
        <Button variant="secondary" size="sm">
          Back home
        </Button>
      </Link>
    </main>
  );
}
