import { Language, WallMode } from "@/client"

export type WindowMode = 'Day' | 'Week' | 'Month';

export interface NavigationSearchParams {
  now: Date,
  languages: Language[],
  tags: number[],
  wall_mode?: WallMode,
  window_mode?: WindowMode,
};

export function toURLSearchParams({
  now,
  languages,
  tags,
  wall_mode,
  window_mode,
}: NavigationSearchParams): URLSearchParams {
  const res = new URLSearchParams();

  res.append("now", now.toISOString());
  languages.forEach(lang_it => res.append("languages", lang_it));
  tags.forEach(tag_it => res.append("tags", tag_it.toString()));
  if (wall_mode) {
    res.append("wall_mode", wall_mode);
  }
  if (window_mode) {
    res.append("window_mode", window_mode);
  }

  return res;
}
