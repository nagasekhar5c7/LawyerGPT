import { test, expect } from "@playwright/test";

test.describe("LawyerGPT - Page Load", () => {
  test("should load the app with correct title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("LawyerGPT");
  });

  test("should display the header with app name", async ({ page }) => {
    await page.goto("/");
    const header = page.locator("h1");
    await expect(header).toHaveText("LawyerGPT");
  });

  test("should display the Legal AI Assistant badge", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Legal AI Assistant")).toBeVisible();
  });

  test("should show the welcome screen when no conversation is active", async ({
    page,
  }) => {
    await page.goto("/");
    await expect(page.getByTestId("empty-chat")).toBeVisible();
    await expect(page.getByText("Welcome to LawyerGPT")).toBeVisible();
  });
});

test.describe("LawyerGPT - Sidebar", () => {
  test("should display sidebar with New Chat button", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("sidebar")).toBeVisible();
    await expect(page.getByTestId("new-chat-button")).toBeVisible();
    await expect(page.getByTestId("new-chat-button")).toHaveText("New Chat");
  });

  test("should show empty conversation list initially", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("No conversations yet")).toBeVisible();
  });

  test("should create a new conversation when clicking New Chat", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("new-chat-button").click();
    await expect(page.getByTestId("conversation-list")).toBeVisible();
    await expect(page.getByTestId("conversation-list").getByText("New Chat")).toBeVisible();
  });
});

test.describe("LawyerGPT - Chat Input", () => {
  test("should display the chat input area", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("chat-input-container")).toBeVisible();
    await expect(page.getByTestId("chat-textarea")).toBeVisible();
    await expect(page.getByTestId("send-button")).toBeVisible();
    await expect(page.getByTestId("upload-button")).toBeVisible();
  });

  test("should have placeholder text in textarea", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("chat-textarea")).toHaveAttribute(
      "placeholder",
      "Ask a legal question..."
    );
  });

  test("send button should be disabled when input is empty", async ({
    page,
  }) => {
    await page.goto("/");
    await expect(page.getByTestId("send-button")).toBeDisabled();
  });

  test("send button should be enabled when input has text", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("chat-textarea").fill("What is contract law?");
    await expect(page.getByTestId("send-button")).toBeEnabled();
  });

  test("should show disclaimer text", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByText("LawyerGPT can make mistakes")
    ).toBeVisible();
  });
});

test.describe("LawyerGPT - Chat Flow", () => {
  test("should send a message and create a conversation", async ({ page }) => {
    await page.goto("/");

    await page.getByTestId("chat-textarea").fill("What is tort law?");
    await page.getByTestId("send-button").click();

    // User message should appear
    await expect(page.getByTestId("message-user").first()).toBeVisible();
    await expect(page.getByTestId("chat-area").getByText("What is tort law?")).toBeVisible();

    // Welcome screen should be gone
    await expect(page.getByTestId("empty-chat")).not.toBeVisible();

    // Chat area should now be visible
    await expect(page.getByTestId("chat-area")).toBeVisible();
  });

  test("should auto-create conversation on first message", async ({
    page,
  }) => {
    await page.goto("/");

    await page.getByTestId("chat-textarea").fill("Define negligence");
    await page.getByTestId("send-button").click();

    // Conversation should appear in sidebar
    await expect(page.getByTestId("conversation-list")).toBeVisible();
  });

  test("should clear input after sending", async ({ page }) => {
    await page.goto("/");

    await page.getByTestId("chat-textarea").fill("Test question");
    await page.getByTestId("send-button").click();

    await expect(page.getByTestId("chat-textarea")).toHaveValue("");
  });

  test("should send message on Enter key", async ({ page }) => {
    await page.goto("/");

    await page.getByTestId("chat-textarea").fill("Enter key test");
    await page.getByTestId("chat-textarea").press("Enter");

    await expect(page.getByTestId("chat-area").getByText("Enter key test")).toBeVisible();
    await expect(page.getByTestId("chat-textarea")).toHaveValue("");
  });

  test("should not send on Shift+Enter (allows newline)", async ({ page }) => {
    await page.goto("/");

    await page.getByTestId("chat-textarea").fill("Line one");
    await page.getByTestId("chat-textarea").press("Shift+Enter");

    // Message should NOT be sent — textarea should still have content
    await expect(page.getByTestId("chat-textarea")).not.toHaveValue("");
  });
});

