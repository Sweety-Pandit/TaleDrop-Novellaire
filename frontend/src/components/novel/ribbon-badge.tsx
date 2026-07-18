import { cn } from "@/lib/utils";

interface RibbonBadgeProps {
  label: string;
  tone?: "ember" | "gold";
  className?: string;
}

/**
 * A small ribbon that appears to hang from the top edge of a novel
 * cover, cut with a V-notch at the bottom like a physical bookmark
 * ribbon. Used to mark premium novels/chapters and, elsewhere, as the
 * base visual for the reading-progress rail.
 */
export function RibbonBadge({ label, tone = "ember", className }: RibbonBadgeProps) {
  return (
    <div
      className={cn(
        "absolute right-3 top-0 flex w-7 justify-center pb-3 pt-2 font-mono text-[10px] font-medium uppercase tracking-wider text-parchment shadow-md",
        tone === "ember" ? "bg-ember" : "bg-gold",
        className
      )}
      style={{
        clipPath: "polygon(0 0, 100% 0, 100% 100%, 50% 82%, 0 100%)",
        writingMode: "vertical-rl",
      }}
    >
      <span>{label}</span>
    </div>
  );
}
