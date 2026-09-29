let pending = false

export function requestSearchFocus() {
  pending = true
}

export function consumeSearchFocusRequest(): boolean {
  const was = pending
  pending = false
  return was
}
