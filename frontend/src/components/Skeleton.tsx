export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-foreground/10 ${className}`} />;
}

export function GameCardSkeleton() {
  return (
    <div className="rounded-lg border border-foreground/10 bg-[#161616] p-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-3 w-16" />
      </div>
      <div className="mt-4 flex items-center justify-between gap-4">
        <Skeleton className="h-4 w-2/5" />
        <Skeleton className="h-4 w-8" />
        <Skeleton className="h-4 w-2/5" />
      </div>
      <div className="mt-4 flex gap-2">
        <Skeleton className="h-6 w-14" />
        <Skeleton className="h-6 w-14" />
        <Skeleton className="h-6 w-14" />
      </div>
    </div>
  );
}

export function AnalysisSkeleton() {
  return (
    <div className="space-y-3 rounded-lg border border-foreground/10 bg-[#161616] p-4">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-5/6" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}
