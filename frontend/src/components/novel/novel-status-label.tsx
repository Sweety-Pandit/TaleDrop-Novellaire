import { cn } from "@/lib/utils";
import type { NovelStatus } from "@/types";

interface NovelStatusLabelProps {
  status: NovelStatus;
  className?: string;
}

/**
 * Small status label shown on a novel's cover: green "Ongoing" for a
 * published-but-not-finished novel, orange "Completed" once the author
 * has marked it done. Not shown for DRAFT novels (those never appear
 * in public-facing views to begin with).
 */
export function NovelStatusLabel({ status, className }: NovelStatusLabelProps) {
  if (status !== "PUBLISHED" && status !== "COMPLETED") return null;

  const isCompleted = status === "COMPLETED";

  return (
    <span
      className={cn(
        "rounded bg-ink/80 px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider backdrop-blur-sm",
        isCompleted ? "text-ember" : "text-moss-light",
        className
      )}
    >
      {isCompleted ? "Completed" : "Ongoing"}
    </span>
  );
}
