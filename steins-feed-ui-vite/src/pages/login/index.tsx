import { useNavigate, useSearchParams } from "react-router"

import { skip_login_if_unnecessary } from "@/auth"

import LoginModal from "./modal"

export default function Page() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate();
  const pathname = searchParams.get("pathname") ?? "/";

  skip_login_if_unnecessary(navigate, pathname);

  return (
<div className="container">
<LoginModal callback={ pathname }/>
</div>
  );
}
