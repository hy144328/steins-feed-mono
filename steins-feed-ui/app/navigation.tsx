import { NavigationSearchParams } from "./util"

import { doLanguagesFeedsLangaugesGet, doTagsFeedsTagsGet } from "./actions"
import { SideNav, TopNav } from "./components"

export default async function Navigation({
  now,
  languages,
  tags,
}: NavigationSearchParams) {
  const all_languages = await doLanguagesFeedsLangaugesGet();
  const all_tags = await doTagsFeedsTagsGet();

  return (
<>
<TopNav
  now={ now }
  languages={ languages }
  tags={ tags }
/>
<SideNav
  now={ now }
  languages={ languages }
  tags={ tags }
  all_languages={ all_languages }
  all_tags={ all_tags }
/>
</>
  );
}
