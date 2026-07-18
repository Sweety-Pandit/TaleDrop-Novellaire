import * as React from "react";
import { listGenres, listTags } from "@/lib/author-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert } from "@/components/ui/alert";
import { cn } from "@/lib/utils";
import type { Genre, Tag, NovelCreate, NovelUpdate } from "@/types";

export interface NovelFormValues {
  title: string;
  description: string;
  language: string;
  is_premium: boolean;
  price: number;
  genre_ids: string[];
  tag_ids: string[];
}

interface NovelFormProps {
  initialValues?: Partial<NovelFormValues>;
  onSubmit: (payload: NovelCreate | NovelUpdate) => Promise<void>;
  submitLabel: string;
  error?: string | null;
}

export function NovelForm({ initialValues, onSubmit, submitLabel, error }: NovelFormProps) {
  const [title, setTitle] = React.useState(initialValues?.title ?? "");
  const [description, setDescription] = React.useState(initialValues?.description ?? "");
  const [language, setLanguage] = React.useState(initialValues?.language ?? "en");
  const [isPremium, setIsPremium] = React.useState(initialValues?.is_premium ?? false);
  const [price, setPrice] = React.useState(initialValues?.price ?? 0);
  const [genreIds, setGenreIds] = React.useState<string[]>(initialValues?.genre_ids ?? []);
  const [tagIds, setTagIds] = React.useState<string[]>(initialValues?.tag_ids ?? []);

  const [genres, setGenres] = React.useState<Genre[]>([]);
  const [tags, setTags] = React.useState<Tag[]>([]);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    (async () => {
      const [genresData, tagsData] = await Promise.all([listGenres(), listTags()]);
      setGenres(genresData);
      setTags(tagsData);
    })();
  }, []);

  function toggle(ids: string[], id: string): string[] {
    return ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id];
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({
        title,
        description,
        language,
        is_premium: isPremium,
        price: isPremium ? price : 0,
        genre_ids: genreIds,
        tag_ids: tagIds,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {error && <Alert variant="error">{error}</Alert>}

      <div>
        <Label htmlFor="title">Title</Label>
        <Input id="title" required value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          rows={5}
          maxLength={5000}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="language">Language</Label>
        <Input
          id="language"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="max-w-[8rem]"
        />
      </div>

      <div>
        <Label>Pricing</Label>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 font-body text-sm text-parchment">
            <input
              type="checkbox"
              checked={isPremium}
              onChange={(e) => setIsPremium(e.target.checked)}
              className="accent-ember"
            />
            Premium novel
          </label>
          {isPremium && (
            <Input
              type="number"
              min={0}
              step={0.01}
              value={price}
              onChange={(e) => setPrice(Number(e.target.value))}
              className="w-28"
              aria-label="Price"
            />
          )}
        </div>
      </div>

      {genres.length > 0 && (
        <div>
          <Label>Genres</Label>
          <div className="flex flex-wrap gap-2">
            {genres.map((genre) => (
              <button
                key={genre.id}
                type="button"
                onClick={() => setGenreIds((prev) => toggle(prev, genre.id))}
                className={cn(
                  "rounded-full border px-3 py-1 font-body text-xs transition-colors",
                  genreIds.includes(genre.id)
                    ? "border-ember bg-ember/10 text-parchment"
                    : "border-ink-border text-slate-light hover:text-parchment"
                )}
              >
                {genre.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {tags.length > 0 && (
        <div>
          <Label>Tags</Label>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => setTagIds((prev) => toggle(prev, tag.id))}
                className={cn(
                  "rounded-full border px-3 py-1 font-body text-xs transition-colors",
                  tagIds.includes(tag.id)
                    ? "border-gold bg-gold/10 text-parchment"
                    : "border-ink-border text-slate-light hover:text-parchment"
                )}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <Button type="submit" isLoading={isSubmitting} className="self-start">
        {submitLabel}
      </Button>
    </form>
  );
}
