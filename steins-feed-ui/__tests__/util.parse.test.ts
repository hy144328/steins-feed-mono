import {text_content, replace_word} from "@parse"

test("text_content() works", () => {
  const s = "Hello <em>world</em>!";
  const t = "Hello world!";
  expect(text_content(s)).toBe(t);
});

test("replace_word() works with simple replacement", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "Hello <em>world</em>!";
  const t = "H<span>ell</span>o <em>world</em>!";

  expect(replace_word(s, "ell", emphasize)).toBe(t);
});

test("replace_word() works with complex replacement", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "Hello <em>world</em>!";
  const t = "Hell<span>o </span><em><span>world</span></em><span>!</span>";

  expect(replace_word(s, "o world!", emphasize)).toBe(t);
});
