import React from 'react';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  error?: string | null;
}

/**
 * TextInput component renders a textarea for user input along with
 * a submit button.  Error messages are displayed when present.
 */
const TextInput: React.FC<Props> = ({ value, onChange, onSubmit, error }) => {
  return (
    <div className="flex flex-col gap-2">
      <textarea
        className="w-full h-40 p-2 border rounded focus:outline-none focus:ring focus:border-accent"
        placeholder="ここにテキストを入力してください…"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {error && <span className="text-red-500 text-sm">{error}</span>}
      <button
        className="self-start px-4 py-2 bg-accent text-white rounded hover:bg-blue-600"
        onClick={onSubmit}
      >
        リライト
      </button>
    </div>
  );
};

export default TextInput;