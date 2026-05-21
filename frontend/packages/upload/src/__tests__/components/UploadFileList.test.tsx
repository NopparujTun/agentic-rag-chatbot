import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import UploadFileList from '../../components/UploadFileList';

describe('UploadFileList', () => {
  it('renders empty list', () => {
    const { container } = render(<UploadFileList files={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders files', () => {
    const file1 = new File([''], 'test1.pdf', { type: 'application/pdf' });
    const file2 = new File([''], 'test2.txt', { type: 'text/plain' });
    
    render(<UploadFileList files={[file1, file2]} />);
    expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test2.txt')).toBeInTheDocument();
  });
});
