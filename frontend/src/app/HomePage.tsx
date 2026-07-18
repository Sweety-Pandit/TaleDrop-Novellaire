import * as React from "react";
import { Link } from "react-router-dom";
import { browseNovels } from "@/lib/novels-api";
import { NovelCard } from "@/components/novel/novel-card";
import { Button } from "@/components/ui/button";
import type { NovelListItem } from "@/types";

export default function HomePage() {
  const [novels, setNovels] = React.useState<NovelListItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    browseNovels({ limit: 12 })
      .then(setNovels)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main>
      <section className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-ember">Chapter One</p>
        <h1 className="max-w-2xl font-display text-5xl font-medium text-parchment sm:text-6xl">
          Stories worth staying up for.
        </h1>
        <p className="max-w-md font-body text-slate-light">
          Serialized fiction, published chapter by chapter. Read for free, unlock premium
          chapters, and follow the stories you love as they update.
        </p>
        <div className="mt-4 flex gap-3">
          <Link to="/novels">
            <Button size="lg">Start reading</Button>
          </Link>
          <Link to="/register">
            <Button variant="secondary" size="lg">
              Become an author
            </Button>
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-16">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-display text-2xl font-medium text-parchment">Recently updated</h2>
          <Link to="/novels" className="font-body text-sm text-ember hover:underline">
            Browse all →
          </Link>
        </div>

        {isLoading ? (
          <p className="font-body text-sm text-slate-light">Loading…</p>
        ) : novels.length === 0 ? (
          <p className="font-body text-sm text-slate-light">
            No stories published yet — be the first.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {novels.map((novel) => (
              <NovelCard key={novel.id} novel={novel} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
