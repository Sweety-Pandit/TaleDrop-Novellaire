// Mirrors backend/app/schemas.py. Keep in sync when backend schemas change.

export type UserRole = "ADMIN" | "AUTHOR" | "READER";
export type NovelStatus = "DRAFT" | "PUBLISHED" | "COMPLETED";
export type ChapterStatus = "DRAFT" | "PUBLISHED";
export type PaymentStatus = "PENDING" | "SUCCESS" | "FAILED" | "REFUNDED";

export interface User {
  id: string;
  username: string;
  display_name: string;
  email: string;
  bio: string | null;
  avatar: string | null;
  role: UserRole;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface UserPublic {
  id: string;
  username: string;
  display_name: string;
  bio: string | null;
  avatar: string | null;
  role: UserRole;
  created_at: string;
}

export interface UserUpdate {
  display_name?: string;
  bio?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface AuthorBrief {
  id: string;
  username: string;
  display_name: string;
  avatar: string | null;
}

export interface Genre {
  id: string;
  name: string;
  slug: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface NovelListItem {
  id: string;
  title: string;
  slug: string;
  cover_image: string | null;
  language: string;
  status: NovelStatus;
  is_premium: boolean;
  average_rating: number;
  views: number;
  author: AuthorBrief;
  updated_at: string;
}

export interface Novel {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  cover_image: string | null;
  banner_image: string | null;
  language: string;
  status: NovelStatus;
  is_premium: boolean;
  price: number;
  views: number;
  likes: number;
  average_rating: number;
  author: AuthorBrief;
  genres: Genre[];
  tags: Tag[];
  chapter_count: number;
  created_at: string;
  updated_at: string;
}

export interface NovelCreate {
  title: string;
  description?: string;
  language?: string;
  is_premium?: boolean;
  price?: number;
  genre_ids?: string[];
  tag_ids?: string[];
}

export interface NovelUpdate {
  title?: string;
  description?: string;
  language?: string;
  is_premium?: boolean;
  price?: number;
  genre_ids?: string[];
  tag_ids?: string[];
}

export interface ChapterListItem {
  id: string;
  novel_id: string;
  chapter_number: number;
  title: string;
  is_premium: boolean;
  price: number;
  views: number;
  status: ChapterStatus;
  created_at: string;
  updated_at: string;
}

export interface ChapterCreate {
  chapter_number?: number;
  title: string;
  content: string;
  is_premium?: boolean;
  price?: number;
}

export interface ChapterUpdate {
  chapter_number?: number;
  title?: string;
  content?: string;
  is_premium?: boolean;
  price?: number;
}

export interface Chapter {
  id: string;
  novel_id: string;
  chapter_number: number;
  title: string;
  content: string | null;
  is_premium: boolean;
  price: number;
  views: number;
  status: ChapterStatus;
  locked: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReadingHistoryItem {
  id: string;
  novel_id: string;
  chapter_id: string;
  last_read_at: string;
  novel_title: string;
  novel_slug: string;
  novel_cover_image: string | null;
  chapter_title: string;
  chapter_number: number;
}

export interface LibraryItem {
  id: string;
  novel_id: string;
  novel_title: string;
  novel_slug: string;
  novel_cover_image: string | null;
  novel_status: NovelStatus;
  created_at: string;
}

export interface ChapterBookmark {
  id: string;
  novel_id: string;
  novel_title: string;
  novel_slug: string;
  chapter_id: string;
  chapter_title: string;
  chapter_number: number;
  created_at: string;
}

export interface Review {
  id: string;
  novel_id: string;
  user: UserPublic;
  rating: number;
  content: string | null;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  novel_id: string;
  chapter_id: string | null;
  user: UserPublic;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface PurchaseHistoryItem {
  id: string;
  novel_id: string | null;
  novel_title: string;
  novel_slug: string | null;
  chapter_id: string | null;
  chapter_title: string | null;
  amount: number;
  currency: string;
  status: PaymentStatus;
  created_at: string;
}

export interface PaymentOrder {
  payment_id: string;
  razorpay_order_id: string;
  razorpay_key_id: string;
  amount: number;
  currency: string;
  novel_id: string;
  chapter_id: string | null;
}

export interface AISummary {
  novel_id: string;
  summary: string;
}

export interface AISource {
  chapter_id: string;
  chapter_number: number;
  chapter_title: string;
  snippet: string;
}

export interface AIAskResponse {
  novel_id: string;
  question: string;
  answer: string;
  sources: AISource[];
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiErrorBody {
  detail: string | { msg: string; loc: (string | number)[] }[];
}

export interface MessageResponse {
  message: string;
}
