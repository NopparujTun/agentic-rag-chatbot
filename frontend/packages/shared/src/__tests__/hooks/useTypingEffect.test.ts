import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useTypingEffect } from "../../hooks/useTypingEffect";

describe("useTypingEffect hook", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("types out text over time", () => {
    const { result } = renderHook(() => useTypingEffect("hello", true, 10, 10));

    // The effect sets timeout 0 immediately to start typing
    act(() => {
      vi.runOnlyPendingTimers(); // this runs the 0ms timeout that sets isTyping = true
    });

    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current.displayedText).toBe("hello");
    expect(result.current.isTyping).toBe(false);
  });

  it("does not type if disabled", () => {
    const { result } = renderHook(() => useTypingEffect("hello", false));

    act(() => {
      vi.runAllTimers();
    });

    expect(result.current.displayedText).toBe("hello");
    expect(result.current.isTyping).toBe(false);
  });
});
