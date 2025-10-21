export const ADMIN_WHITELIST = new Set<string>(["ryanvdb"]); // add more as needed

export function isAdmin(username: string | null | undefined) {
  if (!username) return false;
  return ADMIN_WHITELIST.has(username);
}