import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import MessageMetadata from "../../components/MessageMetadata";
import type { ChatResponse } from "@mfa/shared";

describe("MessageMetadata", () => {
  it("renders nothing if no metadata", () => {
    const { container } = render(<MessageMetadata metadata={undefined as any} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders sources correctly", () => {
    const meta: ChatResponse = {
      answer: "",
      sources: [
        { content: "source 1 text", metadata: { source: "file1.pdf" } },
        { content: "source 2 text", metadata: { source: "file1.pdf" } },
        { content: "source 3 text", metadata: { source: "file2.txt" } },
      ],
      steps: [],
    };
    render(<MessageMetadata metadata={meta} />);

    // Check toggle sources
    const btn = screen.getByText(/Sources/);
    expect(btn).toBeInTheDocument();

    fireEvent.click(btn);
    // Use a function to find the text since it's mixed with emoji
    expect(
      screen.getAllByText((content, element) => {
        return (
          element?.textContent === "📄 file1.pdf" || element?.textContent?.includes("file1.pdf")
        );
      }).length
    ).toBeGreaterThan(0);
  });

  it("renders reasoning steps", () => {
    const meta: ChatResponse = {
      answer: "",
      sources: [],
      steps: [{ tool: "search", tool_input: { q: "test" }, observation: "found" }],
    };
    render(<MessageMetadata metadata={meta} />);

    const btn = screen.getByText(/Thought Process/);
    expect(btn).toBeInTheDocument();

    fireEvent.click(btn);
    expect(screen.getByText(/search/)).toBeInTheDocument();
    expect(screen.getByText(/found/)).toBeInTheDocument();
  });
});
