import { NavigationSearchParams } from "./util"

import { getLanguagesAction, getTagsAction } from "./actions"
import { SideNav, TopNav } from "./components"

export default async function Navigation({
  now,
  languages,
  tags,
  wall_mode,
  contentServed = false,
}: NavigationSearchParams & {
  contentServed?: boolean,
}) {
  const all_languages = await getLanguagesAction();
  const all_tags = await getTagsAction();

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
