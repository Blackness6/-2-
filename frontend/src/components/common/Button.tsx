import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "ghost" | "danger";

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: "btn-primary",
  ghost: "btn-ghost",
  danger: "btn-danger",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export default function Button({ variant, className, ...props }: ButtonProps) {
  const classes = [variant && VARIANT_CLASS[variant], className].filter(Boolean).join(" ");
  return <button className={classes || undefined} {...props} />;
}
