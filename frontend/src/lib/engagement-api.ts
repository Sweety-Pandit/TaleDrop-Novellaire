import { api } from "@/lib/api";
import type {
  Review,
  Comment,
  MessageResponse,
  AISummary,
  AIAskResponse,
  NovelListItem,
} from "@/types";

// --- Reviews ---
export async function listReviews(novelId: string): Promise<Review[]> {
  const { data } = await api.get<Review[]>(`/novels/${novelId}/reviews`);
  return data;
}

export async function submitReview(
  novelId: string,
  payload: { rating: number; content?: string }
): Promise<Review> {
  const { data } = await api.post<Review>(`/novels/${novelId}/reviews`, payload);
  return data;
}

export async function deleteReview(reviewId: string): Promise<MessageResponse> {
  const { data } = await api.delete<MessageResponse>(`/reviews/${reviewId}`);
  return data;
}

// --- Comments ---
export async function listComments(novelId: string, chapterId?: string): Promise<Comment[]> {
  const { data } = await api.get<Comment[]>(`/novels/${novelId}/comments`, {
    params: chapterId ? { chapter_id: chapterId } : undefined,
  });
  return data;
}

export async function postComment(
  novelId: string,
  content: string,
  chapterId?: string
): Promise<Comment> {
  const { data } = await api.post<Comment>(`/novels/${novelId}/comments`, {
    content,
    chapter_id: chapterId,
  });
  return data;
}

export async function deleteComment(commentId: string): Promise<MessageResponse> {
  const { data } = await api.delete<MessageResponse>(`/comments/${commentId}`);
  return data;
}

// --- AI ---
export async function getNovelSummary(novelId: string): Promise<AISummary> {
  const { data } = await api.get<AISummary>(`/novels/${novelId}/ai/summary`);
  return data;
}

export async function askNovelQuestion(novelId: string, question: string): Promise<AIAskResponse> {
  const { data } = await api.post<AIAskResponse>(`/novels/${novelId}/ai/ask`, { question });
  return data;
}

export async function getMyRecommendations(): Promise<NovelListItem[]> {
  const { data } = await api.get<NovelListItem[]>("/users/me/recommendations");
  return data;
}
