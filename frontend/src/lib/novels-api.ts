import { api } from "@/lib/api";
import type {
  Novel,
  NovelListItem,
  Chapter,
  ChapterListItem,
  LibraryItem,
  MessageResponse,
} from "@/types";

export interface BrowseNovelsParams {
  search?: string;
  genre?: string;
  author?: string;
  skip?: number;
  limit?: number;
}

export async function browseNovels(params: BrowseNovelsParams = {}): Promise<NovelListItem[]> {
  const { data } = await api.get<NovelListItem[]>("/novels", { params });
  return data;
}

export async function getNovelBySlug(slug: string): Promise<Novel> {
  const { data } = await api.get<Novel>(`/novels/${slug}`);
  return data;
}

export async function listNovelChapters(slug: string): Promise<ChapterListItem[]> {
  const { data } = await api.get<ChapterListItem[]>(`/novels/${slug}/chapters`);
  return data;
}

export async function getChapter(slug: string, chapterNumber: number): Promise<Chapter> {
  const { data } = await api.get<Chapter>(`/novels/${slug}/chapters/${chapterNumber}`);
  return data;
}

export async function addToLibrary(novelId: string): Promise<LibraryItem> {
  const { data } = await api.post<LibraryItem>(`/users/me/library/${novelId}`);
  return data;
}

export async function removeFromLibrary(novelId: string): Promise<MessageResponse> {
  const { data } = await api.delete<MessageResponse>(`/users/me/library/${novelId}`);
  return data;
}

export async function getMyLibrary(): Promise<LibraryItem[]> {
  const { data } = await api.get<LibraryItem[]>("/users/me/library");
  return data;
}

export async function recordReadingProgress(
  novelId: string,
  chapterId: string
): Promise<void> {
  await api.post("/users/me/reading-history", { novel_id: novelId, chapter_id: chapterId });
}
