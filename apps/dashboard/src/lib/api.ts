import {
  getMockBrief,
  getMockBuySheet,
  getMockCandidates,
  mockRunController
} from "./mock";
import type { Brief, Candidate, Run } from "./types";

const DEFAULT_API_BASE = "http://localhost:8000";
const EXPLICIT_API_BASE = process.env.NEXT_PUBLIC_API_BASE;
export const API_BASE = EXPLICIT_API_BASE || DEFAULT_API_BASE;

let usingMock = !EXPLICIT_API_BASE;

export function isUsingMock(): boolean {
  return usingMock;
}

function setMockMode(value: boolean) {
  usingMock = value;
}

function fallback<T>(producer: () => T): T {
  setMockMode(true);
  return producer();
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  if (!EXPLICIT_API_BASE) {
    throw new Error("Mock mode");
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3_000);

  try {
    const response = await fetch(`/api/theta${path}`, {
      ...init,
      cache: "no-store",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {})
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    setMockMode(false);
    return (await response.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

export async function getLatestRun(): Promise<Run> {
  try {
    return await requestJson<Run>("/runs/latest");
  } catch {
    return fallback(() => mockRunController.getRun());
  }
}

export async function getCandidates(): Promise<Candidate[]> {
  try {
    return await requestJson<Candidate[]>("/candidates");
  } catch {
    return fallback(() => getMockCandidates());
  }
}

export async function getLatestBrief(): Promise<Brief> {
  try {
    return await requestJson<Brief>("/briefs/latest");
  } catch {
    return fallback(() => getMockBrief());
  }
}

export async function startRun(mode: "live" | "replay"): Promise<Run> {
  try {
    return await requestJson<Run>("/runs", {
      method: "POST",
      body: JSON.stringify({ mode })
    });
  } catch {
    return fallback(() => mockRunController.start(mode));
  }
}

export async function buySheet(): Promise<{ paid: boolean; tx: string; sheet: Brief }> {
  try {
    return await requestJson<{ paid: boolean; tx: string; sheet: Brief }>("/briefs/today/buy", {
      method: "POST"
    });
  } catch {
    return fallback(() => getMockBuySheet());
  }
}
