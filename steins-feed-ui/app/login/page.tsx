import Container from "react-bootstrap/Container"

import { skip_login_if_unnecessary } from "../auth"
import LoginModal from "./components"

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{pathname?: string}>,
}) {
  const pathname = (await searchParams).pathname ?? "/";

  await skip_login_if_unnecessary(pathname);

  return (
<Container>
<LoginModal callback={ pathname }/>
</Container>
  );
}
