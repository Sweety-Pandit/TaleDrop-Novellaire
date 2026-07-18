import * as React from "react";
import { Trash2 } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { listComments, postComment, deleteComment } from "@/lib/engagement-api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { Comment } from "@/types";

export function CommentThread({ novelId }: { novelId: string }) {
  const user = useAuthStore((s) => s.user);
  const [comments, setComments] = React.useState<Comment[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [content, setContent] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const load = React.useCallback(() => {
    listComments(novelId)
      .then(setComments)
      .finally(() => setIsLoading(false));
  }, [novelId]);

  React.useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    setIsSubmitting(true);
    try {
      await postComment(novelId, content);
      setContent("");
      load();
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(commentId: string) {
    await deleteComment(commentId);
    load();
  }

  return (
    <section>
      <h2 className="mb-4 font-display text-xl font-medium text-parchment">Comments</h2>

      {user && (
        <form onSubmit={handleSubmit} className="mb-6 flex flex-col gap-3">
          <Textarea
            placeholder="Join the discussion…"
            rows={3}
            maxLength={3000}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <Button type="submit" size="sm" isLoading={isSubmitting} className="self-start">
            Post comment
          </Button>
        </form>
      )}

      {isLoading ? (
        <p className="font-body text-sm text-slate-light">Loading…</p>
      ) : comments.length === 0 ? (
        <p className="font-body text-sm text-slate-light">No comments yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {comments.map((comment) => (
            <li key={comment.id} className="border-b border-ink-border pb-4">
              <div className="mb-1 flex items-center justify-between">
                <span className="font-body text-sm font-medium text-parchment">
                  {comment.user.display_name}
                </span>
                {user?.id === comment.user.id && (
                  <button onClick={() => handleDelete(comment.id)} aria-label="Delete comment">
                    <Trash2 className="h-3.5 w-3.5 text-slate-light hover:text-ember" />
                  </button>
                )}
              </div>
              <p className="font-body text-sm text-parchment-dim">{comment.content}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
