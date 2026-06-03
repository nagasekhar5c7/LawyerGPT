import type { Citation } from "../../types";

interface CitationCardProps {
  citations: Citation[];
}

export default function CitationCard({ citations }: CitationCardProps) {
  if (citations.length === 0) return null;

  return (
    <div className="mt-3 space-y-2" data-testid="citation-card">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
        Sources
      </p>
      <div className="flex flex-wrap gap-2">
        {citations.map((cite, idx) => (
          <div
            key={idx}
            className="flex items-center gap-1.5 rounded-md bg-blue-50 border border-blue-200 px-3 py-1.5 text-xs text-blue-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <span className="font-medium">{cite.document_name}</span>
            <span className="text-blue-500">p.{cite.page_number}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
