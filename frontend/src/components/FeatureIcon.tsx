import type { ReactElement } from "react";

const ICONS: Record<string, ReactElement> = {
  people: (
    <path d="M12 12c2.2 0 4-1.8 4-4s-1.8-4-4-4-4 1.8-4 4 1.8 4 4 4zm0 2c-2.7 0-8 1.3-8 4v2h16v-2c0-2.7-5.3-4-8-4z" />
  ),
  shield: (
    <path d="M12 2l8 3v6c0 5-3.4 8.7-8 10-4.6-1.3-8-5-8-10V5l8-3zm0 2.2L6 6.4V11c0 3.8 2.5 6.8 6 7.9 3.5-1.1 6-4.1 6-7.9V6.4l-6-2.2z" />
  ),
  hoodie: (
    <path d="M12 2c-1.4 0-2.6.8-3.2 2L4 6v4l2-.7V20h12V9.3l2 .7V6l-4.8-2C14.6 2.8 13.4 2 12 2zm-1 2.3c.3.4.7.7 1 .7s.7-.3 1-.7c.5.1.9.4 1.2.8L12 7 9.8 5.1c.3-.4.7-.7 1.2-.8z" />
  ),
  sparkle: (
    <path d="M12 2l1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2zm6 12l.9 2.6L21.5 17l-2.6.9L18 20.5l-.9-2.6L14.5 17l2.6-.9L18 14zM5 14l.9 2.6L8.5 17l-2.6.9L5 20.5l-.9-2.6L1.5 17l2.6-.9L5 14z" />
  ),
  ruler: (
    <path d="M3 7h18a1 1 0 011 1v8a1 1 0 01-1 1H3a1 1 0 01-1-1V8a1 1 0 011-1zm2 2v4h1v-4H5zm3 0v2h1V9H8zm3 0v4h1v-4h-1zm3 0v2h1V9h-1zm3 0v4h1v-4h-1z" />
  ),
  chat: (
    <path d="M4 4h16a1 1 0 011 1v11a1 1 0 01-1 1H9l-4.3 3.6A1 1 0 013 19.8V6a1 1 0 011-1zm2.5 5a1 1 0 100 2 1 1 0 000-2zm4.5 0a1 1 0 100 2 1 1 0 000-2zm4.5 0a1 1 0 100 2 1 1 0 000-2z" />
  ),
};

export default function FeatureIcon({ name }: { name: keyof typeof ICONS }) {
  return (
    <div className="feature-icon">
      <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true">
        {ICONS[name]}
      </svg>
    </div>
  );
}
