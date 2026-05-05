import { useState, useEffect } from 'react';

const THINKING_STEPS = [
  'Rewriting query...',
  'Using tools...',
  'Searching knowledge base...',
  'Reading documents...',
  'Generating answer...'
];

interface ThinkingIndicatorProps {
  step?: number;
}

export function ThinkingIndicator({ step }: ThinkingIndicatorProps) {
  const [internalStep, setInternalStep] = useState(0);

  useEffect(() => {
    if (step !== undefined) {
      setInternalStep(step);
      return;
    }
    
    const interval = setInterval(() => {
      setInternalStep(prev => (prev < THINKING_STEPS.length - 1 ? prev + 1 : prev));
    }, 2000);
    
    return () => clearInterval(interval);
  }, [step]);

  const currentStep = Math.min(Math.max(internalStep, 0), THINKING_STEPS.length - 1);

  return (
    <div className="flex flex-col gap-3 py-2">
      {THINKING_STEPS.map((label, index) => {
        const isCompleted = index < currentStep;
        const isActive = index === currentStep;
        const isPending = index > currentStep;

        if (isPending) return null;

        return (
          <div 
            key={index} 
            className={`flex items-center gap-3 text-sm transition-opacity duration-500 animate-[fadeIn_0.3s_ease-out] ${
              isActive ? 'text-gray-800' : 'text-gray-400'
            }`}
          >
            <div className="flex items-center justify-center w-4 h-4">
              {isCompleted ? (
                <svg className="w-3.5 h-3.5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              ) : isActive ? (
                <div className="w-3.5 h-3.5 border-2 border-gray-200 border-t-gray-800 rounded-full animate-spin" />
              ) : null}
            </div>
            <span className={`${isActive ? 'animate-pulse font-medium' : ''}`}>
              {label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
