export function createInspectionSession() {
  let currentToken = Symbol("initial-inspection-state");

  return Object.freeze({
    begin() {
      currentToken = Symbol("inspection");
      return currentToken;
    },
    invalidate() {
      currentToken = Symbol("invalidated-inspection");
    },
    isCurrent(token) {
      return token === currentToken;
    },
  });
}

export async function readTextForInspection(file, session, token) {
  try {
    const text = await file.text();
    return session.isCurrent(token)
      ? { status: "ready", text }
      : { status: "stale" };
  } catch {
    return session.isCurrent(token)
      ? { status: "error" }
      : { status: "stale" };
  }
}
