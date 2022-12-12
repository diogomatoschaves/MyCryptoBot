import App from "./App";
import {Location} from 'history'
import withToken from "../higherOrderComponents/withToken";
import Login from "./Login";
import {Redirect, Route, Switch} from "react-router-dom";
import withMessage from "../higherOrderComponents/withMessage";
import {UpdateMessage} from "../types";
import ErrorHandler from "./ErrorHandler";


interface Props {
  location: Location
  history: History
  token: string | undefined
  saveToken: (userToken: string) => void
  removeToken: () => void
  updateMessage: UpdateMessage
}


const AppLogin = (props: Props) => {

  const { location, history, token, saveToken, removeToken, updateMessage } = props

  return (
    <ErrorHandler removeToken={removeToken} location={location}>
      {token ? (
        <App
          location={location}
          history={history}
          removeToken={removeToken}
          updateMessage={updateMessage}
        />
      ) : (!token && token !=="" && token !== undefined && location.pathname !== "/login") ? (
        <Redirect to="/login"/>
      ) : (
        <Switch>
          <Route path="/login">
            <Login saveToken={saveToken} updateMessage={updateMessage}/>
          </Route>
          <Route path="*">
            <App
              location={location}
              history={history}
              removeToken={removeToken}
              updateMessage={updateMessage}
            />
          </Route>
        </Switch>
      )}
    </ErrorHandler>
  )
}


export default withMessage(withToken(AppLogin))