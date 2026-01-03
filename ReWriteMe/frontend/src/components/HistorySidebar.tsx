import React from 'react';

/**
 * HistorySidebar is reserved for future implementation.  It will show
 * previous rewrites and allow users to restore or reuse their voice
 * memory.  For now it renders a placeholder.
 */
const HistorySidebar: React.FC = () => {
  return (
    <div className="p-4">
      <h3 className="font-semibold mb-2">履歴</h3>
      <p className="text-sm text-gray-600">近日公開予定です。</p>
    </div>
  );
};

export default HistorySidebar;