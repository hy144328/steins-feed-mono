import { join } from "@util"

test("join interleaves string array with comma", () => {
  expect(join(["a", "b"], ",")).toEqual(["a", ",", "b"]);
});
