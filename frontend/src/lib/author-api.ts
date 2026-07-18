import { api } from "@/lib/api";
import type {
  Novel,
  NovelListItem,
  NovelCreate,
  NovelUpdate,
  Chapter,
  ChapterCreate,
  ChapterUpdate,
  ChapterListItem,
  MessageResponse,
  Genre,
  Tag,
} from "@/types";

export async function listMyNovels(): Promise<NovelListItem[]> {
  const { data } = await api.get<NovelListItem[]>("/novels/me");
  return data;
}

export async function createNovel(payload: NovelCreate): Promise<Novel> {
  const { data } = await api.post<Novel>("/novels", payload);
  return data;
}

export async function updateNovel(novelId: string, payload: NovelUpdate): Promise<Novel> {
  const { data } = await api.put<Novel>(`/novels/${novelId}`, payload);
  return data;
}

export async function deleteNovel(novelId: string): Promise<MessageResponse> {
  const { data } = await api.delete<MessageResponse>(`/novels/${novelId}`);
  return data;
}

export async function publishNovel(novelId: string): Promise<Novel> {
  const { data } = await api.post<Novel>(`/novels/${novelId}/publish`);
  return data;
}

export async function unpublishNovel(novelId: string): Promise<Novel> {
  const { data } = await api.post<Novel>(`/novels/${novelId}/unpublish`);
  return data;
}

export async function completeNovel(novelId: string): Promise<Novel> {
  const { data } = await api.post<Novel>(`/novels/${novelId}/complete`);
  return data;
}

export async function uploadNovelCover(novelId: string, file: File): Promise<Novel> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<Novel>(`/novels/${novelId}/cover`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function uploadNovelBanner(novelId: string, file: File): Promise<Novel> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<Novel>(`/novels/${novelId}/banner`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function createChapter(
  novelId: string,
  payload: ChapterCreate
): Promise<ChapterListItem> {
  const { data } = await api.post<ChapterListItem>(`/novels/${novelId}/chapters`, payload);
  return data;
}

export async function getChapterById(slug: string, chapterId: string): Promise<Chapter> {
  // There's no direct "get chapter by id" route; fetch the table of
  // contents to find the chapter's number, then load full content by
  // (slug, chapter_number), which is how the reader route works too.
  const { data: chapters } = await api.get<ChapterListItem[]>(`/novels/${slug}/chapters`);
  const match = chapters.find((c) => c.id === chapterId);
  if (!match) throw new Error("Chapter not found");
  const { data } = await api.get<Chapter>(`/novels/${slug}/chapters/${match.chapter_number}`);
  return data;
}

export async function updateChapter(
  chapterId: string,
  payload: ChapterUpdate
): Promise<ChapterListItem> {
  const { data } = await api.put<ChapterListItem>(`/chapters/${chapterId}`, payload);
  return data;
}

export async function deleteChapter(chapterId: string): Promise<MessageResponse> {
  const { data } = await api.delete<MessageResponse>(`/chapters/${chapterId}`);
  return data;
}

export async function publishChapter(chapterId: string): Promise<ChapterListItem> {
  const { data } = await api.post<ChapterListItem>(`/chapters/${chapterId}/publish`);
  return data;
}

export async function unpublishChapter(chapterId: string): Promise<ChapterListItem> {
  const { data } = await api.post<ChapterListItem>(`/chapters/${chapterId}/unpublish`);
  return data;
}

export async function listGenres(): Promise<Genre[]> {
  const { data } = await api.get<Genre[]>("/genres");
  return data;
}

export async function listTags(): Promise<Tag[]> {
  const { data } = await api.get<Tag[]>("/tags");
  return data;
}
