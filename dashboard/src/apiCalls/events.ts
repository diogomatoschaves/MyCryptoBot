export interface PipelineEvent {
  type: 'pipeline.started' | 'pipeline.stopped' | 'pipeline.deactivated' | 'pipeline.start_failed'
  pipelineId: number
  reason: string | null
  active: boolean
  timestamp: string
}

// Subscribes to the server's pipeline lifecycle stream (SSE). The dashboard
// is same-origin with the data service everywhere (Vite proxy in dev, nginx
// in compose, served by the data service in prod). EventSource auto-reconnects
// on network errors; onConnect fires on every (re)connect so the caller can
// resync state it may have missed while disconnected. On an auth failure the
// browser closes the stream permanently - the regular polling (and its 401
// handling) takes over.
export const subscribePipelineEvents = (
  onEvent: (event: PipelineEvent) => void,
  onConnect?: () => void
): (() => void) => {
  const source = new EventSource('/api/events', {withCredentials: true})

  source.onopen = () => {
    if (onConnect) onConnect()
  }

  source.onmessage = (message) => {
    try {
      onEvent(JSON.parse(message.data))
    } catch {
      // malformed frame: ignore
    }
  }

  return () => source.close()
}
