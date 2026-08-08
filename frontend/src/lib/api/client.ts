import { API_URL } from "@/lib/env";
import type { ApiError } from "@/types/api";

type JsonBody = Record<string, unknown> | unknown[] | string | number | boolean | null;

type ApiRequestOptions = Omit<RequestInit, "body"> & {
  path: string;
  body?: BodyInit | JsonBody;
  query?: Record<string, string | number | boolean | null | undefined>;
};

export class ApiClientError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: unknown;

  constructor({
    status,
    code,
    message,
    details,
  }: {
    status: number;
    code: string;
    message: string;
    details?: unknown;
  }) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function buildUrl(path: string, query?: ApiRequestOptions["query"]) {
  const url = new URL(`${API_URL}${path}`);

  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      url.searchParams.set(key, String(value));
    }
  });

  return url.toString();
}

function isBodyInit(body: ApiRequestOptions["body"]): body is BodyInit {
  return (
    body instanceof FormData ||
    body instanceof Blob ||
    body instanceof ArrayBuffer ||
    body instanceof URLSearchParams ||
    body instanceof ReadableStream
  );
}

async function parseErrorResponse(response: Response): Promise<ApiClientError> {
  try {
    const payload = (await response.json()) as Partial<ApiError>;
    const error = payload.error;

    if (error?.code && error.message) {
      return new ApiClientError({
        status: response.status,
        code: error.code,
        message: error.message,
        details: error.details,
      });
    }
  } catch {
    // Fall through to a generic normalized error below.
  }

  return new ApiClientError({
    status: response.status,
    code: "API_REQUEST_FAILED",
    message: `API request failed with status ${response.status}`,
  });
}

export async function apiRequest<TResponse>({
  path,
  query,
  headers,
  body,
  ...init
}: ApiRequestOptions): Promise<TResponse> {
  const requestHeaders = new Headers(headers);
  const requestBody = isBodyInit(body) ? body : JSON.stringify(body);

  if (body !== undefined && !isBodyInit(body) && !requestHeaders.has("Content-Type")) {
    requestHeaders.set("Content-Type", "application/json");
  }

  const response = await fetch(buildUrl(path, query), {
    ...init,
    body: requestBody,
    credentials: init.credentials ?? "include",
    headers: requestHeaders,
  });

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  return response.json() as Promise<TResponse>;
}
