import { apiRequest } from "./api";

const ACCESS_TOKEN_KEY = "trainecg_access_token";

export const getAccessToken = (): string | null => {
  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setAccessToken = (token: string) => {
  try {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  } catch {
    // Ignore storage errors (private mode, etc.)
  }
};

export const clearAccessToken = () => {
  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
  } catch {
    // Ignore storage errors
  }
};

/**
 * Decodify JWT token without verification (client-side only)
 * This is safe because we validate with the backend
 */
export const decodeToken = (token: string): Record<string, unknown> | null => {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const decoded = parts[1];
    const padded = decoded + "=".repeat((4 - (decoded.length % 4)) % 4);
    const json = atob(padded);
    return JSON.parse(json);
  } catch {
    return null;
  }
};

/**
 * Check if token is expired based on JWT exp claim
 */
export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) return true;

    const expirationTime = (decoded.exp as number) * 1000; // Convert to milliseconds
    return Date.now() >= expirationTime;
  } catch {
    return true;
  }
};

/**
 * Validate token with backend by making a request to /users/me
 * Returns true if token is valid, false if invalid/expired
 */
export const validateTokenWithBackend = async (token: string): Promise<boolean> => {
  try {
    await apiRequest("/users/me", {
      token,
    });
    return true;
  } catch {
    return false;
  }
};

/**
 * Check if token is valid:
 * 1. Token exists
 * 2. Token is not expired (based on JWT exp claim)
 * 3. Token is valid with backend
 */
export const isTokenValid = async (token: string | null): Promise<boolean> => {
  if (!token) return false;

  // First check: is token expired based on JWT claims?
  if (isTokenExpired(token)) {
    clearAccessToken();
    return false;
  }

  // Second check: is token valid with backend?
  const isValid = await validateTokenWithBackend(token);
  if (!isValid) {
    clearAccessToken();
    return false;
  }

  return true;
};
