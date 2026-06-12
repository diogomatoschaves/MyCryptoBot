// Always call the data service same-origin at /api so the httpOnly JWT cookie
// is sent: in dev the Vite proxy forwards /api, in docker-compose the dashboard
// nginx forwards it, and in production the data service serves the dashboard.
const urlPrefix = '/api'


const getCookie = (name: string): string | null => {
  const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'))
  return match ? decodeURIComponent(match[2]) : null
}

interface RequestOptions {
  method?: string
  body?: object
  auth?: boolean
}

const request = async <T = any>(path: string, options: RequestOptions = {}): Promise<T> => {
  const { method = 'GET', body, auth = true } = options

  const headers: Record<string, string> = {
    "Accept": "application/json, text/plain, */*",
  }
  if (body) headers["Content-Type"] = "application/json"

  // CSRF double-submit: echo the readable csrf cookie on state-changing calls
  if (method !== 'GET' && method !== 'HEAD') {
    const csrf = getCookie('csrf_access_token')
    if (csrf) headers["X-CSRF-TOKEN"] = csrf
  }

  const response = await fetch(`${urlPrefix}${path}`, {
    method,
    headers,
    credentials: 'include',  // send/receive the httpOnly JWT cookie
    ...(body ? { body: JSON.stringify(body) } : {})
  })

  // Session expired / invalid: App.logoutUser matches on the message below.
  // Unauthenticated requests (login) return the body so the caller can show
  // the server's error message instead.
  if (auth && (response.status === 401 || response.status === 422)) {
    throw new Error(String(response.status))
  }

  return await response.json()
}

export const getResources = (resources: string[]) =>
  request(`/resources/${resources.join()}`)

export const getTrades = (page?: number, pipelineId?: string) =>
  request(`/trades${page ? '/' + page : ''}${pipelineId ? '?pipelineId=' + pipelineId : ''}`)

export const getPipelines = (page?: number) =>
  request(`/pipelines${page ? '/' + page : ''}`)

export const getPositions = (page?: number) =>
  request(`/positions${page ? '/' + page : ''}`)

export const getPrice = (symbol: string) =>
  request(`/prices?symbol=${symbol}`)

export const getFuturesAccountBalance = () =>
  request('/futures_account_balance')

export const startBot = (requestData: object) =>
  request('/start_bot', { method: 'PUT', body: requestData })

export const stopBot = (requestData: object) =>
  request('/stop_bot', { method: 'PUT', body: requestData })

export const editBot = (requestData: object, pipelineId?: number | string) =>
  request(`/pipelines?pipelineId=${pipelineId}`, { method: 'PUT', body: requestData })

export const deleteBot = (pipelineId: number | string) =>
  request(`/pipelines?pipelineId=${pipelineId}`, { method: 'DELETE' })

export const getTradesMetrics = (pipelineId?: string) =>
  request(`/trades-metrics${pipelineId ? `?pipelineId=${pipelineId}` : ''}`)

export const getPipelinesMetrics = () =>
  request('/pipelines-metrics')

export const userLogin = (requestData: object) =>
  request('/token', { method: 'POST', body: requestData, auth: false })

// auth state probe (httpOnly cookie can't be read by JS)
export const getMe = () => request('/me')

export const logout = () =>
  request('/logout', { method: 'POST', auth: false })

export const getEquityTimeSeries = ({ pipelineId, maxItems }: { pipelineId?: number | string | null, maxItems?: number }) =>
  request(`/pipeline-equity${pipelineId ? '/' + pipelineId : ''}${maxItems ? `?maxItems=${maxItems}` : ''}`)
