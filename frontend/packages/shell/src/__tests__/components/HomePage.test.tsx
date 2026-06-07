import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import HomePage from "../../components/HomePage";

vi.mock("@mfa/shared", () => ({
  HeroSection: () => <div data-testid="hero-section" />,
  ChatInput: ({ isSending, onSendMessage, onUploadDocuments }: { isSending: boolean; onSendMessage: (msg: string) => void; onUploadDocuments: (files: unknown[]) => void }) => (
    <div data-testid="chat-input" data-sending={isSending}>
      <button data-testid="send-btn" onClick={() => onSendMessage("test")}>
        Send
      </button>
      <button data-testid="upload-btn" onClick={() => onUploadDocuments([])}>
        Upload
      </button>
    </div>
  ),
}));

describe("HomePage", () => {
  it("renders correctly", () => {
    const onSend = vi.fn();
    const onUpload = vi.fn();

    render(
      <HomePage
        isSending={true}
        status="test status"
        onSendMessage={onSend}
        onUploadDocuments={onUpload}
      />
    );

    expect(screen.getByTestId("hero-section")).toBeInTheDocument();
    expect(screen.getByText("test status")).toBeInTheDocument();

    const input = screen.getByTestId("chat-input");
    expect(input).toHaveAttribute("data-sending", "true");

    fireEvent.click(screen.getByTestId("send-btn"));
    expect(onSend).toHaveBeenCalledWith("test");

    fireEvent.click(screen.getByTestId("upload-btn"));
    expect(onUpload).toHaveBeenCalled();
  });
});
