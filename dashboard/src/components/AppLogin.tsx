import {Fragment} from "react";
import App from "./App";
import {Location} from 'history'
import useToken from "./useToken";
import Login from "./Login";


interface Props {
  location: Location
}

const AppLogin = (props: Props) => {

  const { location } = props

  const { token, removeToken, setToken } = useToken()

  console.log(token)

  return (
    <Fragment>
      {!token && token!=="" &&token!== undefined ? (
        <Login setToken={setToken} />
      ) : (
        <App location={location}/>
      )}
    </Fragment>
  )
}


export default AppLogin