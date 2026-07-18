import { api } from "@/lib/api";
import type {
  User,
  UserPublic,
  UserUpdate,
  ChangePasswordRequest,
  MessageResponse,
  ReadingHistoryItem,
  ChapterBookmark,
} from "@/types";

export async function getPublicProfile(username: string): Promise<UserPublic> {
  const { data } = await api.get<UserPublic>(`/users/${username}`);
  return data;
}

export async function updateProfile(payload: UserUpdate): Promise<User> {
  const { data } = await api.put<User>("/users/me", payload);
  return data;
}

export async function uploadAvatar(file: File): Promise<User> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<User>("/users/me/avatar", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function changePassword(payload: ChangePasswordRequest): Promise<MessageResponse> {
  const { data } = await api.put<MessageResponse>("/users/me/password", payload);
  return data;
}

export async function getReadingHistory(): Promise<ReadingHistoryItem[]> {
  const { data } = await api.get<ReadingHistoryItem[]>("/users/me/reading-history");
  return data;
}

export async function getChapterBookmarks(): Promise<ChapterBookmark[]> {
  const { data } = await api.get<ChapterBookmark[]>("/users/me/bookmarks");
  return data;
}
