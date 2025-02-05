import {text_content, wrap_word, wrap_words} from "@parse"

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

test("wrap_word() is able to ignore case", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "HELLO <em>WORLD</em>!";
  const t = "H<span>ELL</span>O <em>WORLD</em>!";

  expect(wrap_word(s, "ell", emphasize, true)).toBe(t);
});

test("wrap_word() is able to respect word boundaries", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "Hello <em>world</em>!";
  const t = "Hello <em>world</em>!";

  expect(wrap_word(s, "ell", emphasize, true, true)).toBe(t);
});

test("wrap_words() handles multiple words", () => {
  function emphasize(word: string): HTMLSpanElement {
    const res = document.createElement("span");
    res.textContent = word;
    return res;
  }

  const s = "1 2  3   4    5";
  const t = "1 <span>2</span>  <span>3</span>   <span>4</span>    5";

  expect(wrap_words(s, ["2", "3", "4"], emphasize)).toBe(t);
});
