import * as React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PartyPopper, Info } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ChapterUnlockedPage() {
  const { slug = "", number = "" } = useParams<{ slug: string; number: string }>();
  const navigate = useNavigate();
  const [showDisclaimer, setShowDisclaimer] = React.useState(true);

  return (
    <main className="mx-auto flex max-w-md flex-col items-center gap-4 px-6 py-24 text-center">
      <PartyPopper className="h-10 w-10 text-ember" />
      <h1 className="font-display text-2xl font-medium text-parchment">Chapter unlocked!</h1>
      <p className="font-body text-sm text-slate-light">
        You now have access to this chapter. Head back to start reading.
      </p>
      <Button onClick={() => navigate(`/novels/${slug}/chapters/${number}`)}>Back to chapter</Button>

      {showDisclaimer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/90 px-4">
          <div className="w-full max-w-sm rounded border border-ink-border bg-ink-soft p-5 text-left">
            <div className="mb-3 flex items-center gap-2">
              <Info className="h-5 w-5 shrink-0 text-gold" />
              <h2 className="font-display text-lg font-medium text-parchment">About this purchase</h2>
            </div>
            <p className="mb-4 font-body text-sm text-slate-light">
              No real payment was processed — Razorpay isn't connected to live credentials yet, so
              this checkout is simulated for demo purposes. Access to the chapter was granted
              directly, without a real transaction taking place.
            </p>
            <Button size="sm" onClick={() => setShowDisclaimer(false)} className="self-start">
              Got it
            </Button>
          </div>
        </div>
      )}
    </main>
  );
}