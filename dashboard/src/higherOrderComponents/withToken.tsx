import { useState } from 'react';

const withToken = (WrappedComponent: any) => {

  return function(props: any) {

    const getToken = () => {
      const userToken = window.localStorage.getItem('crypto-token');
      return userToken && userToken
    }

    const [token, setToken] = useState(getToken());

    const saveToken = (userToken: string) => {
      window.localStorage.setItem('crypto-token', userToken);
      setToken(userToken);
    };

    const removeToken = () => {
      window.localStorage.removeItem("crypto-token");
      setToken(null);
    }

    return <WrappedComponent saveToken={saveToken} token={token} removeToken={removeToken} {...props}/>
  }
}

// @ts-ignore
export default withToken