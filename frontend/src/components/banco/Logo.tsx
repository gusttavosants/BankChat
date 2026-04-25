export const Logo = ({ className = "" }: { className?: string }) => (
  <div className={`flex items-center gap-2.5 ${className}`}>
    <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-gold shadow-soft">
      <svg viewBox="0 0 24 24" className="h-5 w-5 text-primary" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 10 12 4l9 6" />
        <path d="M5 10v8h14v-8" />
        <path d="M9 18v-5M15 18v-5" />
      </svg>
    </div>
    <div className="leading-tight">
      <div className="font-display text-lg font-semibold tracking-tight">Banco Ágil</div>
      <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">Atendimento inteligente</div>
    </div>
  </div>
);
