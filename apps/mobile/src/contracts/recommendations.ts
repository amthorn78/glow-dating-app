/** App-owned development projection; never an HDE wire contract. */
export type DevelopmentProfile = Readonly<{
  profile_id: string;
  display_name: string;
  age: number;
  summary: string;
  compatibility: Readonly<{ status: 'pending'; source: 'fixture' }>;
}>;
export type DevelopmentRecommendations = Readonly<{
  mode: 'fixture';
  contract_version: 'gapp-dev-v1';
  items: readonly DevelopmentProfile[];
}>;

export class ContractError extends Error {
  constructor() {
    super('The development response does not match the supported public contract.');
    this.name = 'ContractError';
  }
}

function record(value: unknown): Record<string, unknown> {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new ContractError();
  return value as Record<string, unknown>;
}

function keys(value: Record<string, unknown>, allowed: readonly string[]) {
  if (Object.keys(value).length !== allowed.length || Object.keys(value).some((key) => !allowed.includes(key))) {
    throw new ContractError();
  }
}

function text(value: unknown, maxLength: number): string {
  if (typeof value !== 'string' || value.trim().length === 0 || value.length > maxLength) throw new ContractError();
  return value;
}

/** Closed shape deliberately rejects private fields, scores and unreviewed contract extensions. */
export function parseDevelopmentRecommendations(value: unknown): DevelopmentRecommendations {
  const root = record(value);
  keys(root, ['mode', 'contract_version', 'items']);
  if (root.mode !== 'fixture' || root.contract_version !== 'gapp-dev-v1' || !Array.isArray(root.items) || root.items.length > 50) {
    throw new ContractError();
  }
  const ids = new Set<string>();
  const items = root.items.map((candidate): DevelopmentProfile => {
    const item = record(candidate);
    keys(item, ['profile_id', 'display_name', 'age', 'summary', 'compatibility']);
    const compatibility = record(item.compatibility);
    keys(compatibility, ['status', 'source']);
    if (compatibility.status !== 'pending' || compatibility.source !== 'fixture' ||
        typeof item.age !== 'number' || !Number.isInteger(item.age) || item.age < 18 || item.age > 120) {
      throw new ContractError();
    }
    const profileId = text(item.profile_id, 100);
    if (ids.has(profileId)) throw new ContractError();
    ids.add(profileId);
    return {
      profile_id: profileId,
      display_name: text(item.display_name, 80),
      age: item.age,
      summary: text(item.summary, 500),
      compatibility: { status: 'pending', source: 'fixture' },
    };
  });
  return { mode: 'fixture', contract_version: 'gapp-dev-v1', items };
}
