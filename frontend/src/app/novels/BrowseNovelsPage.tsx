import * as React from "react";
import { Search } from "lucide-react";
import { browseNovels } from "@/lib/novels-api";
import { NovelCard } from "@/components/novel/novel-card";
import { Input } from "@/components/ui/input";
import type { NovelListItem } from "@/types";

export default function BrowseNovelsPage() {
  const [novels, setNovels] = React.useState<NovelListItem[]>([]);
  const [search, setSearch] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);

    const timeout = setTimeout(async () => {
      try {
        const data = await browseNovels({ search: search || undefined, limit: 40 });
        if (!controller.signal.aborted) setNovels(data);
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    }, 300); // debounce while typing

    return () => {
      clearTimeout(timeout);
      controller.abort();
    };
  }, [search]);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 flex flex-col gap-1">
        <h1 className="font-display text-3xl font-medium text-parchment">Browse stories</h1>
        <p className="font-body text-sm text-slate-light">
          Discover serialized fiction from writers on TaleDrop-Novellaire.
        </p>
      </div>

      <div className="relative mb-8 max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate" />
        <Input
          placeholder="Search by title or description…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {isLoading ? (
        <p className="font-body text-sm text-slate-light">Loading…</p>
      ) : novels.length === 0 ? (
        <p className="font-body text-sm text-slate-light">
          No stories found{search ? ` for "${search}"` : ""}.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {novels.map((novel) => (
            <NovelCard key={novel.id} novel={novel} />
          ))}
        </div>
      )}
    </main>
  );
}
