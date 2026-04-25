export const TypingIndicator = () => (
  <div className="flex animate-fade-in items-end gap-3">
    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-hero text-primary-foreground shadow-soft">
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 10 12 4l9 6" />
        <path d="M5 10v8h14v-8" />
      </svg>
    </span>
    <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md border border-border/60 bg-card px-4 py-3 shadow-bubble">
      <span className="typing-dot" style={{ animationDelay: "0ms" }} />
      <span className="typing-dot" style={{ animationDelay: "150ms" }} />
      <span className="typing-dot" style={{ animationDelay: "300ms" }} />
    </div>
  </div>
);
