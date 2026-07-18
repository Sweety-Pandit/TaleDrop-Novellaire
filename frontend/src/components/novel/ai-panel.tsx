import * as React from "react";
import { Sparkles, Send, Lock } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { getNovelSummary, askNovelQuestion } from "@/lib/engagement-api";
import { extractErrorMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import type { AISource } from "@/types";

export function AIPanel({ novelId }: { novelId: string }) {
  const user = useAuthStore((s) => s.user);

  const [summary, setSummary] = React.useState<string | null>(null);
  const [isSummaryLoading, setIsSummaryLoading] = React.useState(false);
  const [summaryError, setSummaryError] = React.useState<string | null>(null);

  const [question, setQuestion] = React.useState("");
  const [answer, setAnswer] = React.useState<string | null>(null);
  const [sources, setSources] = React.useState<AISource[]>([]);
  const [isAsking, setIsAsking] = React.useState(false);
  const [askError, setAskError] = React.useState<string | null>(null);

  async function handleGetSummary() {
    setIsSummaryLoading(true);
    setSummaryError(null);
    try {
      const result = await getNovelSummary(novelId);
      setSummary(result.summary);
    } catch (err) {
      setSummaryError(extractErrorMessage(err));
    } finally {
      setIsSummaryLoading(false);
    }
  }

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setIsAsking(true);
    setAskError(null);
    try {
      const result = await askNovelQuestion(novelId, question);
      setAnswer(result.answer);
      setSources(result.sources);
    } catch (err) {
      setAskError(extractErrorMessage(err));
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <section className="rounded border border-ink-border p-4">
      <h2 className="mb-3 flex items-center gap-2 font-display text-lg font-medium text-parchment">
        <Sparkles className="h-4 w-4 text-ember" /> AI companion
      </h2>

      <div className="mb-6">
        {summary ? (
          <p className="font-body text-sm italic text-parchment-dim">{summary}</p>
        ) : (
          <Button variant="secondary" size="sm" onClick={handleGetSummary} isLoading={isSummaryLoading}>
            Generate summary
          </Button>
        )}
        {summaryError && <Alert variant="error" className="mt-2">{summaryError}</Alert>}
      </div>

      <div className="border-t border-ink-border pt-4">
        <p className="mb-2 font-body text-xs text-slate-light">Ask about this story so far</p>
        {user ? (
          <form onSubmit={handleAsk} className="flex gap-2">
            <Input
              placeholder="e.g. Who is the main character?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <Button type="submit" size="sm" isLoading={isAsking}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        ) : (
          <p className="flex items-center gap-1 font-body text-xs text-slate-light">
            <Lock className="h-3 w-3" /> Log in to ask questions about this story.
          </p>
        )}

        {askError && <Alert variant="error" className="mt-3">{askError}</Alert>}

        {answer && (
          <div className="mt-3 rounded bg-ink-soft p-3">
            <p className="font-body text-sm text-parchment">{answer}</p>
            {sources.length > 0 && (
              <p className="mt-2 font-mono text-[10px] uppercase tracking-wide text-slate-light">
                Sources: {sources.map((s) => `Ch. ${s.chapter_number}`).join(", ")}
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
