export function Logo({ size = 36 }: { size?: number }) {
  return (
    <div className="flex items-center gap-2">
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        className="shrink-0 drop-shadow-[0_0_10px_rgba(255,107,0,0.45)]"
      >
        <defs>
          <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF6B00" />
            <stop offset="100%" stopColor="#F0B429" />
          </linearGradient>
        </defs>
        <polygon
          points="50,3 93,26 93,74 50,97 7,74 7,26"
          fill="url(#logo-gradient)"
        />
        <text
          x="50"
          y="62"
          textAnchor="middle"
          fontFamily="var(--font-inter), sans-serif"
          fontWeight="800"
          fontSize="38"
          fill="#080B14"
        >
          BA
        </text>
      </svg>
      <span className="text-lg font-bold tracking-tight text-foreground">
        Bet<span className="text-primary">Analyzer</span>
      </span>
    </div>
  );
}
