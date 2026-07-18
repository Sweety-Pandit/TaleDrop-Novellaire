import { Link } from "react-router-dom";
import { Star } from "lucide-react";
import type { NovelListItem } from "@/types";
import { RibbonBadge } from "@/components/novel/ribbon-badge";
import { NovelStatusLabel } from "@/components/novel/novel-status-label";
import { getMediaUrl } from "@/lib/utils";

export function NovelCard({ novel }: { novel: NovelListItem }) {
  const coverUrl = getMediaUrl(novel.cover_image);

  return (
    <Link to={`/novels/${novel.slug}`} className="group flex flex-col gap-2">
      <div className="relative aspect-[2/3] overflow-hidden rounded bg-ink-soft">
        {coverUrl ? (
          <img
            src={coverUrl}
            alt={novel.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center px-3 text-center font-display text-sm text-slate-light">
            {novel.title}
          </div>
        )}
        {novel.is_premium && <RibbonBadge label="Premium" tone="ember" />}
        <NovelStatusLabel status={novel.status} className="absolute bottom-2 left-2" />
      </div>

      <div>
        <h3 className="line-clamp-2 font-display text-sm font-medium leading-snug text-parchment group-hover:text-ember">
          {novel.title}
        </h3>
        <p className="mt-0.5 font-body text-xs text-slate-light">{novel.author.display_name}</p>
        <div className="mt-1 flex items-center gap-1 font-mono text-xs text-slate-light">
          <Star className="h-3 w-3 fill-gold text-gold" />
          {novel.average_rating > 0 ? novel.average_rating.toFixed(1) : "New"}
        </div>
      </div>
    </Link>
  );
}
