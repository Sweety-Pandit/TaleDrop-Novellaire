import { api } from "@/lib/api";
import type { PaymentOrder, PurchaseHistoryItem } from "@/types";

export async function initiateChapterPurchase(chapterId: string): Promise<PaymentOrder> {
  const { data } = await api.post<PaymentOrder>(`/payments/chapters/${chapterId}/initiate`);
  return data;
}

export async function initiateNovelPurchase(novelId: string): Promise<PaymentOrder> {
  const { data } = await api.post<PaymentOrder>(`/payments/novels/${novelId}/initiate`);
  return data;
}

export async function confirmPayment(payload: {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}): Promise<PurchaseHistoryItem> {
  const { data } = await api.post<PurchaseHistoryItem>("/payments/confirm", payload);
  return data;
}

export async function getPurchaseHistory(): Promise<PurchaseHistoryItem[]> {
  const { data } = await api.get<PurchaseHistoryItem[]>("/payments/me");
  return data;
}
