import { NextRequest, NextResponse } from "next/server";

const DEFAULT_API_BASE = "http://localhost:8000";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

type RouteContext = {
  params: {
    path: string[];
  };
};

function buildTargetUrl(request: NextRequest, path: string[]) {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE || DEFAULT_API_BASE;
  const requestUrl = new URL(request.url);
  const cleanBase = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
  const target = new URL(path.map(encodeURIComponent).join("/"), cleanBase);
  target.search = requestUrl.search;
  return target.toString();
}

async function proxy(request: NextRequest, context: RouteContext) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3_000);

  try {
    const body =
      request.method === "GET" || request.method === "HEAD" ? undefined : await request.text();
    const response = await fetch(buildTargetUrl(request, context.params.path), {
      method: request.method,
      body,
      cache: "no-store",
      signal: controller.signal,
      headers: {
        "Content-Type": request.headers.get("content-type") ?? "application/json"
      }
    });

    return new NextResponse(await response.text(), {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("content-type") ?? "application/json"
      }
    });
  } catch {
    return NextResponse.json({ ok: false }, { status: 502 });
  } finally {
    clearTimeout(timeout);
  }
}

export async function GET(request: NextRequest, context: RouteContext) {
  return proxy(request, context);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxy(request, context);
}
