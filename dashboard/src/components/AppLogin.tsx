import {Fragment} from "react";
import App from "./App";
import {Location} from 'history'
import withToken from "../higherOrderComponents/withToken";
import Login from "./Login";
import {Redirect, Route, Switch} from "react-router-dom";
import withMessage from "../higherOrderComponents/withMessage";
import {UpdateMessage} from "../types";


interface Props {
  location: Location
  history: History
  token: string | undefined
  saveToken: (userToken: string) => void
  removeToken: () => void
  updateMessage: UpdateMessage
}

const AppLogin = (props: Props) => {

  const { location, token, saveToken, removeToken, updateMessage } = props

  return (
    <Fragment>
      {token ? (
        <App location={location} removeToken={removeToken} updateMessage={updateMessage}/>
      ) : (!token && token !=="" && token !== undefined && location.pathname !== "/login") ? (
        <Redirect to="/login"/>
      ) : (
        <Switch>
          <Route path="/login">
            <Login saveToken={saveToken} updateMessage={updateMessage}/>
          </Route>
          <Route path="*">
            <App location={location} removeToken={removeToken} updateMessage={updateMessage}/>
          </Route>
        </Switch>
      )}
    </Fragment>
  )
}


export default withMessage(withToken(AppLogin))