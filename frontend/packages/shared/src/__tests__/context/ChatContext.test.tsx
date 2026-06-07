import { renderHook } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { useChatContext } from "../../context/ChatContext";

describe("ChatContext", () => {
  it("throws error when used outside of provider", () => {
    // Suppress console.error for the expected throw
    const originalError = console.error;
    console.error = () => {};

    expect(() => {
      renderHook(() => useChatContext());
    }).toThrow("useChatContext must be used within a ChatProvider");

    console.error = originalError;
  });
});
