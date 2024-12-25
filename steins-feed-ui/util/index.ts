export function join_const<A, B>(a: Array<A>, sep: B): Array<A | B> {
  return a.flatMap((a_it, a_ct) => (a_ct > 0) ? [sep, a_it] : [a_it]);
}

export function join<A, B>(a: Array<A>, sep: (ct: number) => B): Array<A | B> {
  return a.flatMap((a_it, a_ct) => (a_ct > 0) ? [sep(a_ct), a_it] : [a_it]);
}
