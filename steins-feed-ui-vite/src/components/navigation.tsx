import { Language, Tag } from "@/client"
import { languagesFeedsLanguagesGet, tagsFeedsTagsGet } from "@/client"

import { authenticate } from "@/auth"
import { NavigationSearchParams } from "@/util"

import SideNav from "./sidenav"
import TopNav from "./topnav"

export default async function Navigation({
  now,
  languages,
  tags,
  wall_mode,
  contentServed = false,
}: NavigationSearchParams & {
  contentServed?: boolean,
}) {
  const all_languages = await getAllLanguages();
  const all_tags = await getAllTags();

  return (
<>
<TopNav
  now={ now }
  languages={ languages }
  tags={ tags }
  wall_mode={ wall_mode }
  contentServed={ contentServed }
/>
<SideNav
  now={ now }
  languages={ languages }
  tags={ tags }
  wall_mode={ wall_mode }
  all_languages={ all_languages }
  all_tags={ all_tags }
/>
</>
  );
}

async function getAllLanguages(): Promise<Language[]> {
  await authenticate();

  const resp = await languagesFeedsLanguagesGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}

async function getAllTags(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}
