import { Language } from "@client"

export interface NavigationSearchParams {
  now: Date,
  languages: Language[],
  tags: number[],
};

export function toURLSearchParams({
  now,
  languages,
  tags,
}: NavigationSearchParams): URLSearchParams {
  const res = new URLSearchParams();

  res.append("now", now.toISOString());
  languages.forEach(lang_it => res.append("languages", lang_it));
  tags.forEach(tag_it => res.append("tags", tag_it.toString()));

  return res;
}
