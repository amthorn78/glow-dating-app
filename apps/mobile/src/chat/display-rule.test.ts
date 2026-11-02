import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';
import { ChatClient, ChatFailure } from './client.ts';
import * as copy from './copy.ts';
import { LIST_COPY, READ_COPY, SEND_COPY, UNAVAILABLE_MESSAGE } from './copy.ts';
import { PROVIDER_FIELD_CASES, PROVIDER_SENTINEL, plantProviderField } from './fixture-adapter.ts';
import type { ChatTransport } from './transport.ts';
import { chatSetup, settle } from './testing.ts';

/**
 * The display rule (ADR 0003; the brief's point g; item 10): a response carrying any
 * provider field is refused by the generated validators and gives Glow's own error state;
 * nothing of it reaches the store, which is all the screens render.
 */
const MESSAGE_KEYS = ['at', 'author', 'content', 'delivery', 'submission_id', 'text'];
/** A provider's name, its objects or its wording (ADR 0003, decision 3). */
const PROVIDER_TERMS = /\b(providers?|stream|getstream|cloudflare|allauth|channels?|members?|custom|ai)\b/i;
const state = (fixture: Awaited<ReturnType<typeof chatSetup>>) => JSON.stringify(fixture.store.getSnapshot());

for (const field of PROVIDER_FIELD_CASES) test(`a response carrying ${field.replaceAll('_', ' ')} is refused and shows Glow's error state`, async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Glow sent this.');
  fixture.store.select(fixture.matchId); fixture.store.openConversation(); fixture.store.showList(); await settle();
  const before = fixture.store.getSnapshot().conversation.messages;
  assert.deepEqual(before.map(message => message.text), ['Glow sent this.']);
  fixture.fixture.setProviderField(field);
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Arrived with the planted field.');
  // The open conversation's poll and the list's.
  await fixture.timers.advance(30_000);
  let snapshot = fixture.store.getSnapshot();
  assert.equal(snapshot.conversation.status, 'error');
  assert.equal(snapshot.conversation.error, 'invalid_response');
  assert.deepEqual(snapshot.conversation.messages, before, 'no part of a refused page is used');
  assert.deepEqual([snapshot.list.status, snapshot.list.error], ['error', 'invalid_response']);
  // A send whose response carries the field is not confirmed, and may be retried with the same intent.
  fixture.store.setDraft('Mine.'); await fixture.store.send();
  snapshot = fixture.store.getSnapshot();
  assert.deepEqual([snapshot.send.status, snapshot.send.error, snapshot.send.canRetry], ['error', 'invalid_response', true]);
  assert.equal(state(fixture).includes(PROVIDER_SENTINEL), false);
  assert.equal(state(fixture).includes('Arrived with the planted field.'), false);
  // Glow's wording for that state names no provider and gives no reason.
  for (const text of [READ_COPY.invalid_response, LIST_COPY.invalid_response, SEND_COPY.invalid_response]) assert.doesNotMatch(text, PROVIDER_TERMS);
  // Back to Glow's own data: the messages it shows carry only the contract's fields.
  fixture.fixture.setProviderField(null); await fixture.timers.advance(3_000);
  snapshot = fixture.store.getSnapshot();
  assert.equal(snapshot.conversation.status, 'ready');
  assert.ok(snapshot.conversation.messages.some(message => message.text === 'Arrived with the planted field.'));
  for (const message of snapshot.conversation.messages) assert.deepEqual(Object.keys(message).sort(), MESSAGE_KEYS);
});

test('a conversation whose first page carries a provider field shows only Glow\'s error state', async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Never shown.');
  fixture.fixture.setProviderField('user_object');
  fixture.store.select(fixture.matchId); fixture.store.openConversation(); await settle();
  const { conversation } = fixture.store.getSnapshot();
  assert.deepEqual([conversation.status, conversation.error, conversation.messages.length], ['error', 'invalid_response', 0]);
  assert.equal(state(fixture).includes('Never shown.'), false);
});

