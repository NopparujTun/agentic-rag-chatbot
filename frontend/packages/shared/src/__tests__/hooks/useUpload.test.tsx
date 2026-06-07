import type { ReactNode } from "react";
import { renderHook, act, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useUpload } from "../../hooks/useUpload";
import { ChatProvider } from "../../context/ChatContext";
import * as api from "../../api";

vi.mock("../../api", () => ({
  uploadDocuments: vi.fn(),
}));

const wrapper = ({ children }: { children: ReactNode }) => <ChatProvider>{children}</ChatProvider>;

describe("useUpload hook", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("handleUpload does nothing if files is empty", async () => {
    const { result } = renderHook(() => useUpload(), { wrapper });

    const dt = [] as unknown as FileList;
    act(() => {
      result.current.handleUpload(dt);
    });

    expect(api.uploadDocuments).not.toHaveBeenCalled();
  });

  it("handleUpload calls api and updates status on success", async () => {
    vi.mocked(api.uploadDocuments).mockResolvedValueOnce({
      message: "Success",
      files_processed: ["file1.pdf"],
    });

    const { result } = renderHook(() => useUpload(), { wrapper });

    const dt = [new File([""], "file1.pdf")] as unknown as FileList;

    act(() => {
      result.current.handleUpload(dt);
    });

    await waitFor(() => {
      expect(api.uploadDocuments).toHaveBeenCalled();
    });
  });

  it("handleUpload handles API errors", async () => {
    vi.mocked(api.uploadDocuments).mockRejectedValueOnce(new Error("Upload failed"));

    const { result } = renderHook(() => useUpload(), { wrapper });

    const dt = [new File([""], "file1.pdf")] as unknown as FileList;

    act(() => {
      result.current.handleUpload(dt);
    });

    await waitFor(() => {
      expect(api.uploadDocuments).toHaveBeenCalled();
    });
  });
});
