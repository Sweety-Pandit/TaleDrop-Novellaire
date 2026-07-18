import { api } from "@/lib/api";
import type { NovelListItem, UserPublic } from "@/types";

export async function searchNovels(query: string): Promise<NovelListItem[]> {
  const { data } = await api.get<NovelListItem[]>("/search/novels", { params: { q: query } });
  return data;
}

export async function searchAuthors(query: string): Promise<UserPublic[]> {
  const { data } = await api.get<UserPublic[]>("/search/authors", { params: { q: query } });
  return data;
}
