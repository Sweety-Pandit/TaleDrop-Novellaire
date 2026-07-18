import * as React from "react";
import { useNavigate } from "react-router-dom";
import { useRequireRole } from "@/hooks/use-require-role";
import { NovelForm } from "@/components/author/novel-form";
import { createNovel } from "@/lib/author-api";
import { extractErrorMessage } from "@/lib/api";
import { BackButton } from "@/components/ui/back-button";
import type { NovelCreate, NovelUpdate } from "@/types";

export default function NewNovelPage() {
  const { isReady } = useRequireRole(["AUTHOR", "ADMIN"]);
  const navigate = useNavigate();
  const [error, setError] = React.useState<string | null>(null);

  async function handleSubmit(payload: NovelCreate | NovelUpdate) {
    setError(null);
    try {
      const novel = await createNovel(payload as NovelCreate);
      navigate(`/author/novels/${novel.id}/edit`);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  if (!isReady) {
    return <p className="mx-auto max-w-xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  return (
    <main className="mx-auto max-w-xl px-6 py-10">
      <BackButton to="/author/dashboard" label="Back to your novels" className="mb-6" />
      <h1 className="mb-2 font-display text-3xl font-medium text-parchment">New novel</h1>
      <p className="mb-8 font-body text-sm text-slate-light">
        Starts as a draft. You can add a cover image and chapters after creating it.
      </p>
      <NovelForm onSubmit={handleSubmit} submitLabel="Create novel" error={error} />
    </main>
  );
}
