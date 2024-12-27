import Container from "react-bootstrap/Container"

import LoginModal from "./components"

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{pathname?: string}>,
}) {
  return (
<Container>
<LoginModal callback={ (await searchParams).pathname }/>
</Container>
  );
}
