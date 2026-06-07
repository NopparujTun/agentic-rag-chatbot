import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import MainContent from "../../components/MainContent";
import type { ChatMessage } from "@mfa/shared";

vi.mock("@mfa/shared", () => ({
  HeroSection: () => <div data-testid="hero-section" />,
  ChatInput: () => <div data-testid="chat-input" />,
}));

vi.mock("../../components/MessageItem", () => ({
  default: ({ message, isLatestAssistantMessage, isThinking }: any) => (
    <div
      data-testid="message-item"
      data-role={message.role}
      data-latest={isLatestAssistantMessage}
      data-thinking={isThinking}
    >
      {message.content}
    </div>
  ),
}));

describe("MainContent", () => {
  it("renders empty state", () => {
    render(
      <MainContent
        messages={[]}
        isSending={false}
        status="ready"
        onSendMessage={() => {}}
        onUploadDocuments={() => {}}
      />
    );

    expect(screen.getByTestId("hero-section")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toBeInTheDocument();
    expect(screen.queryByTestId("message-item")).not.toBeInTheDocument();
  });

  it("renders messages and hides hero section", () => {
    const msgs: ChatMessage[] = [
      { id: 1, role: "user", content: "hello" },
      { id: 2, role: "assistant", content: "hi" },
    ];

    render(
      <MainContent
        messages={msgs}
        isSending={false}
        status="ready"
        onSendMessage={() => {}}
        onUploadDocuments={() => {}}
      />
    );

    expect(screen.queryByTestId("hero-section")).not.toBeInTheDocument();
    const messageItems = screen.getAllByTestId("message-item");
    expect(messageItems).toHaveLength(2);
    expect(messageItems[1]).toHaveAttribute("data-latest", "true");
  });

  it("shows thinking indicator message when sending", () => {
    const msgs: ChatMessage[] = [{ id: 1, role: "user", content: "hello" }];

    render(
      <MainContent
        messages={msgs}
        isSending={true}
        status="ready"
        onSendMessage={() => {}}
        onUploadDocuments={() => {}}
      />
    );

    const messageItems = screen.getAllByTestId("message-item");
    expect(messageItems).toHaveLength(2);
    expect(messageItems[1]).toHaveAttribute("data-thinking", "true");
  });
});
