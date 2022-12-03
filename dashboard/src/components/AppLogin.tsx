import {Fragment} from "react";
import App from "./App";
import {Location} from 'history'
import withToken from "../higherOrderComponents/withToken";
import Login from "./Login";
import {Redirect, Route, Switch} from "react-router-dom";


interface Props {
  location: Location
  history: History
  token: string | undefined
  saveToken: (userToken: string) => void
  removeToken: () => void
}

const AppLogin = (props: Props) => {

  const { location, token, saveToken, removeToken } = props

  return (
    <Fragment>
      {token ? (
        <App location={location} removeToken={removeToken}/>
      ) : (!token && token !=="" && token !== undefined && location.pathname !== "/login") ? (
        <Redirect to="/login"/>
      ) : (
        <Switch>
          <Route path="/login">
            <Login saveToken={saveToken}/>
          </Route>
          <Route path="*">
            <App location={location} removeToken={removeToken}/>
          </Route>
        </Switch>
      )}
    </Fragment>
  )
}


export default withToken(AppLogin)