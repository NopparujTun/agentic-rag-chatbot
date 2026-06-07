import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import ChatInput from "../../components/ChatInput";

vi.mock("../../components/ui/input-bar", () => ({
  InputBar: ({ onSend, onAttach, status }: any) => (
    <div data-testid="input-bar" data-status={status}>
      <button
        data-testid="send-btn"
        onClick={() => onSend({ role: "user", content: "test message" })}
      >
        Send
      </button>
      <button data-testid="attach-btn" onClick={onAttach}>
        Attach
      </button>
    </div>
  ),
}));

describe("ChatInput", () => {
  it("renders correctly", () => {
    render(<ChatInput isSending={false} onSendMessage={() => {}} onUploadDocuments={() => {}} />);
    expect(screen.getByTestId("input-bar")).toBeInTheDocument();
    expect(screen.getByTestId("input-bar")).toHaveAttribute("data-status", "ready");
  });

  it("shows streaming status when isSending is true", () => {
    render(<ChatInput isSending={true} onSendMessage={() => {}} onUploadDocuments={() => {}} />);
    expect(screen.getByTestId("input-bar")).toHaveAttribute("data-status", "streaming");
  });

  it("calls onSendMessage when InputBar triggers onSend", () => {
    const onSendMock = vi.fn();
    render(<ChatInput isSending={false} onSendMessage={onSendMock} onUploadDocuments={() => {}} />);

    fireEvent.click(screen.getByTestId("send-btn"));
    expect(onSendMock).toHaveBeenCalledWith("test message");
  });

  it("triggers file input click when onAttach is called", () => {
    render(<ChatInput isSending={false} onSendMessage={() => {}} onUploadDocuments={() => {}} />);

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const clickSpy = vi.spyOn(fileInput, "click");

    fireEvent.click(screen.getByTestId("attach-btn"));
    expect(clickSpy).toHaveBeenCalled();
  });

  it("calls onUploadDocuments when files are selected", () => {
    const onUploadMock = vi.fn();
    render(
      <ChatInput isSending={false} onSendMessage={() => {}} onUploadDocuments={onUploadMock} />
    );

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File([""], "test.pdf", { type: "application/pdf" });

    // create a fake FileList
    Object.defineProperty(fileInput, "files", {
      value: [file],
    });

    fireEvent.change(fileInput);

    expect(onUploadMock).toHaveBeenCalled();
  });
});
