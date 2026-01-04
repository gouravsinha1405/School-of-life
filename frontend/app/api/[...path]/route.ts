import { NextRequest } from "next/server";

function getBackendBaseUrl(): string {
  const url = process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!url) {
    throw new Error(
      "API_BASE_URL is not set (required for /api proxy). Set it to your backend base URL, e.g. https://<backend>.onrender.com",
    );
  }
  return url.replace(/\/$/, "");
}

async function proxy(req: NextRequest) {
  const backendBase = getBackendBaseUrl();
  const upstreamUrl = new URL(req.nextUrl.pathname + req.nextUrl.search, backendBase);

  const headers = new Headers(req.headers);
  headers.delete("host");

  const res = await fetch(upstreamUrl, {
    method: req.method,
    headers,
    body:
      req.method === "GET" || req.method === "HEAD" ? undefined : await req.arrayBuffer(),
    redirect: "manual",
  });

  // Pass through status, body, and important headers (including Set-Cookie)
  const outHeaders = new Headers(res.headers);
  outHeaders.delete("content-encoding");
  outHeaders.delete("content-length");

  return new Response(res.body, {
    status: res.status,
    headers: outHeaders,
  });
}

export async function GET(req: NextRequest) {
  return proxy(req);
}
export async function POST(req: NextRequest) {
  return proxy(req);
}
export async function PATCH(req: NextRequest) {
  return proxy(req);
}
export async function PUT(req: NextRequest) {
  return proxy(req);
}
export async function DELETE(req: NextRequest) {
  return proxy(req);
}
export async function OPTIONS(req: NextRequest) {
  return proxy(req);
}
