export function similar_edit(
  s: string,
  t: string,
  thresh: number,
  i: number = 0,
  j: number = 0,
): boolean {
  if (thresh < 0) {
    return false;
  }

  if (i === s.length) {
    return t.length - j <= thresh;
  }

  if (j === t.length) {
    return s.length - i <= thresh;
  }

  if (s[i] === t[j]) {
    return similar_edit(s, t, thresh, i+1, j+1);
  }

  return similar_edit(s, t, thresh-1, i+1, j+1) || similar_edit(s, t, thresh-1, i+1, j) || similar_edit(s, t, thresh-1, i, j+1);
}

export function similar_prefix(
  s: string,
  t: string,
  thresh: number,
): boolean {
  if (s.length < thresh) {
    return false;
  }

  if (t.length < thresh) {
    return false;
  }

  return s.slice(0, thresh) === t.slice(0, thresh);
}
