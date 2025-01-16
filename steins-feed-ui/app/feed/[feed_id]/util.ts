import { Tag } from "@client"

export function contains_tag(tags: Tag[], tag_name: string): boolean {
  return tags.some(tag_it => (tag_it.name === tag_name))
}
