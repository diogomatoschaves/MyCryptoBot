const dataAPIHost = process.env.REACT_APP_DATA_API_HOST
const executionAPIHost = process.env.REACT_APP_EXECUTION_API_HOST

export const getResources = async (resources) => {

  const resourcesString = resources.join()

  const url = `${dataAPIHost}/resources/${resourcesString}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching resources'))
      } else {
        return res.json()
      }
    })
}


export const getTrades = async (page) => {

  const url = `${dataAPIHost}/trades${page ? '/' + page : ''}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching trades'))
      } else {
        return res.json()
      }
    })
}


export const getPipelines = async (page) => {

  const url = `${dataAPIHost}/pipelines${page ? '/' + page : ''}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching pipelines'))
      } else {
        return res.json()
      }
    })
}


export const getPositions = async (page) => {

  const url = `${dataAPIHost}/positions${page ? '/' + page : ''}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching positions'))
      } else {
        return res.json()
      }
    })
}


export const getPrice = async (symbol) => {

  const url = `${executionAPIHost}/prices?symbol=${symbol}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching prices'))
      } else {
        return res.json()
      }
    })
}


export const getFuturesAccountBalance = async () => {

  const url = `${executionAPIHost}/futures_account_balance`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
      } else {
        return res.json()
      }
    })
}


export const startBot = async (requestData) => {

  const url = `${dataAPIHost}/start_bot`

  const response = await fetch(url, {
    body: JSON.stringify(requestData),
    method: 'PUT'
  })

  return await response.json()
}


export const stopBot = async (requestData) => {

  const url = `${dataAPIHost}/stop_bot`

  const response = await fetch(url, {
    body: JSON.stringify(requestData),
    method: 'PUT'
  })

  return await response.json()
}

export const deleteBot = async (pipelineId) => {

  const url = `${dataAPIHost}/pipelines?pipelineId=${pipelineId}`

  const response = await fetch(url, {
    method: 'DELETE'
  })

  return await response.json()
}