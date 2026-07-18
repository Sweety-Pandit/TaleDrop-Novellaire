import * as React from "react";
import { Link } from "react-router-dom";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { getPurchaseHistory } from "@/lib/payments-api";
import { cn } from "@/lib/utils";
import type { PurchaseHistoryItem, PaymentStatus } from "@/types";

const STATUS_STYLES: Record<PaymentStatus, string> = {
  PENDING: "bg-ink-soft text-slate-light",
  SUCCESS: "bg-moss/20 text-moss-light",
  FAILED: "bg-ember/20 text-ember-light",
  REFUNDED: "bg-gold/20 text-gold",
};

export default function PurchaseHistoryPage() {
  const { isReady } = useRequireAuth();
  const [purchases, setPurchases] = React.useState<PurchaseHistoryItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    if (!isReady) return;
    getPurchaseHistory()
      .then(setPurchases)
      .finally(() => setIsLoading(false));
  }, [isReady]);

  if (!isReady) {
    return <p className="mx-auto max-w-2xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-8 font-display text-3xl font-medium text-parchment">Purchase history</h1>

      {isLoading ? (
        <p className="font-body text-sm text-slate-light">Loading…</p>
      ) : purchases.length === 0 ? (
        <p className="font-body text-sm text-slate-light">No purchases yet.</p>
      ) : (
        <ul className="divide-y divide-ink-border rounded border border-ink-border">
          {purchases.map((purchase) => (
            <li key={purchase.id} className="flex items-center justify-between px-4 py-3">
              <div>
                {purchase.novel_slug ? (
                  <Link
                    to={`/novels/${purchase.novel_slug}`}
                    className="font-body text-sm text-parchment hover:text-ember"
                  >
                    {purchase.novel_title}
                  </Link>
                ) : (
                  <span className="font-body text-sm text-parchment">{purchase.novel_title}</span>
                )}
                {purchase.chapter_title && (
                  <p className="font-body text-xs text-slate-light">{purchase.chapter_title}</p>
                )}
                <p className="font-mono text-[10px] text-slate-light">
                  {new Date(purchase.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-body text-sm text-parchment">
                  {purchase.currency} {purchase.amount.toFixed(2)}
                </span>
                <span
                  className={cn(
                    "rounded px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide",
                    STATUS_STYLES[purchase.status]
                  )}
                >
                  {purchase.status}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
