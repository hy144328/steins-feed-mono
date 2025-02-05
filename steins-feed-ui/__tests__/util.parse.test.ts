import {text_content} from "@parse"

test("text_content()", () => {
  const s = "Hello <em>world</em>!";
  const t = "Hello world!";
  expect(text_content(s)).toBe(t);
});
