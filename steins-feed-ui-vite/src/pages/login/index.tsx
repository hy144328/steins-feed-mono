import { skip_login_if_unnecessary } from "@/auth"

import LoginModal from "./modal"

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{pathname?: string}>,
}) {
  const pathname = (await searchParams).pathname ?? "/";

  await skip_login_if_unnecessary(pathname);

  return (
<div className="container">
<LoginModal callback={ pathname }/>
</div>
  );
}
