import * as React from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Lock, ChevronLeft, ChevronRight } from "lucide-react";
import { getNovelBySlug, listNovelChapters, getChapter, recordReadingProgress } from "@/lib/novels-api";
import { initiateChapterPurchase, confirmPayment } from "@/lib/payments-api";
import { openRazorpayCheckout } from "@/lib/razorpay";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { ChapterContent } from "@/components/reader/chapter-content";
import { ReadingProgressRail } from "@/components/reader/reading-progress-rail";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { extractErrorMessage } from "@/lib/api";
import type { Chapter, ChapterListItem, Novel } from "@/types";

export default function ChapterReaderPage() {
  const { slug = "", number = "" } = useParams<{ slug: string; number: string }>();
  const navigate = useNavigate();
  const { user, isReady } = useRequireAuth();
  const chapterNumber = Number(number);

  const [novel, setNovel] = React.useState<Novel | null>(null);
  const [chapters, setChapters] = React.useState<ChapterListItem[]>([]);
  const [chapter, setChapter] = React.useState<Chapter | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [isPurchasing, setIsPurchasing] = React.useState(false);

  const load = React.useCallback(async () => {
    if (!isReady) return;
    setIsLoading(true);
    setError(null);
    try {
      const [novelData, chapterData] = await Promise.all([
        getNovelBySlug(slug),
        getChapter(slug, chapterNumber),
      ]);
      setNovel(novelData);
      setChapter(chapterData);
      const chaptersData = await listNovelChapters(slug);
      setChapters(chaptersData);

      if (!chapterData.locked) {
        await recordReadingProgress(novelData.id, chapterData.id);
      }
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [slug, chapterNumber, isReady]);

  React.useEffect(() => {
    load();
  }, [load]);

  async function handlePurchase() {
    if (!chapter || !user) return;
    setIsPurchasing(true);
    setError(null);
    try {
      const order = await initiateChapterPurchase(chapter.id);
      const result = await openRazorpayCheckout(order, {
        title: chapter.title,
        userEmail: user.email,
        userName: user.display_name,
      });
      await confirmPayment(result);
      await load(); // re-fetch: chapter should now come back unlocked
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsPurchasing(false);
    }
  }

  if (!isReady || isLoading) {
    return <p className="mx-auto max-w-2xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  if (error && !chapter) {
    return <p className="mx-auto max-w-2xl px-6 py-10 font-body text-sm text-slate-light">{error}</p>;
  }

  if (!chapter || !novel) return null;

  const currentIndex = chapters.findIndex((c) => c.chapter_number === chapterNumber);
  const prevChapter = currentIndex > 0 ? chapters[currentIndex - 1] : null;
  const nextChapter =
    currentIndex >= 0 && currentIndex < chapters.length - 1 ? chapters[currentIndex + 1] : null;

  return (
    <main className="pb-24">
      <ReadingProgressRail />

      <div className="mx-auto max-w-2xl px-6 py-10">
        <Link to={`/novels/${slug}`} className="font-body text-xs text-slate-light hover:text-ember">
          ← {novel.title}
        </Link>

        <h1 className="mb-8 mt-2 font-display text-2xl font-medium text-parchment">
          Chapter {chapter.chapter_number}: {chapter.title}
        </h1>

        {chapter.locked ? (
          <div className="flex flex-col items-center gap-4 rounded border border-ink-border bg-ink-soft px-6 py-12 text-center">
            <Lock className="h-8 w-8 text-ember" />
            <p className="font-body text-sm text-parchment">This is a premium chapter.</p>
            {error && <Alert variant="error">{error}</Alert>}
            {user ? (
              <Button onClick={handlePurchase} isLoading={isPurchasing}>
                Unlock for ₹{chapter.price.toFixed(2)}
              </Button>
            ) : (
              <Button onClick={() => navigate("/login")}>Log in to purchase</Button>
            )}
          </div>
        ) : (
          <ChapterContent content={chapter.content ?? ""} />
        )}

        <div className="mt-12 flex items-center justify-between border-t border-ink-border pt-6">
          {prevChapter ? (
            <Link
              to={`/novels/${slug}/chapters/${prevChapter.chapter_number}`}
              className="flex items-center gap-1 font-body text-sm text-parchment hover:text-ember"
            >
              <ChevronLeft className="h-4 w-4" /> Chapter {prevChapter.chapter_number}
            </Link>
          ) : (
            <span />
          )}
          {nextChapter ? (
            <Link
              to={`/novels/${slug}/chapters/${nextChapter.chapter_number}`}
              className="flex items-center gap-1 font-body text-sm text-parchment hover:text-ember"
            >
              Chapter {nextChapter.chapter_number} <ChevronRight className="h-4 w-4" />
            </Link>
          ) : (
            <span />
          )}
        </div>
      </div>
    </main>
  );
}
