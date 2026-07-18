import * as React from "react";
import { Link } from "react-router-dom";
import { useParams, useNavigate } from "react-router-dom";
import { Plus, Lock } from "lucide-react";
import { useRequireRole } from "@/hooks/use-require-role";
import { NovelForm } from "@/components/author/novel-form";
import {
  listMyNovels,
  updateNovel,
  deleteNovel,
  publishNovel,
  unpublishNovel,
  completeNovel,
  uploadNovelCover,
  uploadNovelBanner,
} from "@/lib/author-api";
import { getNovelBySlug, listNovelChapters } from "@/lib/novels-api";
import { extractErrorMessage } from "@/lib/api";
import { getMediaUrl } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { BackButton } from "@/components/ui/back-button";
import type { Novel, NovelCreate, NovelUpdate, ChapterListItem } from "@/types";

export default function EditNovelPage() {
  const { isReady } = useRequireRole(["AUTHOR", "ADMIN"]);
  const { novelId = "" } = useParams<{ novelId: string }>();
  const navigate = useNavigate();

  const [novel, setNovel] = React.useState<Novel | null>(null);
  const [chapters, setChapters] = React.useState<ChapterListItem[]>([]);
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
      const [novelData, chaptersData] = await Promise.all([
        getNovelBySlug(match.slug),
        listNovelChapters(match.slug),
      ]);
      setNovel(novelData);
      setChapters(chaptersData);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [novelId]);

  React.useEffect(() => {
    if (isReady) load();
  }, [isReady, load]);

  async function handleSubmit(payload: NovelCreate | NovelUpdate) {
    setError(null);
    try {
      const updated = await updateNovel(novelId, payload as NovelUpdate);
      setNovel(updated);
      setStatusMessage("Saved.");
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  async function handleStatusAction(action: "publish" | "unpublish" | "complete") {
    setError(null);
    try {
      const fn = { publish: publishNovel, unpublish: unpublishNovel, complete: completeNovel }[action];
      const updated = await fn(novelId);
      setNovel(updated);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  async function handleDelete() {
    if (!novel) return;
    if (!window.confirm(`Delete "${novel.title}"? This cannot be undone.`)) return;
    await deleteNovel(novelId);
    navigate("/author/dashboard");
  }

  async function handleCoverChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setNovel(await uploadNovelCover(novelId, file));
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      e.target.value = "";
    }
  }

  async function handleBannerChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setNovel(await uploadNovelBanner(novelId, file));
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      e.target.value = "";
    }
  }

  if (!isReady || isLoading) {
    return <p className="mx-auto max-w-xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  if (!novel) {
    return (
      <p className="mx-auto max-w-xl px-6 py-10 font-body text-sm text-slate-light">
        {error ?? "Novel not found."}
      </p>
    );
  }

  const coverUrl = getMediaUrl(novel.cover_image);
  const bannerUrl = getMediaUrl(novel.banner_image);

  return (
    <main className="mx-auto max-w-xl px-6 py-10">
      <BackButton to="/author/dashboard" label="Back to your novels" className="mb-6" />
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-3xl font-medium text-parchment">Edit novel</h1>
        <span className="rounded bg-ink-soft px-2 py-1 font-mono text-xs uppercase tracking-wide text-slate-light">
          {novel.status}
        </span>
      </div>

      {statusMessage && <Alert variant="success" className="mb-4">{statusMessage}</Alert>}

      <section className="mb-8 flex gap-4">
        <div>
          <p className="mb-1 font-body text-xs text-slate-light">Cover</p>
          <div className="relative mb-2 h-32 w-24 overflow-hidden rounded bg-ink-soft">
            {coverUrl && <img src={coverUrl} alt="" className="h-full w-full object-cover" />}
          </div>
          <input type="file" accept="image/*" onChange={handleCoverChange} className="text-xs" />
        </div>
        <div className="flex-1">
          <p className="mb-1 font-body text-xs text-slate-light">Banner</p>
          <div className="relative mb-2 h-32 w-full overflow-hidden rounded bg-ink-soft">
            {bannerUrl && <img src={bannerUrl} alt="" className="h-full w-full object-cover" />}
          </div>
          <input type="file" accept="image/*" onChange={handleBannerChange} className="text-xs" />
        </div>
      </section>

      <NovelForm
        initialValues={{
          title: novel.title,
          description: novel.description ?? "",
          language: novel.language,
          is_premium: novel.is_premium,
          price: novel.price,
          genre_ids: novel.genres.map((g) => g.id),
          tag_ids: novel.tags.map((t) => t.id),
        }}
        onSubmit={handleSubmit}
        submitLabel="Save changes"
        error={error}
      />

      <section className="mt-8 flex flex-wrap gap-2 border-t border-ink-border pt-6">
        {novel.status === "DRAFT" && (
          <Button variant="secondary" size="sm" onClick={() => handleStatusAction("publish")}>
            Publish
          </Button>
        )}
        {novel.status === "PUBLISHED" && (
          <>
            <Button variant="secondary" size="sm" onClick={() => handleStatusAction("unpublish")}>
              Unpublish
            </Button>
            <Button variant="secondary" size="sm" onClick={() => handleStatusAction("complete")}>
              Mark complete
            </Button>
          </>
        )}
        <Button variant="destructive" size="sm" onClick={handleDelete}>
          Delete novel
        </Button>
      </section>

      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-medium text-parchment">Chapters</h2>
          <Link to={`/author/novels/${novelId}/chapters/new`}>
            <Button size="sm">
              <Plus className="h-4 w-4" /> Add chapter
            </Button>
          </Link>
        </div>

        {chapters.length === 0 ? (
          <p className="font-body text-sm text-slate-light">No chapters yet.</p>
        ) : (
          <ol className="divide-y divide-ink-border rounded border border-ink-border">
            {chapters.map((chapter) => (
              <li key={chapter.id}>
                <Link
                  to={`/author/novels/${novelId}/chapters/${chapter.id}/edit`}
                  className="flex items-center justify-between px-4 py-3 font-body text-sm text-parchment hover:bg-ink-soft"
                >
                  <span>
                    <span className="text-slate-light">Ch. {chapter.chapter_number}</span>{" "}
                    {chapter.title}
                  </span>
                  <span className="flex items-center gap-2">
                    {chapter.is_premium && <Lock className="h-3.5 w-3.5 text-ember" />}
                    <span className="font-mono text-[10px] uppercase text-slate-light">
                      {chapter.status}
                    </span>
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        )}
      </section>
    </main>
  );
}
