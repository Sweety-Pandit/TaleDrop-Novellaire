import type { PaymentOrder } from "@/types";

declare global {
  interface Window {
    Razorpay: new (options: RazorpayOptions) => { open: () => void };
  }
}

interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description?: string;
  order_id: string;
  prefill?: { email?: string; name?: string };
  theme?: { color?: string };
  handler: (response: RazorpaySuccessResponse) => void;
  modal?: { ondismiss?: () => void };
}

export interface RazorpaySuccessResponse {
  razorpay_payment_id: string;
  razorpay_order_id: string;
  razorpay_signature: string;
}

let scriptLoadPromise: Promise<void> | null = null;

function loadRazorpayScript(): Promise<void> {
  if (typeof window !== "undefined" && window.Razorpay) return Promise.resolve();

  scriptLoadPromise =
    scriptLoadPromise ??
    new Promise<void>((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Razorpay checkout script"));
      document.body.appendChild(script);
    });

  return scriptLoadPromise;
}

/**
 * Opens the Razorpay checkout widget for a previously-initiated order.
 * Resolves with the payment response on success, or rejects if the
 * reader closes the widget without paying.
 */
export async function openRazorpayCheckout(
  order: PaymentOrder,
  opts: { title: string; userEmail?: string; userName?: string }
): Promise<RazorpaySuccessResponse> {
  await loadRazorpayScript();

  return new Promise((resolve, reject) => {
    const razorpay = new window.Razorpay({
      key: order.razorpay_key_id,
      amount: Math.round(order.amount * 100),
      currency: order.currency,
      name: "TaleDrop-Novellaire",
      description: opts.title,
      order_id: order.razorpay_order_id,
      prefill: { email: opts.userEmail, name: opts.userName },
      theme: { color: "#C1502E" },
      handler: (response) => resolve(response),
      modal: { ondismiss: () => reject(new Error("Payment cancelled")) },
    });
    razorpay.open();
  });
}
