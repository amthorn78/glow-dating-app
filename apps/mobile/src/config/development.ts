export type DevelopmentConfig = Readonly<{ mode: 'fixture'; apiOrigin?: string }>;

/** Runtime defense remains in place even if build configuration is bypassed. */
export function getDevelopmentConfig(input: {
  isDevelopment: boolean;
  mode: string | undefined;
  apiOrigin: string | undefined;
}): DevelopmentConfig {
  if (!input.isDevelopment || input.mode !== 'fixture') {
    throw new Error('This preview is available only in a development build.');
  }
  if (!input.apiOrigin) return { mode: 'fixture' };
  let url: URL;
  try {
    url = new URL(input.apiOrigin);
  } catch {
    throw new Error('The development API origin is invalid.');
  }
  const host = url.hostname;
  const privateHost = host === 'localhost' || host === '127.0.0.1' || host === '[::1]' ||
    /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(host) ||
    /^192\.168\.\d{1,3}\.\d{1,3}$/.test(host) ||
    /^172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}$/.test(host);
  if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && privateHost)) ||
      url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error('Use an HTTPS origin, or a private HTTP development origin, without credentials or a path.');
  }
  return { mode: 'fixture', apiOrigin: url.origin };
}
