import * as React from "react";
import { Link } from "react-router-dom";
import { Plus, BookOpen } from "lucide-react";
import { useRequireRole } from "@/hooks/use-require-role";
import { listMyNovels, deleteNovel } from "@/lib/author-api";
import { getMediaUrl, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { NovelListItem, NovelStatus } from "@/types";

const STATUS_STYLES: Record<NovelStatus, string> = {
  DRAFT: "bg-ink-soft text-slate-light",
  PUBLISHED: "bg-moss/20 text-moss-light",
  COMPLETED: "bg-gold/20 text-gold",
};

export default function AuthorDashboardPage() {
  const { isReady } = useRequireRole(["AUTHOR", "ADMIN"]);
  const [novels, setNovels] = React.useState<NovelListItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    if (!isReady) return;
    listMyNovels()
      .then(setNovels)
      .finally(() => setIsLoading(false));
  }, [isReady]);

  async function handleDelete(novelId: string, title: string) {
    if (!window.confirm(`Delete "${title}"? This cannot be undone.`)) return;
    await deleteNovel(novelId);
    setNovels((prev) => prev.filter((n) => n.id !== novelId));
  }

  if (!isReady) {
    return <p className="mx-auto max-w-4xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="font-display text-3xl font-medium text-parchment">Your novels</h1>
        <Link to="/author/novels/new">
          <Button size="sm">
            <Plus className="h-4 w-4" /> New novel
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <p className="font-body text-sm text-slate-light">Loading…</p>
      ) : novels.length === 0 ? (
        <p className="font-body text-sm text-slate-light">
          You haven&rsquo;t created any novels yet.
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {novels.map((novel) => {
            const coverUrl = getMediaUrl(novel.cover_image);
            return (
              <li
                key={novel.id}
                className="flex items-center gap-4 rounded border border-ink-border p-3"
              >
                <div className="relative h-20 w-14 shrink-0 overflow-hidden rounded bg-ink-soft">
                  {coverUrl && <img src={coverUrl} alt="" className="h-full w-full object-cover" />}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-body text-sm font-medium text-parchment">
                      {novel.title}
                    </p>
                    <span
                      className={cn(
                        "shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide",
                        STATUS_STYLES[novel.status]
                      )}
                    >
                      {novel.status}
                    </span>
                  </div>
                  <p className="font-body text-xs text-slate-light">
                    {novel.views} views · {novel.average_rating > 0 ? novel.average_rating.toFixed(1) : "unrated"}
                  </p>
                </div>

                <Link to={`/author/novels/${novel.id}/chapters/new`}>
                  <Button variant="ghost" size="sm">
                    <BookOpen className="h-4 w-4" /> Add chapter
                  </Button>
                </Link>
                <Link to={`/author/novels/${novel.id}/edit`}>
                  <Button variant="secondary" size="sm">
                    Edit
                  </Button>
                </Link>
                <Button variant="destructive" size="sm" onClick={() => handleDelete(novel.id, novel.title)}>
                  Delete
                </Button>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
