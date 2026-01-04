#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import secrets
import statistics
import time
from dataclasses import dataclass

import httpx


@dataclass
class Result:
    ok: int = 0
    failed: int = 0
    latencies_ms: list[float] | None = None

    def __post_init__(self) -> None:
        if self.latencies_ms is None:
            self.latencies_ms = []


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    k = (len(values_sorted) - 1) * pct
    f = int(k)
    c = min(f + 1, len(values_sorted) - 1)
    if f == c:
        return values_sorted[f]
    d0 = values_sorted[f] * (c - k)
    d1 = values_sorted[c] * (k - f)
    return d0 + d1


async def register_or_login(
    client: httpx.AsyncClient,
    *,
    email: str,
    password: str,
    preferred_language: str,
) -> str:
    # Try register (idempotent-ish). If already exists -> login.
    r = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "preferred_language": preferred_language},
        timeout=30.0,
    )
    if r.status_code not in (201, 400):
        raise RuntimeError(f"register failed for {email}: {r.status_code} {r.text}")

    # Always login to get a bearer token for concurrency-safe auth.
    r2 = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        timeout=30.0,
    )
    if r2.status_code != 200:
        raise RuntimeError(f"login failed for {email}: {r2.status_code} {r2.text}")
    data = r2.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"login response missing access_token for {email}: {data}")
    return token


async def create_entry(
    client: httpx.AsyncClient,
    *,
    token: str,
    text: str,
    mood_score: int,
    energy_score: int,
) -> str:
    r = await client.post(
        "/api/journal",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": text, "mood_score": mood_score, "energy_score": energy_score},
        timeout=30.0,
    )
    if r.status_code != 201:
        raise RuntimeError(f"create_entry failed: {r.status_code} {r.text}")
    data = r.json()
    entry_id = (data.get("entry") or {}).get("id")
    if not entry_id:
        raise RuntimeError(f"create_entry response missing entry.id: {data}")
    return entry_id


async def maybe_fetch_report(client: httpx.AsyncClient, *, token: str) -> None:
    r = await client.get(
        "/api/report/current",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30.0,
    )
    if r.status_code != 200:
        raise RuntimeError(f"report/current failed: {r.status_code} {r.text}")


async def maybe_poll_analysis(
    client: httpx.AsyncClient,
    *,
    token: str,
    entry_id: str,
    timeout_s: float,
    interval_s: float,
) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = await client.get(
            f"/api/journal/{entry_id}/analysis",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        if r.status_code != 200:
            raise RuntimeError(f"analysis poll failed: {r.status_code} {r.text}")
        if r.json() is not None:
            return
        await asyncio.sleep(interval_s)
    raise RuntimeError(f"analysis not ready after {timeout_s}s for entry_id={entry_id}")


async def run_user_flow(
    *,
    base_url: str,
    email: str,
    password: str,
    preferred_language: str,
    entries_per_user: int,
    mood_score: int,
    energy_score: int,
    fetch_report: bool,
    poll_analysis: bool,
    poll_timeout_s: float,
    poll_interval_s: float,
) -> None:
    async with httpx.AsyncClient(base_url=base_url) as client:
        token = await register_or_login(
            client,
            email=email,
            password=password,
            preferred_language=preferred_language,
        )

        created_entry_ids: list[str] = []
        for i in range(entries_per_user):
            text = f"Load test entry {i + 1}/{entries_per_user}: {secrets.token_hex(16)}"
            entry_id = await create_entry(
                client,
                token=token,
                text=text,
                mood_score=mood_score,
                energy_score=energy_score,
            )
            created_entry_ids.append(entry_id)

        if poll_analysis:
            for entry_id in created_entry_ids:
                await maybe_poll_analysis(
                    client,
                    token=token,
                    entry_id=entry_id,
                    timeout_s=poll_timeout_s,
                    interval_s=poll_interval_s,
                )

        if fetch_report:
            await maybe_fetch_report(client, token=token)


async def main_async(args: argparse.Namespace) -> int:
    sem = asyncio.Semaphore(args.concurrency)
    result = Result()

    async def wrapped(i: int) -> None:
        email = f"{args.email_prefix}{i:05d}@{args.email_domain}"
        t0 = time.perf_counter()
        try:
            async with sem:
                await run_user_flow(
                    base_url=args.base_url,
                    email=email,
                    password=args.password,
                    preferred_language=args.preferred_language,
                    entries_per_user=args.entries_per_user,
                    mood_score=args.mood_score,
                    energy_score=args.energy_score,
                    fetch_report=args.fetch_report,
                    poll_analysis=args.poll_analysis,
                    poll_timeout_s=args.poll_timeout_s,
                    poll_interval_s=args.poll_interval_s,
                )
            result.ok += 1
        except Exception as e:  # noqa: BLE001
            result.failed += 1
            if args.verbose:
                print(f"[FAIL] user={email}: {e}")
        finally:
            result.latencies_ms.append((time.perf_counter() - t0) * 1000.0)

    await asyncio.gather(*(wrapped(i) for i in range(args.users)))

    lat = result.latencies_ms
    p50 = _percentile(lat, 0.50)
    p95 = _percentile(lat, 0.95)
    avg = statistics.mean(lat) if lat else 0.0

    print("Load test finished")
    print(f"  base_url: {args.base_url}")
    print(f"  users: {args.users}  concurrency: {args.concurrency}")
    print(f"  entries_per_user: {args.entries_per_user}  fetch_report: {args.fetch_report}  poll_analysis: {args.poll_analysis}")
    print(f"  ok: {result.ok}  failed: {result.failed}")
    print(f"  latency_ms: avg={avg:.1f}  p50={p50:.1f}  p95={p95:.1f}")

    return 0 if result.failed == 0 else 2


def main() -> int:
    p = argparse.ArgumentParser(description="Lebensschule concurrency/load test: bulk users + entries")
    p.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")

    p.add_argument("--users", type=int, default=25, help="Number of users to simulate")
    p.add_argument("--concurrency", type=int, default=10, help="Max concurrent user flows")
    p.add_argument("--entries-per-user", type=int, default=2, help="Journal entries per user")

    p.add_argument("--email-prefix", default="loadtest_user_", help="Email local-part prefix")
    p.add_argument("--email-domain", default="example.com", help="Email domain")
    p.add_argument("--password", default="Password123!", help="Password used for all generated users")
    p.add_argument("--preferred-language", default="de", choices=["de", "en"], help="Language for register")

    p.add_argument("--mood-score", type=int, default=5)
    p.add_argument("--energy-score", type=int, default=5)

    p.add_argument("--fetch-report", action="store_true", help="Call /api/report/current after creating entries")
    p.add_argument("--poll-analysis", action="store_true", help="Poll /analysis until ready for each entry")
    p.add_argument("--poll-timeout-s", type=float, default=30.0)
    p.add_argument("--poll-interval-s", type=float, default=1.0)

    p.add_argument("--verbose", action="store_true", help="Print per-user errors")

    args = p.parse_args()

    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")
    if args.users < 1:
        raise SystemExit("--users must be >= 1")

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
