import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Sidebar from "./Sidebar";
import type { Conversation } from "../../types";

const mockConversations: Conversation[] = [
  {
    id: "conv-1",
    title: "Contract Law Discussion",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T01:00:00Z",
  },
  {
    id: "conv-2",
    title: "Tort Law Q&A",
    created_at: "2026-01-02T00:00:00Z",
    updated_at: "2026-01-02T01:00:00Z",
  },
];

describe("Sidebar", () => {
  it("renders the sidebar", () => {
    render(
      <Sidebar
        conversations={[]}
        activeId={null}
        onNewChat={vi.fn()}
        onSelect={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByTestId("sidebar")).toBeInTheDocument();
  });

  it("renders LawyerGPT branding", () => {
    render(
      <Sidebar
        conversations={[]}
        activeId={null}
        onNewChat={vi.fn()}
        onSelect={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText("LawyerGPT")).toBeInTheDocument();
  });

  it("renders conversation titles", () => {
    render(
      <Sidebar
        conversations={mockConversations}
        activeId={null}
        onNewChat={vi.fn()}
        onSelect={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText("Contract Law Discussion")).toBeInTheDocument();
    expect(screen.getByText("Tort Law Q&A")).toBeInTheDocument();
  });
});