test('each provider field, planted in every response kind, is refused by the client', async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Hello.');
  const page = await fixture.fixture.messages({ match_id: fixture.matchId, cursor: null, limit: 20 }) as object;
  const list = await fixture.fixture.conversations() as object;
  const submission = await fixture.fixture.send({ operation: 'message', match_id: fixture.matchId, text: 'Hi.', meta: { expected_version: 1, idempotency_key: 'k' } }) as object;
  const messageId = (page as { data: { messages: { submission_id: string }[] } }).data.messages[0]!.submission_id;
  const summary = await fixture.fixture.readCursor({ operation: 'read_cursor', match_id: fixture.matchId, submission_id: messageId }) as object;
  for (const field of PROVIDER_FIELD_CASES) {
    for (const [name, body, call] of [
      ['page', page, (client: ChatClient) => client.messages(fixture.matchId, null, 20)],
      ['list', list, (client: ChatClient) => client.conversations()],
      ['submission', submission, (client: ChatClient) => client.send(client.messageIntent(fixture.matchId, 'Hi.', 1, 'k'))],
      ['summary', summary, (client: ChatClient) => client.readCursor(client.readCursorIntent(fixture.matchId, messageId))],
    ] as const) {
      const planted = plantProviderField(body, field, '00000090-0000-4000-8000-0000000000aa');
      const transport: ChatTransport = { conversations: async () => planted, messages: async () => planted, send: async () => planted, readCursor: async () => planted };
      await assert.rejects(call(new ChatClient(transport)), (error: unknown) => error instanceof ChatFailure && error.code === 'invalid_response', `${field} in a ${name}`);
    }
  }
});

test('"unavailable" is Glow\'s own wording with no reason (DM-22 7.2, 6.2)', async () => {
  const fixture = await chatSetup();
  fixture.fixture.developmentOtherSend('profile-jules', fixture.matchId, 'Changed later.');
  fixture.fixture.developmentAlterLatest(fixture.matchId);
  fixture.store.select(fixture.matchId); fixture.store.openConversation(); await settle();
  const [message] = fixture.store.getSnapshot().conversation.messages;
  assert.deepEqual([message!.content, message!.text], ['unavailable', null]);
  assert.equal(UNAVAILABLE_MESSAGE, 'This message is unavailable.');
  assert.equal(state(fixture).includes('Changed later'), false);
});

test('every copy table and label in copy.ts names no provider (M05 finding 18; ADR 0003, decision 3)', () => {
  const texts: string[] = [];
  for (const [name, value] of Object.entries(copy)) {
    if (typeof value === 'string') texts.push(value);
    else if (name === 'timeLabel') texts.push(copy.timeLabel('2026-09-23T12:00:05Z'));
    else if (name === 'unreadLabel') texts.push(...[0, 1, 2].map(count => copy.unreadLabel(count)));
    else for (const entry of Object.values(value as Record<string, string>)) texts.push(entry);
  }
  // Every export is read: the six tables and constants and the two labels.
  assert.deepEqual(Object.keys(copy).sort(), ['DELIVERY_COPY', 'LIST_COPY', 'READ_COPY', 'REVOKED_DETAIL', 'SEND_COPY', 'UNAVAILABLE_MESSAGE', 'timeLabel', 'unreadLabel']);
  assert.equal(texts.length, 3 * 8 + 3 + 2 + 1 + 3);
  for (const text of texts) {
    assert.equal(typeof text, 'string');
    assert.doesNotMatch(text, PROVIDER_TERMS, text);
  }
});

/**
 * The render rule (M05 finding 18): the screens show only contract fields, whatever a response
 * carried, so a provider-shaped field (a message's `name`, a member, custom data) is never read
 * even if a validator let it through. Nothing renders `screen.tsx` in Node, so its source, with
 * the list rows' model (`rows.ts`), is checked twice.
 *
 * The source check reads every property path through the six names the screens use (a message,
 * a conversation, the list, the store's state, a match and a row) against a named list, and
 * refuses a cast, `any`, a spread, a computed or reflective read and an `in` check on a string.
 *
 * The type check (correction C1) does not depend on names. It builds the two files with the
 * TypeScript compiler the app declares, under the app's `tsconfig.json`, and finds Glow's data by
 * type: any value whose type is declared in the generated contracts, the chat store, the row
 * model or the interactions' state (`GLOW_DATA`), through any binding. It refuses:
 * - a read from Glow's data of a property its type does not declare (one the compiler allows
 *   only after an `in` check, through `any`, or not at all), and a computed or rest read of it;
 * - an `in` check, a `for…in` enumeration, a destructuring assignment or a spread of Glow's data;
 * - a widening: Glow's data passed (directly, or through `call`, `apply` or `bind`), returned,
 *   assigned, destructured under an annotation, or given as a prop or a callback parameter,
 *   where the expected type declares a property the data's type does not, or is `any`,
 *   `unknown`, `object`, `{}` or an index signature (so `Object.values`, `JSON.stringify` and
 *   `String` of it are refused too);
 * - a local generic or overload, whose types the check does not follow;
 * - any type error in the two files.
 * Its named exceptions: the value an Array predicate (`filter`, `some`, `every`, `find`…)
 * returns, which the predicate reads for truthiness alone; an element of a React hook's
 * dependency list, which React compares by identity; the initializer of an unannotated object
 * destructuring, whose reads the pattern's own check covers; and a type parameter of a function
 * outside the two files, which is inferred from the value. It reads the two files only: a
 * module they import is not checked (the evidence record names the forms that still evade it).
 */
