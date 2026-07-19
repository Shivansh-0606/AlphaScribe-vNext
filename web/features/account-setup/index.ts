/**
 * Public surface — feature: account-setup
 *
 * The ONLY sanctioned entry point into this feature (02.1 AD-3, 02.2 AD-2).
 * Other modules import from here, never from ui/ application/ integration/
 * internal/ directly. Internals are private and may not cross this boundary
 * (02.7 AD-2). No feature implementation yet (M1 foundation).
 */
export {};
