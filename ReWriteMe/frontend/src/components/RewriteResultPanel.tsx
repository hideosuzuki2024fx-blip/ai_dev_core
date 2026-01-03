import React from 'react';

interface Props {
  original: string;
  options: string[];
  sentiments: string[];
}

/**
 * RewriteResultPanel lists generated rewrite options along with
 * their associated sentiment labels.  Users can quickly scan the
 * suggestions before exploring the detailed comparisons on the right.
 */
const RewriteResultPanel: React.FC<Props> = ({ original, options, sentiments }) => {
  return (
    <div className="mt-4">
      <h2 className="font-semibold mb-2">リライト案</h2>
      <ul className="space-y-2">
        {options.map((opt, idx) => (
          <li key={idx} className="p-2 border rounded bg-white shadow-sm">
            <div className="text-sm text-gray-600">案 {idx + 1} ({sentiments[idx] || 'neutral'})</div>
            <p className="mt-1 whitespace-pre-line">{opt}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RewriteResultPanel;