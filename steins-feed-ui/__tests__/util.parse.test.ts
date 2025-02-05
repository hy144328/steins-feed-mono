import {text_content, wrap_word} from "@parse"

test("text_content() works", () => {
  const s = "Hello <em>world</em>!";
  const t = "Hello world!";
  expect(text_content(s)).toBe(t);
});

test("wrap_word() works within a single element", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "Hello <em>world</em>!";
  const t = "H<span>ell</span>o <em>world</em>!";

  expect(wrap_word(s, "ell", emphasize)).toBe(t);
});

test("wrap_word() works across multiple elements", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "Hello <em>world</em>!";
  const t = "Hell<span>o </span><em><span>world</span></em><span>!</span>";

  expect(wrap_word(s, "o world!", emphasize)).toBe(t);
});
