export function ResponsibleGamingFooter() {
  return (
    <footer className="fixed bottom-0 left-0 right-0 z-20 border-t border-primary/30 bg-[#0D0D0D]/95 px-4 py-2 text-center text-xs text-foreground/70 backdrop-blur">
      <span className="font-semibold text-primary">+18</span> · Apostas envolvem risco real
      de perda de dinheiro e podem causar dependência. Jogue com responsabilidade. Precisa de
      apoio?{" "}
      <a
        href="https://jogadoresanonimos.com.br"
        target="_blank"
        rel="noopener noreferrer"
        className="underline hover:text-primary"
      >
        jogadoresanonimos.com.br
      </a>
    </footer>
  );
}
