import * as React from "react";
import { cn } from "@/lib/utils";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "error" | "success";
}

export function Alert({ variant = "error", className, children, ...props }: AlertProps) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded border px-3 py-2 font-body text-sm",
        variant === "error" && "border-ember-dark/60 bg-ember-dark/10 text-ember-light",
        variant === "success" && "border-moss/60 bg-moss/10 text-moss-light",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
