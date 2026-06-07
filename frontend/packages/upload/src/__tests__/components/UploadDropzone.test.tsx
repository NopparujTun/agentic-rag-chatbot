import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import UploadDropzone from "../../components/UploadDropzone";

describe("UploadDropzone", () => {
  it("renders correctly", () => {
    render(
      <UploadDropzone
        isDragging={false}
        onDragOver={() => {}}
        onDragLeave={() => {}}
        onDrop={() => {}}
        onFileInput={() => {}}
      />
    );
    expect(screen.getByText(/Click to upload/)).toBeInTheDocument();
  });

  it("calls file input when clicked", () => {
    const onFileInput = vi.fn();
    render(
      <UploadDropzone
        isDragging={false}
        onDragOver={() => {}}
        onDragLeave={() => {}}
        onDrop={() => {}}
        onFileInput={onFileInput}
      />
    );

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [] } });
    expect(onFileInput).toHaveBeenCalled();
  });

  it("renders correctly while dragging", () => {
    const { container } = render(
      <UploadDropzone
        isDragging={true}
        onDragOver={() => {}}
        onDragLeave={() => {}}
        onDrop={() => {}}
        onFileInput={() => {}}
      />
    );
    // Check if dragging class is applied
    expect(container.firstChild).toHaveClass("border-indigo-500");
  });
});