const RENDERED_PATHS = new Set([
  // ConversationMessage: the contract's six fields.
  'message.submission_id', 'message.author', 'message.delivery', 'message.content', 'message.text', 'message.at',
  // ConversationSummary, as a list row (rows.ts), and the row the screen renders.
  'conversation.match_id', 'conversation.state', 'conversation.unread_count', 'conversation.latest', 'conversation.latest.at',
  'row.matchId', 'row.name', 'row.openable', 'row.status', 'row.latest',
  // The store's conversation state.
  'conversation.status', 'conversation.error', 'conversation.hasOlder', 'conversation.older', 'conversation.messages',
  'conversation.messages.length', 'conversation.messages.map',
  'list.status', 'list.error', 'list.conversations', 'list.conversations.length', 'list.conversations.map', 'list.conversations.match_id',
  'state.draft', 'state.send', 'state.send.status', 'state.send.error', 'state.send.canRetry', 'state.matches', 'state.matches.filter',
  // Glow's own match projection, for names (ADR 0003, decision 1).
  'match.match_id', 'match.state', 'match.profile', 'match.profile.display_name',
]);
const ROOTS = /\b(message|conversation|list|state|match|row)((?:!?\??\.[A-Za-z_$][\w$]*|\[\d+\]\??)*)/g;
const SCREEN = fileURLToPath(new URL('./screen.tsx', import.meta.url));
const ROWS = fileURLToPath(new URL('./rows.ts', import.meta.url));
function withoutComments(source: string) {
  return source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '').replace(/\{\/\*.*?\*\/\}/g, '');
}
function renderedPaths(source: string) {
  const paths = new Set<string>();
  for (const [, root, chain] of source.matchAll(ROOTS)) {
    const segments = chain!.replace(/\[\d+\]/g, '').replace(/[!?]/g, '').split('.').filter(Boolean);
    for (let index = 1; index <= segments.length; index++) paths.add([root, ...segments.slice(0, index)].join('.'));
  }
  return paths;
}
/** The source check, over the two files' text with comments removed. */
function sourceViolations(source: string) {
  const violations = [...renderedPaths(source)].filter(path => !RENDERED_PATHS.has(path));
  if (/[\w)\]!]\s+as\s+(?!const\b)/.test(source)) violations.push('a type cast');
  if (/\bany\b/.test(source.replace(/'[^'\n]*'|`[^`\n]*`/g, ''))) violations.push('an any type');
  if (/\b(Object\s*\.\s*(?!freeze\b)\w+|Reflect\s*\.|JSON\s*\.)/.test(source)) violations.push('a reflective read');
  if (/\.\.\.\s*(message|conversation|list|state|match|row)\b/.test(source)) violations.push('a spread');
  if (/\b(message|conversation|list|state|match|row)\s*\[\s*(?!\d+\s*\])/.test(source)) violations.push('a computed read');
  if (/(['"`])[^'"`\n]*\1\s+in\b/.test(source)) violations.push('an in check');
  return violations;
}

/** Where Glow's data types are declared: the generated contracts, the chat store and row model, the interactions' state. */
const GLOW_DATA = new Set(['../contracts/generated/gapp-api-v1.ts', '../contracts/generated/gapp-dev-v1.ts', './store.ts', './rows.ts',
  '../interactions/store.ts', '../interactions/fixture-adapter.ts'].map(path => fileURLToPath(new URL(path, import.meta.url))));
const PREDICATES = new Set(['filter', 'some', 'every', 'find', 'findIndex', 'findLast', 'findLastIndex']);

/**
 * The type check. `files` maps each checked path to its text; a planted path sits beside
 * `screen.tsx`, so its imports resolve as the screen's do. All are built in one program.
 */
function typedViolations(files: ReadonlyMap<string, string>) {
  const config = ts.getParsedCommandLineOfConfigFile(fileURLToPath(new URL('../../tsconfig.json', import.meta.url)), {},
    { ...ts.sys, onUnRecoverableConfigFileDiagnostic: diagnostic => { throw new Error(ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n')); } });
  assert.ok(config && config.errors.length === 0, 'the app\'s tsconfig.json is read');
  const host = ts.createCompilerHost(config.options, true);
  const getSourceFile = host.getSourceFile.bind(host);
  host.getSourceFile = (name, language, onError, create) => files.has(name)
    ? ts.createSourceFile(name, files.get(name)!, language, true) : getSourceFile(name, language, onError, create);
  host.fileExists = name => files.has(name) || ts.sys.fileExists(name);
  host.readFile = name => files.get(name) ?? ts.sys.readFile(name);
  const program = ts.createProgram([...files.keys()], config.options, host);
  const checker = program.getTypeChecker();

  const inGlowData = (symbol: ts.Symbol | undefined) => symbol?.declarations?.some(declaration => GLOW_DATA.has(declaration.getSourceFile().fileName)) ?? false;
  const parts = (type: ts.Type): readonly ts.Type[] => type.isUnion() ? type.types.flatMap(parts) : [type];
  const nonNull = (type: ts.Type) => parts(type).filter(part => !(part.flags & (ts.TypeFlags.Null | ts.TypeFlags.Undefined | ts.TypeFlags.Void)));
  const elements = (type: ts.Type) => checker.isArrayType(type) || checker.isTupleType(type) ? checker.getTypeArguments(type as ts.TypeReference) : null;
  /** A type that is Glow's data itself: one of its parts declares a property in a Glow data file. */
  const isGlowData = (type: ts.Type): boolean => nonNull(type).some(part => part.isIntersection() ? part.types.some(isGlowData)
    : elements(part) === null && (part.flags & ts.TypeFlags.Object) !== 0 && checker.getPropertiesOfType(part).some(inGlowData));
  /** A type that carries Glow's data: itself, or an array or tuple of it. */
  const carries = (type: ts.Type, depth = 0): boolean => depth < 4 && (isGlowData(type) || nonNull(type).some(part => elements(part)?.some(element => carries(element, depth + 1)) ?? false));
  /** Whether a value of `source` keeps its type at a place that expects `target`. */
  const keeps = (source: ts.Type, target: ts.Type, depth = 0): boolean => {
    if (depth > 4) return true;
    if (target.flags & (ts.TypeFlags.Any | ts.TypeFlags.Unknown | ts.TypeFlags.NonPrimitive)) return false;
    if (target.flags & ts.TypeFlags.TypeParameter) {
      // A type parameter declared outside the checked files is inferred from the value, which keeps its type.
      if (!target.getSymbol()?.declarations?.some(declaration => files.has(declaration.getSourceFile().fileName))) return true;
      const constraint = checker.getBaseConstraintOfType(target);
      return constraint === undefined || (constraint.flags & ts.TypeFlags.Unknown) !== 0 || keeps(source, constraint, depth + 1);
    }
    const sources = nonNull(source).filter(part => carries(part));
    return nonNull(target).every(part => {
      if (part.isIntersection()) return part.types.every(type => keeps(source, type, depth + 1));
      const targetElements = elements(part);
      if (targetElements !== null) return sources.every(type => {
        const sourceElements = elements(type);
        return sourceElements !== null && targetElements.every((element, index) => keeps(sourceElements[Math.min(index, sourceElements.length - 1)]!, element, depth + 1));
      });
      if (part.flags & ts.TypeFlags.TypeParameter) return keeps(source, part, depth + 1);
      if (!(part.flags & ts.TypeFlags.Object)) return true;
      if (checker.getIndexInfosOfType(part).length > 0) return false;
      const properties = checker.getPropertiesOfType(part);
      if (properties.length === 0 && part.getCallSignatures().length === 0) return false;
      return sources.every(type => properties.every(property => {
        const own = checker.getPropertyOfType(type, property.name);
        if (!own) return false;
        const ownType = checker.getTypeOfSymbol(own);
        return !carries(ownType) || keeps(ownType, checker.getTypeOfSymbol(property), depth + 1);
      }));
    });
  };
  /** The value an Array predicate returns, which it reads for truthiness alone. */
  const predicateValue = (node: ts.Node) => {
    let current = node;
    while (ts.isParenthesizedExpression(current.parent) || ts.isConditionalExpression(current.parent) && current !== current.parent.condition
      || ts.isBinaryExpression(current.parent) && [ts.SyntaxKind.AmpersandAmpersandToken, ts.SyntaxKind.BarBarToken, ts.SyntaxKind.QuestionQuestionToken].includes(current.parent.operatorToken.kind)) current = current.parent;
    const arrow = current.parent;
    if (!ts.isArrowFunction(arrow) || arrow.body !== current || !ts.isCallExpression(arrow.parent) || !ts.isPropertyAccessExpression(arrow.parent.expression)) return false;
    if (!PREDICATES.has(arrow.parent.expression.name.text)) return false;
    const declaration = checker.getResolvedSignature(arrow.parent)?.declaration;
    return declaration !== undefined && program.isSourceFileDefaultLibrary(declaration.getSourceFile());
  };

  /** A signature's parameter type at `index`, through a rest parameter; -1 is its `this`. */
  const parameterAt = (signature: ts.Signature, index: number): ts.Type | undefined => {
    if (index < 0) return signature.thisParameter && checker.getTypeOfSymbol(signature.thisParameter);
    const parameters = signature.getParameters();
    const last = parameters[parameters.length - 1];
    const declaration = last?.valueDeclaration;
    if (last && declaration && ts.isParameter(declaration) && declaration.dotDotDotToken && index >= parameters.length - 1) {
      const rest = checker.getTypeOfSymbol(last);
      const items = elements(rest);
      return items === null ? rest : items[Math.min(index - parameters.length + 1, items.length - 1)];
    }
    return parameters[index] && checker.getTypeOfSymbol(parameters[index]);
  };
  /**
   * The type an argument is passed as: the resolved signature's parameter, instantiated. Through
   * `call`, `apply` or `bind`, it is the called function's own `this` or parameter, since the
   * method's type parameters are inferred from the arguments themselves.
   */
  const argumentType = (node: ts.Expression): ts.Type | undefined => {
    const parent = node.parent;
    const applied = ts.isArrayLiteralExpression(parent) && ts.isCallExpression(parent.parent) && parent.parent.arguments[1] === parent
      && ts.isPropertyAccessExpression(parent.parent.expression) && parent.parent.expression.name.text === 'apply';
    const call = applied ? parent.parent : parent;
    if (!(ts.isCallExpression(call) || ts.isNewExpression(call))) return undefined;
    const index = applied ? parent.elements.indexOf(node) + 1 : call.arguments?.indexOf(node) ?? -1;
    if (index < 0) return undefined;
    const callee = call.expression;
    if (ts.isCallExpression(call) && ts.isPropertyAccessExpression(callee) && ['call', 'apply', 'bind'].includes(callee.name.text)) {
      const [own] = checker.getTypeAtLocation(callee.expression).getCallSignatures();
      if (own) return callee.name.text === 'apply' && !applied && index === 1 ? undefined : parameterAt(own, index - 1);
    }
    if (applied) return undefined;
    const signature = checker.getResolvedSignature(call);
    return signature && parameterAt(signature, index);
  };
  /** An element of a React hook's dependency list, which React compares by identity alone. */
  const dependencyList = (node: ts.Node) => {
    const expected = ts.isArrayLiteralExpression(node) && ts.isCallExpression(node.parent) ? checker.getContextualType(node) : undefined;
    const alias = expected && checker.getNonNullableType(expected).aliasSymbol;
    return alias?.name === 'DependencyList' && (alias.declarations?.some(declaration => declaration.getSourceFile().fileName.includes('/node_modules/@types/react/')) ?? false);
  };
  const dependency = (node: ts.Node) => dependencyList(node) || dependencyList(node.parent);
  /** A destructuring's initializer, whose reads the binding pattern's own check covers. */
  const destructured = (node: ts.Node) => (ts.isVariableDeclaration(node.parent) || ts.isParameter(node.parent) || ts.isBindingElement(node.parent))
    && node.parent.initializer === node && ts.isObjectBindingPattern(node.parent.name) && (ts.isBindingElement(node.parent) || !node.parent.type);

  const result = new Map<string, string[]>();
  for (const name of files.keys()) {
    const file = program.getSourceFile(name)!;
    const violations: string[] = [];
    const say = (kind: string, node: ts.Node) => violations.push(`${kind}: ${node.getText(file).replace(/\s+/g, ' ').slice(0, 80)}`);
    const fieldRead = (receiver: ts.Type, property: ts.Symbol | undefined, node: ts.Node) => {
      if (isGlowData(receiver) && !inGlowData(property)) say('a field outside Glow\'s types', node);
    };
    for (const diagnostic of [...program.getSyntacticDiagnostics(file), ...program.getSemanticDiagnostics(file)]) {
      violations.push(`a type error: ${ts.flattenDiagnosticMessageText(diagnostic.messageText, ' ').slice(0, 100)}`);
    }
    const visit = (node: ts.Node) => {
      if (ts.isPropertyAccessExpression(node)) fieldRead(checker.getTypeAtLocation(node.expression), checker.getSymbolAtLocation(node.name), node);
      if (ts.isElementAccessExpression(node) && (isGlowData(checker.getTypeAtLocation(node.expression)) || checker.getTypeAtLocation(node.expression).flags & (ts.TypeFlags.TypeParameter | ts.TypeFlags.Any | ts.TypeFlags.Unknown))) say('a computed read', node);
      if (ts.isObjectBindingPattern(node)) {
        const receiver = checker.getTypeAtLocation(node);
        if (isGlowData(receiver)) for (const element of node.elements) {
          const key = element.propertyName ?? element.name;
          if (element.dotDotDotToken) say('a rest read', element);
          else if (ts.isIdentifier(key) || ts.isStringLiteral(key)) fieldRead(receiver, checker.getPropertyOfType(checker.getNonNullableType(receiver), key.text), element);
          else say('a computed read', element);
        }
      }
      if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.InKeyword) say('an in check', node);
      if (ts.isTypeParameterDeclaration(node)) say('a local generic', node.parent);
      if ((ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node)) && !node.body) say('a local overload', node);
      if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.EqualsToken && (ts.isObjectLiteralExpression(node.left) || ts.isArrayLiteralExpression(node.left))
        && carries(checker.getTypeAtLocation(node.right))) say('a destructuring assignment', node);
      if (ts.isForInStatement(node) && carries(checker.getTypeAtLocation(node.expression))) say('an enumeration', node);
      if ((ts.isSpreadElement(node) || ts.isSpreadAssignment(node) || ts.isJsxSpreadAttribute(node)) && carries(checker.getTypeAtLocation(node.expression))) say('a spread', node);
      if ((ts.isArrowFunction(node) || ts.isFunctionExpression(node))) {
        const expected = checker.getContextualType(node);
        for (const signature of expected ? nonNull(expected).flatMap(part => part.getCallSignatures()) : []) {
          node.parameters.forEach((parameter, index) => {
            const given = signature.parameters[index];
            if (!parameter.type || !given) return;
            const value = checker.getTypeOfSymbol(given);
            if (carries(value) && !keeps(value, checker.getTypeFromTypeNode(parameter.type))) say('a widening callback parameter', parameter);
          });
        }
      }
      if (ts.isExpression(node) && !(ts.isJsxAttribute(node.parent) && node.parent.name === node)) {
        const value = checker.getTypeAtLocation(node);
        const expected = carries(value) ? argumentType(node) ?? checker.getContextualType(node) : undefined;
        if (expected && !keeps(value, expected) && !destructured(node) && !dependency(node) && !((expected.flags & ts.TypeFlags.Unknown) && predicateValue(node))) say(`a widening to ${checker.typeToString(expected).slice(0, 120)}`, node);
      }
      ts.forEachChild(node, visit);
    };
    visit(file);
    result.set(name, violations);
  }
  return result;
}

/**
 * One planted form: an edit of `screen.tsx` that renders, or could render, a provider-shaped
 * field, and a violation the type check must report for it. `source` marks the nine forms the
 * source check was first tested against, which must still fail it too.
 */
type Planted = Readonly<{ form: string; edit: (screen: string) => string; typed: string; source?: true }>;
function once(text: string, anchor: string) {
  const at = text.indexOf(anchor);
  assert.ok(at >= 0 && text.indexOf(anchor, at + 1) < 0, `the anchor occurs once: ${anchor}`);
  return at;
}
const swap = (anchor: string, replacement: string) => (text: string) => {
  const at = once(text, anchor);
  return `${text.slice(0, at)}${replacement}${text.slice(at + anchor.length)}`;
};
const after = (anchor: string, addition: string) => swap(anchor, `${anchor}\n${addition}`);
const before = (anchor: string, addition: string) => swap(anchor, `${addition}\n${anchor}`);
const both = (...edits: ((text: string) => string)[]) => (text: string) => edits.reduce((edited, edit) => edit(edited), text);
/** `MessageRow` with its message bound as `item` (`item.` for `message.` in its body), then `more` applied to it. */
const asItem = (more: (row: string) => string) => (screen: string) => {
  const start = once(screen, 'function MessageRow(');
  const end = screen.indexOf('\n}\n', start) + 3;
  const row = swap('{ message, name, rowRef }', '{ message: item, name, rowRef }')(screen.slice(start, end)).replaceAll('message.', 'item.');
  return `${screen.slice(0, start)}${more(row)}${screen.slice(end)}`;
};
const ROW_TIME = '<Text style={styles.small}>{timeLabel(message.at)}{delivery}</Text>';
const ITEM_TIME = ROW_TIME.replace('message.', 'item.');
const ROW_START = '  const own =';
const LIST_STATUS = '<Text style={styles.body} testID={`conversation-unread-${row.matchId}`}>{row.status}</Text>';
const REVOKED = '<Text style={styles.body}>{REVOKED_DETAIL}</Text>';
const SCREEN_START = '  const revoked =';
const HELPERS = 'type Viewing = ReturnType<typeof useViewedMessages>;';
const LOOSE = '{ name?: string; text: string | null }';
const LOOSE_TYPE = '{ name?: string | undefined; text: string | null; }';
const PLANTED: readonly Planted[] = [
  // The nine forms the source check was first tested against (P06.2-F), now placed in the screen.
  { form: '{message.name}', edit: after(ROW_TIME, '{message.name}'), typed: 'a field outside Glow\'s types: message.name', source: true },
  { form: '{(message as { name?: string }).name}', edit: after(ROW_TIME, '{(message as { name?: string }).name}'),
    typed: 'a widening to { name?: string | undefined; }: message', source: true },
  { form: '{String(message[\'name\'])}', edit: after(ROW_TIME, '{String(message[\'name\'])}'), typed: 'a computed read: message[\'name\']', source: true },
  { form: '<Text {...message} />', edit: after(ROW_TIME, '<Text {...message} />'), typed: 'a spread: {...message}', source: true },
  { form: '{Object.values(message).join()}', edit: after(ROW_TIME, '{Object.values(message).join()}'),
    typed: 'a widening to { [s: string]: string | null; } | ArrayLike<string | null>: message', source: true },
  { form: '{conversation.member?.name}', edit: after(REVOKED, '{conversation.member?.name}'), typed: 'a field outside Glow\'s types: conversation.member', source: true },
  { form: '{(message as any).user}', edit: after(ROW_TIME, '{(message as any).user}'), typed: 'a widening to any: message', source: true },
  { form: '{row.custom}', edit: after(LIST_STATUS, '{row.custom}'), typed: 'a field outside Glow\'s types: row.custom', source: true },
  { form: '{Object.entries(conversation)}', edit: after(REVOKED, '{Object.entries(conversation)}'), typed: 'a widening to ReactNode: Object.entries(conversation)', source: true },
  // Correction C1: the exact-head review's PA and PB, and the brief's PC.
  { form: 'PA: MessageRow\'s message bound as item, rendering {\'name\' in item ? String(item.name) : null}',
    edit: asItem(after(ITEM_TIME, '{\'name\' in item ? String(item.name) : null}')), typed: 'a field outside Glow\'s types: item.name' },
  { form: `PB: <Eyebrow entry={message} />, whose prop ${LOOSE} renders entry.name`,
    edit: both(before(HELPERS, `function Eyebrow({ entry }: { entry: ${LOOSE} }) { return <Text style={styles.eyebrow}>{entry.name ?? ''}</Text>; }\n`),
      after(ROW_TIME, '<Eyebrow entry={message} />')), typed: `a widening to ${LOOSE_TYPE}: message` },
  { form: 'PC: const { name: label } = item, rendering {label}',
    edit: asItem(both(before(ROW_START, '  const { name: label } = item;'), after(ITEM_TIME, '{label}'))), typed: 'a field outside Glow\'s types: name: label' },
  // Correction C1: further forms the session tried, each passing tsc except the last.
  { form: `a loose annotation: const loose: ${LOOSE} = item, rendering {loose.name}`,
    edit: asItem(both(before(ROW_START, `  const loose: ${LOOSE} = item;`), after(ITEM_TIME, '{loose.name}'))), typed: `a widening to ${LOOSE_TYPE}: item` },
  { form: `a generic helper: <Label entry={item} />, where Label<T extends ${LOOSE}> renders entry.name`,
    edit: both(before(HELPERS, `function Label<T extends ${LOOSE}>({ entry }: { entry: T }) { return <Text>{entry.name ?? ''}</Text>; }\n`),
      asItem(after(ITEM_TIME, '<Label entry={item} />'))), typed: `a local generic: function Label<T extends ${LOOSE}>({ entry }: { en` },
  { form: `a loosely typed callback parameter: conversation.messages.map((entry: ${LOOSE}) => entry.name)`,
    edit: after(REVOKED, `<Text>{conversation.messages.map((entry: ${LOOSE}) => entry.name).join()}</Text>`), typed: `a widening callback parameter: entry: ${LOOSE}` },
  { form: `a call through Function.prototype.call: ((entry: ${LOOSE}) => entry.name).call(null, message)`,
    edit: after(ROW_TIME, `{((entry: ${LOOSE}) => entry.name).call(null, message)}`), typed: `a widening to ${LOOSE_TYPE}: message` },
  { form: `a loosely typed this: (function (this: ${LOOSE}) { return this.name; }).call(message)`,
    edit: after(ROW_TIME, `{(function (this: ${LOOSE}) { return this.name; }).call(message)}`), typed: `a widening to ${LOOSE_TYPE}: message` },
  { form: `a call through Function.prototype.apply: ((entry: ${LOOSE}) => entry.name).apply(null, [message])`,
    edit: after(ROW_TIME, `{((entry: ${LOOSE}) => entry.name).apply(null, [message])}`), typed: `a widening to ${LOOSE_TYPE}: message` },
  { form: `an annotated destructuring: const { name: label }: ${LOOSE} = item, rendering {label}`,
    edit: asItem(both(before(ROW_START, `  const { name: label }: ${LOOSE} = item;`), after(ITEM_TIME, '{label}'))), typed: `a widening to ${LOOSE_TYPE}: item` },
  { form: `a local overload: loud(entry: ConversationMessage), implemented as loud(entry: ${LOOSE}) returning entry.name`,
    edit: both(before(HELPERS, `function loud(entry: ConversationMessage): string;\nfunction loud(entry: ${LOOSE}) { return entry.name ?? ''; }\n`),
      after(ROW_TIME, '<Text>{loud(message)}</Text>')), typed: 'a local overload: function loud(entry: ConversationMessage): string;' },
  { form: `a loosely typed list: const loose: readonly ${LOOSE}[] = conversation.messages, rendering {loose[0]?.name}`,
    edit: both(before(SCREEN_START, `  const loose: readonly ${LOOSE}[] = conversation.messages;`), after(REVOKED, '<Text>{loose[0]?.name}</Text>')),
    typed: `a widening to readonly ${LOOSE_TYPE}[]: conversation.messages` },
  { form: 'a for…of destructuring: for (const { name: label } of conversation.messages)',
    edit: before(SCREEN_START, '  for (const { name: label } of conversation.messages) void label;'), typed: 'a field outside Glow\'s types: name: label' },
];

test('the chat screens render only the contract\'s fields: no provider-shaped field is read, whatever the validators let through (M05 finding 18)', () => {
  const screen = readFileSync(SCREEN, 'utf8');
  const rows = readFileSync(ROWS, 'utf8');
  const source = `${withoutComments(screen)}\n${withoutComments(rows)}`;
  assert.deepEqual(sourceViolations(source), []);
  // Each message field the screen reads is one of the contract's.
  const read = [...renderedPaths(source)].filter(path => path.startsWith('message.')).map(path => path.slice('message.'.length));
  assert.deepEqual(read.filter(key => !MESSAGE_KEYS.includes(key)), []);
  // The type check, through any binding (correction C1).
  assert.deepEqual(Object.fromEntries(typedViolations(new Map([[SCREEN, screen], [ROWS, rows]]))), { [SCREEN]: [], [ROWS]: [] });
});

test('the render rule\'s checks refuse each planted form of a provider-shaped field (M05 finding 18; correction C1)', () => {
  const screen = readFileSync(SCREEN, 'utf8');
  const rows = withoutComments(readFileSync(ROWS, 'utf8'));
  const planted = PLANTED.map((entry, index) => ({ ...entry, path: SCREEN.replace(/\.tsx$/, `.planted-${index}.tsx`), text: entry.edit(screen) }));
  assert.equal(planted.length, 22);
  const typed = typedViolations(new Map(planted.map(entry => [entry.path, entry.text])));
  for (const entry of planted) {
    // The nine forms the source check was tested against still fail it.
    if (entry.source) assert.notDeepEqual(sourceViolations(`${withoutComments(entry.text)}\n${rows}`), [], `the source check: ${entry.form}`);
    // Every form fails the type check, for the reason named, not only as a type error.
    assert.ok(typed.get(entry.path)!.includes(entry.typed), `the type check: ${entry.form}: ${JSON.stringify(typed.get(entry.path))}`);
  }
});
