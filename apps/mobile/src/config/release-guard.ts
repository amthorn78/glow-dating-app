/**
 * The root layout's runtime release guard (`src/app/_layout.tsx`): synthetic routes and controls
 * render only in a development bundle (React Native's `__DEV__`) in fixture mode. The layout passes
 * `__DEV__` and `process.env.EXPO_PUBLIC_GLOW_MODE` itself, so Expo still inlines the mode there.
 */
export const developmentPreviewAvailable = (isDevelopment: boolean, mode: string | undefined) => isDevelopment && mode === 'fixture';
