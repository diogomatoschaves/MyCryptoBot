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


export const getOrders = async (page) => {

  const url = `${apiHost}/orders${page ? '/' + page : ''}`

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