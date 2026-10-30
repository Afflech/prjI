import { expect, test } from "playwright/test";

test("notebook source chat citation and evidence flow works", async ({ page }) => {
  const notebookTitle = `E2E Notebook ${Date.now()}`;
  const sourceTitle = "AVL - E2E.md";
  const sourceText =
    "AVL trees rebalance by applying single or double rotations after insertions. " +
    "The rotations keep the tree height logarithmic.";

  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Hỏi đáp tài liệu" }),
  ).toBeVisible();

  await page.getByRole("textbox", { name: "Tên notebook mới" }).fill(notebookTitle);
  await page.getByRole("button", { name: "Tạo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: notebookTitle, exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Câu hỏi" })).toBeEnabled();

  await page.getByText("Dán văn bản thay thế", { exact: true }).click();
  await page.getByRole("textbox", { name: "Tên nguồn" }).fill(sourceTitle);
  await page.getByRole("textbox", { name: "Nội dung nguồn" }).fill(sourceText);
  await page.getByRole("button", { name: "Thêm nguồn", exact: true }).click();
  await expect(page.getByText(sourceTitle, { exact: true })).toBeVisible();

  await page
    .getByRole("textbox", { name: "Câu hỏi" })
    .fill("How do AVL trees rebalance?");
  await page.getByRole("button", { name: "Gửi", exact: true }).click();
  await expect(
    page.getByText("Retrieval preview answer based on cited source chunks:", {
      exact: false,
    }),
  ).toBeVisible();

  const citation = page.getByRole("button", { name: /^\[1\] đoạn \d+$/ });
  await expect(citation).toBeVisible();
  await citation.click();

  const evidencePanel = page.getByRole("complementary", { name: "Bằng chứng" });
  await expect(
    evidencePanel.getByRole("heading", { name: /^AVL - E2E\.md · đoạn \d+$/ }),
  ).toBeVisible();
  await expect(evidencePanel.getByText(sourceText, { exact: false })).toBeVisible();

  await page.getByRole("checkbox", { name: `Tắt nguồn ${sourceTitle}` }).click();
  await expect(page.getByText("0/1 bật", { exact: true })).toBeVisible();
  await page
    .getByRole("textbox", { name: "Câu hỏi" })
    .fill("How do AVL trees rebalance?");
  await page.getByRole("button", { name: "Gửi", exact: true }).click();
  await expect(
    page.getByText("Không tìm thấy trích dẫn.", { exact: false }),
  ).toBeVisible();
});

test("Markdown uploads can be queried from a notebook", async ({ page }) => {
  const notebookTitle = `E2E Upload Notebook ${Date.now()}`;
  const sourceTitle = "AVL-upload-e2e.md";

  await page.goto("/");
  await page.getByRole("textbox", { name: "Tên notebook mới" }).fill(notebookTitle);
  await page.getByRole("button", { name: "Tạo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: notebookTitle, exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Câu hỏi" })).toBeEnabled();

  await page.getByLabel("Tải tệp nguồn lên").setInputFiles({
    name: sourceTitle,
    mimeType: "text/markdown",
    buffer: Buffer.from(
      "Red-black trees maintain balance with recoloring and rotations after updates.",
    ),
  });
  await expect(page.getByText(sourceTitle, { exact: true })).toBeVisible();

  await page.getByRole("textbox", { name: "Câu hỏi" }).fill("How do red-black trees balance?");
  await page.getByRole("button", { name: "Gửi", exact: true }).click();
  await expect(
    page.getByText("Retrieval preview answer based on cited source chunks:", {
      exact: false,
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /^\[1\] đoạn \d+$/ }),
  ).toBeVisible();
});
