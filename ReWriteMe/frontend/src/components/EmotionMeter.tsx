import React from 'react';

interface Props {
  sentiments: string[];
}

/**
 * EmotionMeter visualises the sentiment of each rewrite option.  Each
 * bar corresponds to a rewrite and is coloured according to the
 * sentiment label.  The legend provides context for the colour
 * mapping.
 */
const EmotionMeter: React.FC<Props> = ({ sentiments }) => {
  const colourFor = (emotion: string) => {
    switch (emotion?.toLowerCase()) {
      case 'joy':
        return 'bg-yellow-400';
      case 'sad':
      case 'anger':
        return 'bg-red-600';
      case 'neutral':
      default:
        return 'bg-accent';
    }
  };

  return (
    <div className="p-4 border rounded bg-white shadow-sm">
      <h3 className="font-medium mb-2">感情トーン</h3>
      <div className="flex space-x-2">
        {sentiments.map((emotion, idx) => (
          <div
            key={idx}
            className={`flex-1 h-4 rounded ${colourFor(emotion)}`}
            title={`${idx + 1}: ${emotion}`}
          />
        ))}
      </div>
      <div className="mt-2 text-xs text-gray-500">
        <span className="inline-block w-3 h-3 bg-yellow-400 mr-1"></span>joy
        <span className="inline-block w-3 h-3 bg-red-600 mx-2"></span>sad/anger
        <span className="inline-block w-3 h-3 bg-accent mr-1"></span>neutral
      </div>
    </div>
  );
};

export default EmotionMeter;