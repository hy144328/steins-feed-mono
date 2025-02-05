import {
  join,
  left_pad,
} from "@util"

test("join() interleaves string array with comma", () => {
  expect(join(["a", "b"], ",")).toEqual(["a", ",", "b"]);
});

test("left_pad() pads zeros until full", () => {
  expect(left_pad(5, 4)).toBe("0005");
});

test("left_pad() pads zeros if necessary", () => {
  expect(left_pad(5000, 4)).toBe("5000");
});
