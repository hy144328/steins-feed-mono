export function join<A, B>(a: Array<A>, sep: B): Array<A | B> {
  return a.flatMap((a_it, a_ct) => (a_ct > 0) ? [sep, a_it] : [a_it]);
}

export function left_pad(x: number, n: number): string {
  return String(x).padStart(n, "0");
}

export const day_of_week = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];
export const day_of_week_short = day_of_week.map(day_it => day_it.slice(0, 3));

export const month_of_year = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];
export const month_of_year_short = month_of_year.map(day_it => day_it.slice(0, 3));

export function format_date(now: Date): string {
  const year = now.getUTCFullYear();
  const month = now.getUTCMonth() + 1;
  const day = now.getUTCDate();

  return `${left_pad(year, 4)}-${left_pad(month, 2)}-${left_pad(day, 2)}`;
}

export function format_time(now: Date): string {
  const hour = now.getUTCHours();
  const minute = now.getUTCMinutes();
  const second = now.getUTCSeconds();

  return `${left_pad(hour, 2)}:${left_pad(minute, 2)}:${left_pad(second, 2)}`;
}

export function format_datetime(now: Date): string {
  return `${format_date(now)} ${format_time(now)} GMT`;
}
