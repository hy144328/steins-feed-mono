"use server"

import { Tag } from "@client"

export async function submit_tag(tag_name: string): Promise<Tag> {
  console.log("whatever");
  return {
    id: -1,
    name: tag_name,
  }
}
