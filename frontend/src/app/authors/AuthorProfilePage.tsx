import * as React from "react";
import { useParams } from "react-router-dom";
import { getPublicProfile } from "@/lib/user-api";
import { browseNovels } from "@/lib/novels-api";
import { NovelCard } from "@/components/novel/novel-card";
import { getMediaUrl } from "@/lib/utils";
import { extractErrorMessage } from "@/lib/api";
import type { UserPublic, NovelListItem } from "@/types";

export default function AuthorProfilePage() {
  const { username = "" } = useParams<{ username: string }>();
  const [author, setAuthor] = React.useState<UserPublic | null>(null);
  const [novels, setNovels] = React.useState<NovelListItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      try {
        const [authorData, novelsData] = await Promise.all([
          getPublicProfile(username),
          browseNovels({ author: username, limit: 40 }),
        ]);
        setAuthor(authorData);
        setNovels(novelsData);
      } catch (err) {
        setError(extractErrorMessage(err));
      } finally {
        setIsLoading(false);
      }
    })();
  }, [username]);

  if (isLoading) {
    return <p className="mx-auto max-w-4xl px-6 py-10 font-body text-sm text-slate-light">Loading…</p>;
  }

  if (error || !author) {
    return (
      <p className="mx-auto max-w-4xl px-6 py-10 font-body text-sm text-slate-light">
        {error ?? "Author not found."}
      </p>
    );
  }

  const avatarUrl = getMediaUrl(author.avatar);

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-10 flex items-center gap-4">
        <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-full bg-ink-soft">
          {avatarUrl ? (
            <img src={avatarUrl} alt={author.display_name} className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center font-display text-xl text-slate-light">
              {author.display_name.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div>
          <h1 className="font-display text-2xl font-medium text-parchment">{author.display_name}</h1>
          <p className="font-body text-sm text-slate-light">@{author.username}</p>
          {author.bio && <p className="mt-2 font-body text-sm text-parchment-dim">{author.bio}</p>}
        </div>
      </div>

      <h2 className="mb-4 font-display text-lg font-medium text-parchment">Published novels</h2>
      {novels.length === 0 ? (
        <p className="font-body text-sm text-slate-light">No published novels yet.</p>
      ) : (
        <div className="grid grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {novels.map((novel) => (
            <NovelCard key={novel.id} novel={novel} />
          ))}
        </div>
      )}
    </main>
  );
}
