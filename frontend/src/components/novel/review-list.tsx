import * as React from "react";
import { Star, Trash2 } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { listReviews, submitReview, deleteReview } from "@/lib/engagement-api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type { Review } from "@/types";

function StarInput({ value, onChange }: { value: number; onChange: (n: number) => void }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} type="button" onClick={() => onChange(n)} aria-label={`${n} stars`}>
          <Star
            className={cn("h-5 w-5", n <= value ? "fill-gold text-gold" : "text-slate")}
          />
        </button>
      ))}
    </div>
  );
}

export function ReviewList({ novelId }: { novelId: string }) {
  const user = useAuthStore((s) => s.user);
  const [reviews, setReviews] = React.useState<Review[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [rating, setRating] = React.useState(0);
  const [content, setContent] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const load = React.useCallback(() => {
    listReviews(novelId)
      .then(setReviews)
      .finally(() => setIsLoading(false));
  }, [novelId]);

  React.useEffect(() => {
    load();
  }, [load]);

  const myReview = user ? reviews.find((r) => r.user.id === user.id) : undefined;

  React.useEffect(() => {
    if (myReview) {
      setRating(myReview.rating);
      setContent(myReview.content ?? "");
    }
  }, [myReview]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (rating === 0) return;
    setIsSubmitting(true);
    try {
      await submitReview(novelId, { rating, content: content || undefined });
      load();
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(reviewId: string) {
    await deleteReview(reviewId);
    load();
  }

  return (
    <section>
      <h2 className="mb-4 font-display text-xl font-medium text-parchment">Reviews</h2>

      {user && (
        <form onSubmit={handleSubmit} className="mb-6 flex flex-col gap-3 rounded border border-ink-border p-4">
          <StarInput value={rating} onChange={setRating} />
          <Textarea
            placeholder="Share your thoughts (optional)"
            rows={3}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <Button type="submit" size="sm" isLoading={isSubmitting} disabled={rating === 0} className="self-start">
            {myReview ? "Update review" : "Post review"}
          </Button>
        </form>
      )}

      {isLoading ? (
        <p className="font-body text-sm text-slate-light">Loading…</p>
      ) : reviews.length === 0 ? (
        <p className="font-body text-sm text-slate-light">No reviews yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {reviews.map((review) => (
            <li key={review.id} className="border-b border-ink-border pb-4">
              <div className="mb-1 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-body text-sm font-medium text-parchment">
                    {review.user.display_name}
                  </span>
                  <span className="flex">
                    {[1, 2, 3, 4, 5].map((n) => (
                      <Star
                        key={n}
                        className={cn(
                          "h-3.5 w-3.5",
                          n <= review.rating ? "fill-gold text-gold" : "text-slate"
                        )}
                      />
                    ))}
                  </span>
                </div>
                {user?.id === review.user.id && (
                  <button onClick={() => handleDelete(review.id)} aria-label="Delete review">
                    <Trash2 className="h-3.5 w-3.5 text-slate-light hover:text-ember" />
                  </button>
                )}
              </div>
              {review.content && (
                <p className="font-body text-sm text-parchment-dim">{review.content}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
