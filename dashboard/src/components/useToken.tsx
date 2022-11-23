import { useState } from 'react';

function useToken() {

  function getToken() {
    const userToken = localStorage.getItem('crypto-token');
    return userToken && userToken
  }

  const [token, setToken] = useState(getToken());

  function saveToken(userToken: string) {
    localStorage.setItem('crypto-token', userToken);
    setToken(userToken);
  };

  function removeToken() {
    localStorage.removeItem("crypto-token");
    setToken(null);
  }

  return {
    setToken: saveToken,
    token,
    removeToken
  }
}

export default useToken