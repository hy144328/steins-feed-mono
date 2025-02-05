import {
  ensure_array,
  ensure_primitive,
  format_datetime,
  group_by,
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

test("format_datetime() has fixed width", () => {
  expect(format_datetime(new Date(Date.UTC(2025, 2, 1, 12, 34, 56)))).toBe("2025-03-01 12:34:56 GMT");
});

test("ensure_array() is empty when undefined", () => {
  expect(ensure_array(undefined)).toEqual([]);
});

test("ensure_array() wraps when single element", () => {
  expect(ensure_array(1)).toEqual([1]);
});

test("ensure_array() passes when multiple elements", () => {
  expect(ensure_array([1])).toEqual([1]);
});

test("ensure_primitive() passes when single element", () => {
  expect(ensure_primitive(1)).toBe(1);
});

test("ensure_primitive() selects when multiple elements", () => {
  expect(ensure_primitive([0, 1])).toBe(0);
});

test("group_by() only groups consecutive elements", () => {
  const data = [
    {a: 1, b: 1},
    {a: 2, b: 1},
    {a: 3, b: 2},
    {a: 4, b: 2},
    {a: 5, b: 2},
    {a: 6, b: 1},
  ];
  const res = [
    [
      {a: 1, b: 1},
      {a: 2, b: 1},
    ],
    [
      {a: 3, b: 2},
      {a: 4, b: 2},
      {a: 5, b: 2},
    ],
    [
      {a: 6, b: 1},
    ],
  ];
  expect(group_by(data, (x, y) => x.b === y.b)).toEqual(res);
});
