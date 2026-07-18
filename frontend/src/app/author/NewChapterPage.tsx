import * as React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useRequireRole } from "@/hooks/use-require-role";
import { ChapterForm } from "@/components/author/chapter-form";
import { createChapter } from "@/lib/author-api";
import { extractErrorMessage } from "@/lib/api";
import { BackButton } from "@/components/ui/back-button";
import type { ChapterCreate, ChapterUpdate } from "@/types";

export default function NewChapterPage() {
  const { isReady } = useRequireRole(["AUTHOR", "ADMIN"]);
  const { novelId = "" } = useParams<{ novelId: string }>();
  const navigate = useNavigate();
  const [error, setError] = React.useState<string | null>(null);

  async function handleSubmit(payload: ChapterCreate | ChapterUpdate) {
    setError(null);
    try {
      await createChapter(novelId, payload as ChapterCreate);
      navigate(`/author/novels/${novelId}/edit`);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  if (!isReady) {
    return <p className="mx-auto max-w-2xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <BackButton to={`/author/novels/${novelId}/edit`} label="Back to novel" className="mb-6" />
      <h1 className="mb-2 font-display text-3xl font-medium text-parchment">New chapter</h1>
      <p className="mb-8 font-body text-sm text-slate-light">
        Starts as a draft. Publish it from the chapter list once you&rsquo;re ready.
      </p>
      <ChapterForm onSubmit={handleSubmit} submitLabel="Create chapter" error={error} />
    </main>
  );
}
