export function getUsername(): string | null {
  return localStorage.getItem("username");
}
export function isLoggedIn(): boolean {
  return !!localStorage.getItem("token");
}
export function setAuth(token: string, username: string) {
  localStorage.setItem("token", token);
  localStorage.setItem("username", username);
  // notify same-tab listeners
  window.dispatchEvent(new Event("auth"));
}
export function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("username");
  window.dispatchEvent(new Event("auth"));
}
export function logout() {
  clearAuth();
  // after clearing, route to signin (full replace is fine here)
  window.location.replace("/signin");
}