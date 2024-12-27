"use server"

import { cookies } from "next/headers"

export async function logout() {
  const cookie_store = await cookies();
  cookie_store.delete("api_token");
}
