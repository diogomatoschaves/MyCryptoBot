import { useEffect, useState } from 'react';
import { getMe, logout } from '../apiCalls';

// The JWT now lives in an httpOnly cookie that JS can't read, so auth state is
// derived from a /me probe rather than a localStorage token. `token` is:
//   undefined -> still resolving, null -> logged out, truthy -> logged in.
const withToken = (WrappedComponent: any) => {

  return function(props: any) {

    const [token, setToken] = useState<string | null | undefined>(undefined);

    useEffect(() => {
      getMe()
        .then((res) => setToken(res && res.username ? res.username : null))
        .catch(() => setToken(null));
    }, []);

    const saveToken = (username: string) => {
      setToken(username || (true as any));
    };

    const removeToken = () => {
      logout().catch(() => {}).finally(() => setToken(null));
    };

    return <WrappedComponent saveToken={saveToken} token={token} removeToken={removeToken} {...props}/>
  }
}

// @ts-ignore
export default withToken
