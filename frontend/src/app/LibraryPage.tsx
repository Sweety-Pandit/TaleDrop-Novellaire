import * as React from "react";
import { Link } from "react-router-dom";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { getMyLibrary, removeFromLibrary } from "@/lib/novels-api";
import { getReadingHistory } from "@/lib/user-api";
import { getMediaUrl, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { LibraryItem, ReadingHistoryItem } from "@/types";

export default function LibraryPage() {
  const { isReady } = useRequireAuth();
  const [tab, setTab] = React.useState<"saved" | "history">("saved");
  const [library, setLibrary] = React.useState<LibraryItem[]>([]);
  const [history, setHistory] = React.useState<ReadingHistoryItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    if (!isReady) return;
    (async () => {
      setIsLoading(true);
      const [libraryData, historyData] = await Promise.all([getMyLibrary(), getReadingHistory()]);
      setLibrary(libraryData);
      setHistory(historyData);
      setIsLoading(false);
    })();
  }, [isReady]);

  async function handleRemove(novelId: string) {
    await removeFromLibrary(novelId);
    setLibrary((prev) => prev.filter((item) => item.novel_id !== novelId));
  }

  if (!isReady) {
    return <p className="mx-auto max-w-4xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="mb-6 font-display text-3xl font-medium text-parchment">Your library</h1>

      <div className="mb-8 flex gap-1 border-b border-ink-border">
        {(["saved", "history"] as const).map((t) => (
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
            {t === "saved" ? "Saved novels" : "Reading history"}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="font-body text-sm text-slate-light">Loading…</p>
      ) : tab === "saved" ? (
        library.length === 0 ? (
          <p className="font-body text-sm text-slate-light">
            You haven&rsquo;t saved any novels yet.{" "}
            <Link to="/novels" className="text-ember hover:underline">
              Browse stories
            </Link>
            .
          </p>
        ) : (
          <ul className="flex flex-col gap-3">
            {library.map((item) => {
              const coverUrl = getMediaUrl(item.novel_cover_image);
              return (
                <li
                  key={item.id}
                  className="flex items-center gap-4 rounded border border-ink-border p-3"
                >
                  <div className="relative h-16 w-11 shrink-0 overflow-hidden rounded bg-ink-soft">
                    {coverUrl && <img src={coverUrl} alt="" className="h-full w-full object-cover" />}
                  </div>
                  <Link
                    to={`/novels/${item.novel_slug}`}
                    className="flex-1 font-body text-sm text-parchment hover:text-ember"
                  >
                    {item.novel_title}
                  </Link>
                  <Button variant="ghost" size="sm" onClick={() => handleRemove(item.novel_id)}>
                    Remove
                  </Button>
                </li>
              );
            })}
          </ul>
        )
      ) : history.length === 0 ? (
        <p className="font-body text-sm text-slate-light">No reading history yet.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {history.map((item) => {
            const coverUrl = getMediaUrl(item.novel_cover_image);
            return (
              <li
                key={item.id}
                className="flex items-center gap-4 rounded border border-ink-border p-3"
              >
                <div className="relative h-16 w-11 shrink-0 overflow-hidden rounded bg-ink-soft">
                  {coverUrl && <img src={coverUrl} alt="" className="h-full w-full object-cover" />}
                </div>
                <Link
                  to={`/novels/${item.novel_slug}/chapters/${item.chapter_number}`}
                  className="flex-1 font-body text-sm text-parchment hover:text-ember"
                >
                  <p>{item.novel_title}</p>
                  <p className="font-body text-xs text-slate-light">
                    Ch. {item.chapter_number}: {item.chapter_title}
                  </p>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
