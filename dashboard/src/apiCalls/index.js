
const dataAPIHost = process.env.REACT_APP_DATA_API_HOST || ''

const domain = window.location.origin !== dataAPIHost && dataAPIHost ? dataAPIHost : window.location.origin

const urlPrefix = new URL('api', domain).toString();


const getToken = () => {
  return `Bearer ${window.localStorage.getItem('crypto-token')}`
}

export const getResources = async (resources, history) => {

  const resourcesString = resources.join()

  const url = `${urlPrefix}/resources/${resourcesString}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const getTrades = async (page, pipelineId) => {

  const url = `${urlPrefix}/trades${page ? '/' + page : ''}${pipelineId ? '?pipelineId=' + pipelineId : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const getPipelines = async (page) => {

  const url = `${urlPrefix}/pipelines${page ? '/' + page : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const getPositions = async (page) => {

  const url = `${urlPrefix}/positions${page ? '/' + page : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const getPrice = async (symbol) => {

  const url = `${urlPrefix}/prices?symbol=${symbol}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const getFuturesAccountBalance = async () => {

  const url = `${urlPrefix}/futures_account_balance`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const startBot = async (requestData) => {

  const url = `${urlPrefix}/start_bot`

  const response = await fetch(url, {
    method: 'PUT',
    body: JSON.stringify(requestData),
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const stopBot = async (requestData) => {

  const url = `${urlPrefix}/stop_bot`

  const response = await fetch(url, {
    method: 'PUT',
    body: JSON.stringify(requestData),
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}

export const editBot = async (requestData, pipelineId) => {

  const url = `${urlPrefix}/pipelines?pipelineId=${pipelineId}`

  const response = await fetch(url, {
    method: 'PUT',
    body: JSON.stringify(requestData),
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}

export const deleteBot = async (pipelineId) => {

  const url = `${urlPrefix}/pipelines?pipelineId=${pipelineId}`

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}

export const getTradesMetrics = async (pipelineId) => {
  const url = `${urlPrefix}/trades-metrics${pipelineId ? `?pipelineId=${pipelineId}` : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}


export const getPipelinesMetrics = async () => {
  const url = `${urlPrefix}/pipelines-metrics`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}

export const userLogin = async (requestData) => {
  const url = `${urlPrefix}/token`

  const response = await fetch(url, {
    body: JSON.stringify(requestData),
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Authorization": getToken()
    }
  })

  return await response.json()
}

export const getEquityTimeSeries = async ({pipelineId, timeFrame}) => {

  const url = `${urlPrefix}/pipeline-equity${pipelineId ? '/' + pipelineId : ''}${timeFrame ? `?timeFrame=${timeFrame}` : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}

export const getPipelinesPnl = async (pipelineIds) => {

  const url = `${urlPrefix}/pipelines-pnl${pipelineIds ? '/' + pipelineIds.join() : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
      "Authorization": getToken()
    }
  })

  return await response.json()
}