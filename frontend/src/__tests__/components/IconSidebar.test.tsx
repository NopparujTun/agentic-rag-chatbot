import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import IconSidebar from "../../components/IconSidebar";

describe("IconSidebar", () => {
  it("renders and calls callbacks", () => {
    const logoClick = vi.fn();
    const homeClick = vi.fn();
    const docClick = vi.fn();

    render(
      <IconSidebar
        onLogoClick={logoClick}
        onHomeClick={homeClick}
        onDocumentClick={docClick}
        activeView="home"
      />
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(3);

    fireEvent.click(buttons[0]);
    expect(logoClick).toHaveBeenCalled();

    fireEvent.click(buttons[1]);
    expect(homeClick).toHaveBeenCalled();

    fireEvent.click(buttons[2]);
    expect(docClick).toHaveBeenCalled();
  });

  it("highlights correct view", () => {
    const { rerender } = render(<IconSidebar activeView="upload" />);
    const buttons = screen.getAllByRole("button");
    expect(buttons[2]).toHaveClass("bg-indigo-100"); // Document button
    expect(buttons[1]).toHaveClass("bg-transparent"); // Home button

    rerender(<IconSidebar activeView="chat" />);
    expect(buttons[1]).toHaveClass("bg-indigo-100"); // Home/Chat button
  });
});
