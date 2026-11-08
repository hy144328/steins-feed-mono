export function join<A, B>(a: A[], sep: B): (A | B)[] {
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

export function ensure_array<T>(
  params?: T | T[],
): T[] {
  if (params === undefined) {
    return [];
  } else if (Array.isArray(params)) {
    return params;
  } else {
    return [params];
  }
}

export function ensure_primitive<T>(
  param: T | T[],
): T {
  if (Array.isArray(param)) {
    return param[0];
  } else {
    return param;
  }
}

export function group_by<T>(
  a: T[],
  compare_func: (a: T, b: T) => boolean,
): T[][] {
  const res: T[][] = [];
  let last: T | null = null;

  for (const a_it of a) {
    const is_old = last ? compare_func(a_it, last) : false;

    const res_it = is_old ? res[res.length - 1] : [];
    if (!is_old) {
      res.push(res_it);
    }

    res_it.push(a_it);
    last = a_it;
  }

  return res;
}

export function get_calendar_week(now: Date): number {
  const d = new Date(Date.UTC(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  ));

  const day = d.getUTCDay() || 7;

  d.setUTCDate(d.getUTCDate() + 4 - day);

  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));

  return Math.ceil(
    ((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7
  );
}

export function get_calendar_year(date: Date): number {
  const d = new Date(Date.UTC(
    date.getFullYear(),
    date.getMonth(),
    date.getDate()
  ));

  const day = d.getUTCDay() || 7;

  d.setUTCDate(d.getUTCDate() + 4 - day);

  return d.getUTCFullYear();
}
