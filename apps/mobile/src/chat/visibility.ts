/**
 * Which messages are inside the conversation's visible area (CX8; DM-23 2.1), from the
 * rendered layout only: each row's box measured in the scroll content, and the scroll
 * view's measured offset and height. Never from the fact that a page arrived.
 */
export type Box = Readonly<{ top: number; height: number }>;
export type VisibleArea = Readonly<{ offset: number; height: number }>;

/** Sub-pixel rounding between the measured offset and boxes; never a whole line of text. */
const TOLERANCE = 1;

/**
 * A row is in view when its whole box lies inside the visible area or, for a row taller than
 * the area, when it fills the area. An unmeasured row, or an unmeasured area, is never in view.
 */
export function inVisibleArea(box: Box | undefined, area: VisibleArea): boolean {
  if (!box || !(box.height > 0) || !(area.height > 0)) return false;
  const top = box.top, bottom = box.top + box.height, start = area.offset, end = area.offset + area.height;
  return (top >= start - TOLERANCE && bottom <= end + TOLERANCE) || (top <= start && bottom >= end);
}

/** The IDs, in the order given, whose measured rows are now in view. */
export function visibleMessages(ids: readonly string[], boxes: ReadonlyMap<string, Box>, area: VisibleArea): string[] {
  return ids.filter(id => inVisibleArea(boxes.get(id), area));
}
