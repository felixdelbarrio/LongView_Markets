export function EmptyState({ message }: { message: string }) {
  return (
    <p className="rounded-lg border border-dashed border-line bg-panel p-6 text-sm text-muted">
      {message}
    </p>
  );
}
