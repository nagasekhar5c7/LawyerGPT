import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ModelSelector from "./ModelSelector";
import { AVAILABLE_MODELS } from "../../types";

describe("ModelSelector", () => {
  it("renders the selected model name", () => {
    render(
      <ModelSelector selectedModel="gpt-5.5" onModelChange={vi.fn()} />
    );
    expect(screen.getByTestId("selected-model-name")).toHaveTextContent(
      "GPT-5.5"
    );
  });

  it("opens dropdown on click", () => {
    render(
      <ModelSelector selectedModel="gpt-5.5" onModelChange={vi.fn()} />
    );
    expect(screen.queryByTestId("model-dropdown")).not.toBeInTheDocument();

    fireEvent.click(screen.getByTestId("model-selector-button"));
    expect(screen.getByTestId("model-dropdown")).toBeInTheDocument();
  });

  it("shows all available models in dropdown", () => {
    render(
      <ModelSelector selectedModel="gpt-5.5" onModelChange={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId("model-selector-button"));

    for (const model of AVAILABLE_MODELS) {
      expect(screen.getByTestId(`model-option-${model.id}`)).toBeInTheDocument();
    }
  });

  it("calls onModelChange when a model is selected", () => {
    const onChange = vi.fn();
    render(<ModelSelector selectedModel="gpt-5.5" onModelChange={onChange} />);

    fireEvent.click(screen.getByTestId("model-selector-button"));
    fireEvent.click(screen.getByTestId("model-option-gpt-4o"));

    expect(onChange).toHaveBeenCalledWith("gpt-4o");
  });

  it("closes dropdown after selection", () => {
    render(
      <ModelSelector selectedModel="gpt-5.5" onModelChange={vi.fn()} />
    );
    fireEvent.click(screen.getByTestId("model-selector-button"));
    expect(screen.getByTestId("model-dropdown")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("model-option-gpt-4o"));
    expect(screen.queryByTestId("model-dropdown")).not.toBeInTheDocument();
  });
});
