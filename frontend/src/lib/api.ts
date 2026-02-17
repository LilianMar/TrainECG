import { getAccessToken, clearAccessToken } from "@/lib/auth";

type ApiRequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  isForm?: boolean;
  token?: string | null;
};

const getApiBaseUrl = () => {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000";
};

const getErrorMessage = async (response: Response) => {
  try {
    const data = await response.json();
    if (typeof data?.detail === "string") {
      return data.detail;
    }
    if (typeof data?.message === "string") {
      return data.message;
    }
  } catch {
    // Ignore JSON parsing errors
  }
  return `Request failed with status ${response.status}`;
};

export const apiRequest = async <T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> => {
  const url = `${getApiBaseUrl()}${path}`;
  const token = options.token ?? getAccessToken();
  const headers: Record<string, string> = {
    ...(options.headers ?? {}),
  };

  let body: BodyInit | undefined;
  if (options.isForm && options.body instanceof FormData) {
    body = options.body;
  } else if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(options.body);
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers,
    body,
  });

  if (!response.ok) {
    // Si el token es inválido o expiró, limpiar y redirigir al login
    if (response.status === 401) {
      clearAccessToken();
      window.location.href = "/login";
      throw new Error("Sesión expirada. Por favor, inicia sesión nuevamente.");
    }
    
    const message = await getErrorMessage(response);
    throw new Error(message);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
};
