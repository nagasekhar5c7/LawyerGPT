import { describe, it, expect } from "vitest";
import { AVAILABLE_MODELS, DEFAULT_MODEL } from "./index";

describe("AVAILABLE_MODELS", () => {
  it("has at least one model", () => {
    expect(AVAILABLE_MODELS.length).toBeGreaterThan(0);
  });

  it("each model has required fields", () => {
    for (const model of AVAILABLE_MODELS) {
      expect(model.id).toBeTruthy();
      expect(model.name).toBeTruthy();
      expect(model.provider).toBeTruthy();
    }
  });

  it("contains the default model", () => {
    const ids = AVAILABLE_MODELS.map((m) => m.id);
    expect(ids).toContain(DEFAULT_MODEL);
  });

  it("includes both OpenAI and Anthropic providers", () => {
    const providers = new Set(AVAILABLE_MODELS.map((m) => m.provider));
    expect(providers.has("OpenAI")).toBe(true);
    expect(providers.has("Anthropic")).toBe(true);
  });

  it("has no duplicate model IDs", () => {
    const ids = AVAILABLE_MODELS.map((m) => m.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

describe("DEFAULT_MODEL", () => {
  it("is gpt-5.5", () => {
    expect(DEFAULT_MODEL).toBe("gpt-5.5");
  });
});
