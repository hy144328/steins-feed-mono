import SideNav from "./sidenav"
import TopNav from "./topnav"
import { NavigationSearchParams } from "./util"

export default function Navigation({
  now,
  languages,
  tags,
  wall_mode,
  contentServed = false,
}: NavigationSearchParams & {
  contentServed?: boolean,
}) {
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
/>
</>
  );
}
