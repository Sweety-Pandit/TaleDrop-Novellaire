import { ChevronLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

interface BackButtonProps {
  /** Optional explicit destination. If omitted, goes to the previous
   * entry in the browser history (like clicking the browser's back
   * button), which is usually what feels natural after a deep link. */
  to?: string;
  label?: string;
  className?: string;
}

export function BackButton({ to, label = "Back", className }: BackButtonProps) {
  const navigate = useNavigate();

  return (
    <button
      type="button"
      onClick={() => (to ? navigate(to) : navigate(-1))}
      className={cn(
        "inline-flex items-center gap-1 font-body text-xs text-slate-light transition-colors hover:text-ember",
        className
      )}
    >
      <ChevronLeft className="h-4 w-4" />
      {label}
    </button>
  );
}
