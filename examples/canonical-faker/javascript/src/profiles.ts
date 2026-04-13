export interface Profile {
  numOrgs: number
  numUsers: number
  seed: number
  name: string
}

export const SMOKE: Profile = { numOrgs: 3, numUsers: 10, seed: 42, name: "smoke" }
export const SMALL: Profile = { numOrgs: 20, numUsers: 200, seed: 1000, name: "small" }
export const MEDIUM: Profile = { numOrgs: 200, numUsers: 5000, seed: 5000, name: "medium" }
export const LARGE: Profile = { numOrgs: 2000, numUsers: 50000, seed: 9999, name: "large" }

export const PROFILES: Record<string, Profile> = {
  smoke: SMOKE,
  small: SMALL,
  medium: MEDIUM,
  large: LARGE
}
