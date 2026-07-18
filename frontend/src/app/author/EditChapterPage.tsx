import * as React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useRequireRole } from "@/hooks/use-require-role";
import { ChapterForm } from "@/components/author/chapter-form";
import {
  listMyNovels,
  getChapterById,
  updateChapter,
  deleteChapter,
  publishChapter,
  unpublishChapter,
} from "@/lib/author-api";
import { extractErrorMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { BackButton } from "@/components/ui/back-button";
import type { Chapter, ChapterCreate, ChapterUpdate } from "@/types";

export default function EditChapterPage() {
  const { isReady } = useRequireRole(["AUTHOR", "ADMIN"]);
  const { novelId = "", chapterId = "" } = useParams<{ novelId: string; chapterId: string }>();
  const navigate = useNavigate();

  const [chapter, setChapter] = React.useState<Chapter | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [statusMessage, setStatusMessage] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const mine = await listMyNovels();
      const match = mine.find((n) => n.id === novelId);
      if (!match) {
        setError("Novel not found, or you don't own it.");
        return;
      }
      const chapterData = await getChapterById(match.slug, chapterId);
      setChapter(chapterData);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [novelId, chapterId]);

  React.useEffect(() => {
    if (isReady) load();
  }, [isReady, load]);

  async function handleSubmit(payload: ChapterCreate | ChapterUpdate) {
    setError(null);
    try {
      await updateChapter(chapterId, payload as ChapterUpdate);
      setStatusMessage("Saved.");
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  async function handleTogglePublish() {
    if (!chapter) return;
    setError(null);
    try {
      if (chapter.status === "PUBLISHED") {
        await unpublishChapter(chapterId);
      } else {
        await publishChapter(chapterId);
      }
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  async function handleDelete() {
    if (!chapter) return;
    if (!window.confirm(`Delete "${chapter.title}"? This cannot be undone.`)) return;
    await deleteChapter(chapterId);
    navigate(`/author/novels/${novelId}/edit`);
  }

  if (!isReady || isLoading) {
    return <p className="mx-auto max-w-2xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  if (!chapter) {
    return (
      <p className="mx-auto max-w-2xl px-6 py-10 font-body text-sm text-slate-light">
        {error ?? "Chapter not found."}
      </p>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <BackButton to={`/author/novels/${novelId}/edit`} label="Back to novel" className="mb-6" />
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-3xl font-medium text-parchment">Edit chapter</h1>
        <span className="rounded bg-ink-soft px-2 py-1 font-mono text-xs uppercase tracking-wide text-slate-light">
          {chapter.status}
        </span>
      </div>

      {statusMessage && <Alert variant="success" className="mb-4">{statusMessage}</Alert>}

      <ChapterForm
        initialValues={{
          chapter_number: chapter.chapter_number,
          title: chapter.title,
          content: chapter.content ?? "",
          is_premium: chapter.is_premium,
          price: chapter.price,
        }}
        onSubmit={handleSubmit}
        submitLabel="Save changes"
        error={error}
      />

      <section className="mt-8 flex gap-2 border-t border-ink-border pt-6">
        <Button variant="secondary" size="sm" onClick={handleTogglePublish}>
          {chapter.status === "PUBLISHED" ? "Unpublish" : "Publish"}
        </Button>
        <Button variant="destructive" size="sm" onClick={handleDelete}>
          Delete chapter
        </Button>
      </section>
    </main>
  );
}