test.describe("LawyerGPT - Conversation Management", () => {
  test("should create multiple conversations", async ({ page }) => {
    await page.goto("/");

    // Create first conversation via message
    await page.getByTestId("chat-textarea").fill("First question");
    await page.getByTestId("send-button").click();
    await expect(page.getByTestId("conversation-list")).toBeVisible();

    // Create second conversation via New Chat button
    await page.getByTestId("new-chat-button").click();

    // Should show welcome screen for new chat
    await expect(page.getByTestId("empty-chat")).toBeVisible();
  });

  test("should delete a conversation", async ({ page }) => {
    await page.goto("/");

    // Create conversation
    await page.getByTestId("new-chat-button").click();
    await expect(page.getByTestId("conversation-list")).toBeVisible();

    // Hover to reveal delete button and click it
    const conversationItem = page.getByTestId("conversation-list").locator("div").first();
    await conversationItem.hover();
    const deleteButton = conversationItem.locator('button[aria-label="Delete conversation"]');
    await deleteButton.click();

    // Conversation should be gone
    await expect(page.getByText("No conversations yet")).toBeVisible();
  });
});

test.describe("LawyerGPT - File Upload", () => {
  test("should have a file upload button", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("upload-button")).toBeVisible();
  });

  test("should have a hidden file input that accepts PDFs", async ({
    page,
  }) => {
    await page.goto("/");
    const fileInput = page.getByTestId("file-input");
    await expect(fileInput).toHaveAttribute("accept", ".pdf");
  });
});

test.describe("LawyerGPT - Model Selector", () => {
  test("should display model selector in header with default model", async ({
    page,
  }) => {
    await page.goto("/");
    await expect(page.getByTestId("model-selector")).toBeVisible();
    await expect(page.getByTestId("selected-model-name")).toHaveText("GPT-5.5");
  });

  test("should open dropdown when clicked", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("model-selector-button").click();
    await expect(page.getByTestId("model-dropdown")).toBeVisible();
  });

  test("should show all available models in dropdown", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("model-selector-button").click();
    await expect(page.getByTestId("model-option-gpt-5.5")).toBeVisible();
    await expect(page.getByTestId("model-option-gpt-4o")).toBeVisible();
    await expect(page.getByTestId("model-option-gpt-4o-mini")).toBeVisible();
    await expect(page.getByTestId("model-option-claude-sonnet-4-6")).toBeVisible();
    await expect(page.getByTestId("model-option-claude-haiku-4-5")).toBeVisible();
  });

  test("should change selected model when an option is clicked", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("model-selector-button").click();
    await page.getByTestId("model-option-gpt-4o").click();

    // Dropdown should close
    await expect(page.getByTestId("model-dropdown")).not.toBeVisible();

    // Selected model should update
    await expect(page.getByTestId("selected-model-name")).toHaveText("GPT-4o");
  });

  test("should close dropdown when clicking outside", async ({ page }) => {
    await page.goto("/");
    await page.getByTestId("model-selector-button").click();
    await expect(page.getByTestId("model-dropdown")).toBeVisible();

    // Click outside the dropdown
    await page.locator("h1").click();
    await expect(page.getByTestId("model-dropdown")).not.toBeVisible();
  });

  test("should show checkmark on currently selected model", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByTestId("model-selector-button").click();

    // Default GPT-5.5 should have blue highlight
    const defaultOption = page.getByTestId("model-option-gpt-5.5");
    await expect(defaultOption).toHaveClass(/bg-blue-50/);
  });
});

test.describe("LawyerGPT - Responsive Layout", () => {
  test("should show sidebar on desktop viewport", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/");
    await expect(page.getByTestId("sidebar")).toBeVisible();
  });

  test("should hide sidebar on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");
    await expect(page.getByTestId("sidebar")).not.toBeVisible();
  });
});
