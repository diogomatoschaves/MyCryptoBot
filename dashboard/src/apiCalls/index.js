const apiHost = process.env.REACT_APP_API_HOST

export const getResources = async (resources) => {

  const resourcesString = resources.join()

  const url = `${apiHost}/resources/${resourcesString}`

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

  const url = `${apiHost}/trades${page ? '/' + page : ''}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching orders'))
      } else {
        return res.json()
      }
    })
}


export const getPipelines = async (page) => {

  const url = `${apiHost}/pipelines${page ? '/' + page : ''}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching orders'))
      } else {
        return res.json()
      }
    })
}


export const getPositions = async (page) => {

  const url = `${apiHost}/positions${page ? '/' + page : ''}`

  return await fetch(url, {
    method: 'GET',
    headers: {
      "Accept": "application/json, text/plain, */*",
    }
  })
    .then(res => {
      if (res.status >= 400) {
        throw(new Error('Error fetching orders'))
      } else {
        return res.json()
      }
    })
}


export const startBot = async (requestData) => {

  const url = `${apiHost}/start_bot`

  const response = await fetch(url, {
    body: JSON.stringify(requestData),
    method: 'PUT'
  })

  return await response.json()
}


export const stopBot = async (requestData) => {

  const url = `${apiHost}/stop_bot`

  const response = await fetch(url, {
    body: JSON.stringify(requestData),
    method: 'PUT'
  })

  return await response.json()
}