import * as React from "react";
import { Link } from "react-router-dom";
import { Search as SearchIcon } from "lucide-react";
import { searchNovels, searchAuthors } from "@/lib/search-api";
import { NovelCard } from "@/components/novel/novel-card";
import { Input } from "@/components/ui/input";
import { getMediaUrl, cn } from "@/lib/utils";
import type { NovelListItem, UserPublic } from "@/types";

export default function SearchPage() {
  const [query, setQuery] = React.useState("");
  const [tab, setTab] = React.useState<"novels" | "authors">("novels");
  const [novels, setNovels] = React.useState<NovelListItem[]>([]);
  const [authors, setAuthors] = React.useState<UserPublic[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (!query.trim()) {
      setNovels([]);
      setAuthors([]);
      return;
    }
    const timeout = setTimeout(async () => {
      setIsLoading(true);
      try {
        if (tab === "novels") {
          setNovels(await searchNovels(query));
        } else {
          setAuthors(await searchAuthors(query));
        }
      } finally {
        setIsLoading(false);
      }
    }, 300);
    return () => clearTimeout(timeout);
  }, [query, tab]);

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="mb-6 font-display text-3xl font-medium text-parchment">Search</h1>

      <div className="relative mb-4 max-w-md">
        <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate" />
        <Input
          placeholder="Search novels or authors…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="mb-8 flex gap-1 border-b border-ink-border">
        {(["novels", "authors"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "px-4 py-2 font-body text-sm capitalize transition-colors",
              tab === t
                ? "border-b-2 border-ember text-parchment"
                : "text-slate-light hover:text-parchment"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {!query.trim() ? (
        <p className="font-body text-sm text-slate-light">Start typing to search.</p>
      ) : isLoading ? (
        <p className="font-body text-sm text-slate-light">Searching…</p>
      ) : tab === "novels" ? (
        novels.length === 0 ? (
          <p className="font-body text-sm text-slate-light">No novels found.</p>
        ) : (
          <div className="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 md:grid-cols-4">
            {novels.map((novel) => (
              <NovelCard key={novel.id} novel={novel} />
            ))}
          </div>
        )
      ) : authors.length === 0 ? (
        <p className="font-body text-sm text-slate-light">No authors found.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {authors.map((author) => {
            const avatarUrl = getMediaUrl(author.avatar);
            return (
              <li key={author.id}>
                <Link
                  to={`/authors/${author.username}`}
                  className="flex items-center gap-3 rounded border border-ink-border p-3 hover:bg-ink-soft"
                >
                  <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-full bg-ink-soft">
                    {avatarUrl && <img src={avatarUrl} alt="" className="h-full w-full object-cover" />}
                  </div>
                  <div>
                    <p className="font-body text-sm text-parchment">{author.display_name}</p>
                    <p className="font-body text-xs text-slate-light">@{author.username}</p>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
