import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function ChapterContent({ content }: { content: string }) {
  return (
    <div className="prose-reading font-reading text-[1.15rem] leading-8 text-parchment">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
