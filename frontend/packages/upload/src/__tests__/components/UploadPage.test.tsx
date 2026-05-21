import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import UploadPage from '../../components/UploadPage';

vi.mock('../../components/UploadDropzone', () => ({
  default: ({ onDrop, onFileInput, isDragging, onDragOver, onDragLeave }: any) => (
    <div 
      data-testid="dropzone" 
      data-dragging={isDragging}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
    >
      <input data-testid="file-input" type="file" onChange={onFileInput} />
    </div>
  )
}));

vi.mock('../../components/UploadFileList', () => ({
  default: ({ files }: { files: File[] }) => (
    <div data-testid="file-list">Files: {files.length}</div>
  )
}));

describe('UploadPage', () => {
  it('renders default state', () => {
    render(<UploadPage onUpload={() => {}} status="ready" />);
    expect(screen.getByText('Upload Documents')).toBeInTheDocument();
    expect(screen.getByText('Upload to Knowledge Base')).toBeDisabled();
    expect(screen.getByTestId('file-list')).toHaveTextContent('Files: 0');
  });

  it('handles drag events', () => {
    render(<UploadPage onUpload={() => {}} status="ready" />);
    const dropzone = screen.getByTestId('dropzone');
    
    fireEvent.dragOver(dropzone);
    expect(dropzone).toHaveAttribute('data-dragging', 'true');
    
    fireEvent.dragLeave(dropzone);
    expect(dropzone).toHaveAttribute('data-dragging', 'false');
  });

  it('handles valid file drop and upload', () => {
    const onUpload = vi.fn();
    render(<UploadPage onUpload={onUpload} status="ready" />);
    const dropzone = screen.getByTestId('dropzone');
    
    const file = new File([''], 'test.pdf', { type: 'application/pdf' });
    
    // Test Drop
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });
    
    expect(screen.getByTestId('file-list')).toHaveTextContent('Files: 1');
    
    const uploadBtn = screen.getByText('Upload to Knowledge Base');
    expect(uploadBtn).not.toBeDisabled();
    
    // Mock DataTransfer for jsdom
    class MockDataTransfer {
      items = { add: vi.fn() };
      files = [file];
    }
    global.DataTransfer = MockDataTransfer as any;
    
    fireEvent.click(uploadBtn);
    expect(onUpload).toHaveBeenCalled();
  });

  it('ignores invalid file extensions', () => {
    render(<UploadPage onUpload={() => {}} status="ready" />);
    const fileInput = screen.getByTestId('file-input');
    
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    expect(screen.getByTestId('file-list')).toHaveTextContent('Files: 0');
  });

  it('shows uploading status correctly', () => {
    render(<UploadPage onUpload={() => {}} status="Uploading documents..." />);
    expect(screen.getByText('Uploading...')).toBeInTheDocument();
  });
});
