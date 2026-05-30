export function ErrorState({ message }: { message: string }) {
  return (
    <p className="rounded-lg border border-red-400/40 bg-red-400/10 p-4 text-sm text-red-300">
      {message}
    </p>
  );
}
