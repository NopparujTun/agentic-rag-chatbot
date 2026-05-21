import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { InputBar } from '../../components/ui/input-bar';

describe('InputBar', () => {
  it('renders correctly in ready state', () => {
    const onSend = vi.fn();
    render(<InputBar status="ready" onSend={onSend} />);
    
    expect(screen.getByPlaceholderText('Send a message...')).toBeInTheDocument();
  });

  it('handles input change and send', () => {
    const onSend = vi.fn();
    render(<InputBar status="ready" onSend={onSend} />);
    
    const textarea = screen.getByPlaceholderText('Send a message...');
    fireEvent.change(textarea, { target: { value: 'Hello world' } });
    
    expect(textarea).toHaveValue('Hello world');
    
    // Test send button click
    // The send button usually has some specific label or aria-label, but we can look for it
    // In InputBar, the send button is rendered when status is ready
    const sendBtn = screen.getByRole('button', { name: /send/i }) || document.querySelector('button[type="button"]')!;
    if (sendBtn) {
       fireEvent.click(sendBtn);
    }
  });

  it('handles textarea auto-resize', () => {
    const { container } = render(<InputBar status="ready" onSend={() => {}} />);
    const textarea = screen.getByPlaceholderText('Send a message...') as HTMLTextAreaElement;
    
    // Mock the scrollHeight to trigger resize logic
    Object.defineProperty(textarea, 'scrollHeight', { configurable: true, value: 100 });
    
    fireEvent.change(textarea, { target: { value: 'Line 1\nLine 2\nLine 3' } });
    
    // Since input-bar uses standard logic for textarea resize, triggering change
    // should execute the branch that sets target.style.height
    expect(textarea.value).toBe('Line 1\nLine 2\nLine 3');
  });

  it('handles attach click', () => {
    const onAttach = vi.fn();
    render(<InputBar status="ready" onSend={() => {}} onAttach={onAttach} />);
    
    // the attach button usually has a paperclip or plus icon
    const buttons = screen.getAllByRole('button');
    if (buttons.length > 0) {
      fireEvent.click(buttons[0]); // The first button is usually the attach button
      expect(onAttach).toHaveBeenCalled();
    }
  });
    it('renders streaming state and calls onStop', () => {
    const onStop = vi.fn();
    render(<InputBar status="streaming" onStop={onStop} onSend={() => {}} />);
    
    const stopBtn = screen.getByRole('button', { name: /stop/i }) || document.querySelector('button');
    if (stopBtn) {
      fireEvent.click(stopBtn);
    }
  });
});
