import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export default function Input({ label, ...props }: InputProps) {
  if (!label) return <input {...props} />;
  return (
    <label>
      {label}
      <input {...props} />
    </label>
  );
}
