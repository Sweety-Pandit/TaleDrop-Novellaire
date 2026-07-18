import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert } from "@/components/ui/alert";
import type { ChapterCreate, ChapterUpdate } from "@/types";

export interface ChapterFormValues {
  chapter_number?: number;
  title: string;
  content: string;
  is_premium: boolean;
  price: number;
}

interface ChapterFormProps {
  initialValues?: Partial<ChapterFormValues>;
  onSubmit: (payload: ChapterCreate | ChapterUpdate) => Promise<void>;
  submitLabel: string;
  error?: string | null;
}

export function ChapterForm({ initialValues, onSubmit, submitLabel, error }: ChapterFormProps) {
  const [chapterNumber, setChapterNumber] = React.useState<string>(
    initialValues?.chapter_number != null ? String(initialValues.chapter_number) : ""
  );
  const [title, setTitle] = React.useState(initialValues?.title ?? "");
  const [content, setContent] = React.useState(initialValues?.content ?? "");
  const [isPremium, setIsPremium] = React.useState(initialValues?.is_premium ?? false);
  const [price, setPrice] = React.useState(initialValues?.price ?? 0);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({
        chapter_number: chapterNumber ? Number(chapterNumber) : undefined,
        title,
        content,
        is_premium: isPremium,
        price: isPremium ? price : 0,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      {error && <Alert variant="error">{error}</Alert>}

      <div className="flex gap-4">
        <div className="flex-1">
          <Label htmlFor="title">Chapter title</Label>
          <Input id="title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="w-28">
          <Label htmlFor="chapterNumber">Number</Label>
          <Input
            id="chapterNumber"
            type="number"
            min={1}
            placeholder="Auto"
            value={chapterNumber}
            onChange={(e) => setChapterNumber(e.target.value)}
          />
        </div>
      </div>

      <div>
        <Label htmlFor="content">Content (Markdown)</Label>
        <Textarea
          id="content"
          required
          rows={18}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="font-mono text-sm leading-relaxed"
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
            Premium chapter
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

      <Button type="submit" isLoading={isSubmitting} className="self-start">
        {submitLabel}
      </Button>
    </form>
  );
}
