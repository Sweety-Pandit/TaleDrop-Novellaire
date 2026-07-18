import * as React from "react";
import { Link, useParams } from "react-router-dom";
import { BookmarkPlus, BookmarkCheck, Lock, Star } from "lucide-react";
import { getNovelBySlug, listNovelChapters, addToLibrary, removeFromLibrary, getMyLibrary } from "@/lib/novels-api";
import { Button } from "@/components/ui/button";
import { RibbonBadge } from "@/components/novel/ribbon-badge";
import { NovelStatusLabel } from "@/components/novel/novel-status-label";
import { BackButton } from "@/components/ui/back-button";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { getMediaUrl } from "@/lib/utils";
import { extractErrorMessage } from "@/lib/api";
import { AIPanel } from "@/components/novel/ai-panel";
import { ReviewList } from "@/components/novel/review-list";
import { CommentThread } from "@/components/novel/comment-thread";
import type { Novel, ChapterListItem } from "@/types";

export default function NovelDetailPage() {
  const { slug = "" } = useParams<{ slug: string }>();
  const { user, isReady } = useRequireAuth();

  const [novel, setNovel] = React.useState<Novel | null>(null);
  const [chapters, setChapters] = React.useState<ChapterListItem[]>([]);
  const [inLibrary, setInLibrary] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!isReady) return;
    let cancelled = false;
    (async () => {
      try {
        const [novelData, chaptersData] = await Promise.all([
          getNovelBySlug(slug),
          listNovelChapters(slug),
        ]);
        if (cancelled) return;
        setNovel(novelData);
        setChapters(chaptersData);

        const library = await getMyLibrary();
        if (!cancelled) {
          setInLibrary(library.some((item) => item.novel_id === novelData.id));
        }
      } catch (err) {
        if (!cancelled) setError(extractErrorMessage(err));
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [slug, isReady]);

  async function handleToggleLibrary() {
    if (!novel || !user) return;
    if (inLibrary) {
      await removeFromLibrary(novel.id);
      setInLibrary(false);
    } else {
      await addToLibrary(novel.id);
      setInLibrary(true);
    }
  }

  if (!isReady || isLoading) {
    return <p className="mx-auto max-w-4xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  if (error || !novel) {
    return (
      <p className="mx-auto max-w-4xl px-6 py-10 font-body text-sm text-slate-light">
        {error ?? "This story couldn't be found."}
      </p>
    );
  }

  const coverUrl = getMediaUrl(novel.cover_image);
  const bannerUrl = getMediaUrl(novel.banner_image);

  return (
    <main>
      {bannerUrl && (
        <div className="relative h-56 w-full overflow-hidden">
          <img src={bannerUrl} alt="" className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-ink to-transparent" />
        </div>
      )}

      <div className="mx-auto max-w-4xl px-6 py-10">
        <BackButton to="/novels" label="Back to novels" className="mb-6" />
        <div className="flex flex-col gap-6 sm:flex-row">
          <div className="relative aspect-[2/3] w-40 shrink-0 overflow-hidden rounded bg-ink-soft">
            {coverUrl ? (
              <img src={coverUrl} alt={novel.title} className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full w-full items-center justify-center px-2 text-center font-display text-sm text-slate-light">
                {novel.title}
              </div>
            )}
            {novel.is_premium && <RibbonBadge label="Premium" tone="ember" />}
            <NovelStatusLabel status={novel.status} className="absolute bottom-2 left-2" />
          </div>

          <div className="flex-1">
            <h1 className="font-display text-3xl font-medium text-parchment">{novel.title}</h1>
            <Link
              to={`/authors/${novel.author.username}`}
              className="font-body text-sm text-slate-light hover:text-ember"
            >
              by {novel.author.display_name}
            </Link>

            <div className="mt-2 flex flex-wrap items-center gap-3 font-mono text-xs text-slate-light">
              <span className="flex items-center gap-1">
                <Star className="h-3.5 w-3.5 fill-gold text-gold" />
                {novel.average_rating > 0 ? novel.average_rating.toFixed(1) : "New"}
              </span>
              <span>{novel.chapter_count} chapters</span>
              <span>{novel.views} views</span>
            </div>

            {(novel.genres.length > 0 || novel.tags.length > 0) && (
              <div className="mt-3 flex flex-wrap gap-2">
                {[...novel.genres, ...novel.tags].map((g) => (
                  <span
                    key={g.id}
                    className="rounded-full border border-ink-border px-2.5 py-0.5 font-body text-xs text-slate-light"
                  >
                    {g.name}
                  </span>
                ))}
              </div>
            )}

            {novel.description && (
              <p className="mt-4 font-body text-sm leading-relaxed text-parchment-dim">
                {novel.description}
              </p>
            )}

            {user && (
              <Button variant="secondary" size="sm" className="mt-4" onClick={handleToggleLibrary}>
                {inLibrary ? (
                  <>
                    <BookmarkCheck className="h-4 w-4" /> In your library
                  </>
                ) : (
                  <>
                    <BookmarkPlus className="h-4 w-4" /> Add to library
                  </>
                )}
              </Button>
            )}
          </div>
        </div>

        <div className="mt-10">
          <h2 className="mb-4 font-display text-xl font-medium text-parchment">Chapters</h2>
          {chapters.length === 0 ? (
            <p className="font-body text-sm text-slate-light">No chapters published yet.</p>
          ) : (
            <ol className="divide-y divide-ink-border rounded border border-ink-border">
              {chapters.map((chapter) => (
                <li key={chapter.id}>
                  <Link
                    to={`/novels/${novel.slug}/chapters/${chapter.chapter_number}`}
                    className="flex items-center justify-between px-4 py-3 font-body text-sm text-parchment hover:bg-ink-soft"
                  >
                    <span>
                      <span className="text-slate-light">Ch. {chapter.chapter_number}</span>{" "}
                      {chapter.title}
                    </span>
                    {chapter.is_premium && <Lock className="h-3.5 w-3.5 text-ember" />}
                  </Link>
                </li>
              ))}
            </ol>
          )}
        </div>

        <div className="mt-10">
          <AIPanel novelId={novel.id} />
        </div>

        <div className="mt-10 grid gap-10 sm:grid-cols-2">
          <ReviewList novelId={novel.id} />
          <CommentThread novelId={novel.id} />
        </div>
      </div>
    </main>
  );
}
