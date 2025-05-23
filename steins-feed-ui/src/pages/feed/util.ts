import { Tag } from "@/client"

export function contains_tag(tags: Tag[], tag_name: string): boolean {
  return tags.some(tag_it => (tag_it.name === tag_name))
}

export function insert_tag(tags: Tag[], tag: Tag): Tag[] {
  const res = Array.from(tags);
  res.push(tag);
  return sort_tags(res);
}

export function insert_by_mirror_tag<T>(ts: T[], tags: Tag[], tag: Tag, val: T): T[] {
  const res = Array.from(Array(ts.length).keys()).map(ct => {
    return {t: ts[ct], tag: tags[ct]};
  });
  res.push({t: val, tag: tag});
  return res.sort((a, b) => a.tag.name.localeCompare(b.tag.name)).map(x => x.t);
}

export function remove_tag(tags: Tag[], tag: Tag): Tag[] {
  return tags.filter(tag_it => (tag_it.name !== tag.name));
}

export function remove_by_mirror_tag<T>(ts: T[], tags: Tag[], tag: Tag): T[] {
  return ts.filter((_, t_ct) => (tags[t_ct].name !== tag.name));
}

export function replace_tag(tags: Tag[], tag: Tag): Tag[] {
  return tags.map(tag_it => (tag_it.name === tag.name) ? tag : tag_it);
}

export function replace_by_mirror_tag<T>(ts: T[], tags: Tag[], tag: Tag, val: T): T[] {
  return ts.map((t_it, t_ct) => (tags[t_ct].name === tag.name) ? val : t_it);
}

export function sort_tags(tags: Tag[]): Tag[] {
  return tags.sort(compare_tags);
}

export function compare_tags(a: Tag, b: Tag): number {
  return a.name.localeCompare(b.name);
}
