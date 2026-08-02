/**
 * Public surface — feature: account-setup
 *
 * The ONLY sanctioned entry point into this feature (02.1 AD-3, 02.2 AD-2).
 * Other modules import from here, never from ui/ application/ integration/
 * internal/ directly. Internals are private and may not cross this boundary
 * (02.7 AD-2).
 */
export { AuthGate } from "./ui/AuthGate";
export { LoginForm } from "./ui/LoginForm";
export { SignupForm } from "./ui/SignupForm";
export { ForgotPasswordForm } from "./ui/ForgotPasswordForm";
export { SettingsPanel } from "./ui/SettingsPanel";
export { AIAccessSelector } from "./ui/AIAccessSelector";
export { useAuthStatus, useIdentity } from "./application/useAuth";
export { useAiAccessStatus } from "./application/useAiAccess";
