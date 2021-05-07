

export const getResources = async (resources) => {

  const resourcesString = resources.join()

  const url = `http://localhost:5000/resources/${resourcesString}`

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

  const url = `http://localhost:5000/orders${page ? '/' + page : ''}`

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