import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const isAuthed = request.cookies.get("bankscan_auth")?.value === "1";
  const { pathname } = request.nextUrl;

  if (!isAuthed && pathname !== "/login") {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (isAuthed && pathname === "/login") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/login", "/admin"],
};
