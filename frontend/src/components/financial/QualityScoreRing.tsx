export function QualityScoreRing({ score }: { score: number }) {
  return (
    <div className="grid h-24 w-24 place-items-center rounded-full border-8 border-teal/30 bg-teal/10 text-center">
      <span className="text-2xl font-bold text-teal">{Math.round(score)}</span>
    </div>
  );
}
