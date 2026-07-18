import * as React from "react";

export function ReadingProgressRail() {
  const [progress, setProgress] = React.useState(0);

  React.useEffect(() => {
    function handleScroll() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? Math.min(100, Math.max(0, (scrollTop / docHeight) * 100)) : 0;
      setProgress(pct);
    }
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div
      className="fixed left-0 top-16 z-10 hidden h-[calc(100vh-4rem)] w-1.5 bg-ink-soft md:block"
      aria-hidden="true"
    >
      <div
        className="w-full bg-ember transition-[height] duration-150 ease-out"
        style={{ height: `${progress}%` }}
      />
    </div>
  );
}
