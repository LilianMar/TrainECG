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
