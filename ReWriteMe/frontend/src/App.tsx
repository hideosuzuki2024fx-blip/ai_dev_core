import React, { useState } from 'react';
import axios from 'axios';
import TextInput from './components/TextInput';
import RewriteResultPanel from './components/RewriteResultPanel';
import EmotionMeter from './components/EmotionMeter';
import ComparisonView from './components/ComparisonView';
import HistorySidebar from './components/HistorySidebar';

// Root component orchestrating the layout and API calls
const App: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [options, setOptions] = useState<string[]>([]);
  const [sentiments, setSentiments] = useState<string[]>([]);
  const [historyId, setHistoryId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRewrite = async () => {
    setError(null);
    if (!inputText.trim()) {
      setError('テキストを入力してください。');
      return;
    }
    try {
      const response = await axios.post('/rewrite', { text: inputText });
      const data = response.data;
      setOptions(data.options.map((opt: any) => opt.text));
      setSentiments(data.options.map((opt: any) => opt.emotion));
      setHistoryId(data.history_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'リライトに失敗しました');
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* History Sidebar */}
      <div className="w-1/4 bg-white border-r hidden lg:block">
        <HistorySidebar />
      </div>
      {/* Main content */}
      <div className="flex-1 p-4 flex flex-col overflow-y-auto">
        {/* Header */}
        <header className="mb-4">
          <h1 className="text-2xl font-bold text-accent">ReWriteMe</h1>
          <p className="text-sm text-gray-600">共に書き直すAI</p>
        </header>
        {/* Input and Results */}
        <div className="flex flex-col lg:flex-row gap-4 flex-1">
          <div className="lg:w-1/2">
            <TextInput
              value={inputText}
              onChange={setInputText}
              onSubmit={handleRewrite}
              error={error}
            />
            {options.length > 0 && (
              <RewriteResultPanel
                original={inputText}
                options={options}
                sentiments={sentiments}
              />
            )}
          </div>
          {/* Right side: emotion meter & comparison */}
          {options.length > 0 && (
            <div className="lg:w-1/2 flex flex-col gap-4">
              <EmotionMeter sentiments={sentiments} />
              {/* Show comparison for each rewrite */}
              {options.map((opt, idx) => (
                <ComparisonView
                  key={idx}
                  original={inputText}
                  rewrite={opt}
                  index={idx}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;