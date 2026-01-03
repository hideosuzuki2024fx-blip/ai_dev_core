import React from 'react';

interface Props {
  original: string;
  rewrite: string;
  index: number;
}

/**
 * ComparisonView shows the original and rewritten text side by side.  A simple
 * heuristic highlights words in the rewrite that were not present in the
 * original.  This allows users to quickly spot differences without a full
 * diff algorithm.
 */
const ComparisonView: React.FC<Props> = ({ original, rewrite, index }) => {
  const originalWords = new Set(original.split(/\s+/));
  const rewriteWords = rewrite.split(/\s+/);

  const renderHighlighted = () => {
    return rewriteWords.map((word, i) => {
      const key = `${index}-${i}`;
      if (!originalWords.has(word)) {
        return (
          <mark key={key} className="bg-yellow-200">
            {word + ' '}
          </mark>
        );
      }
      return word + ' ';
    });
  };

  return (
    <div className="border rounded bg-white p-3 shadow-sm">
      <h4 className="font-semibold text-sm mb-2">案 {index + 1} 比較</h4>
      <div className="flex flex-col">
        <div className="mb-1 text-xs text-gray-600">原文:</div>
        <p className="mb-2 whitespace-pre-line text-sm bg-gray-50 p-2 rounded">
          {original}
        </p>
        <div className="mb-1 text-xs text-gray-600">リライト:</div>
        <p className="whitespace-pre-line text-sm bg-gray-50 p-2 rounded">
          {renderHighlighted()}
        </p>
      </div>
    </div>
  );
};

export default ComparisonView;