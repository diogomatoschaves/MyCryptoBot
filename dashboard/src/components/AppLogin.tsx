import App from "./App";
import {Location} from 'history'
import withToken from "../higherOrderComponents/withToken";
import Login from "./Login";
import {Redirect, Route, Switch} from "react-router-dom";
import withMessage from "../higherOrderComponents/withMessage";
import {UpdateMessage} from "../types";
import ErrorHandler from "./ErrorHandler";
import withWindowSizeListener from "../higherOrderComponents/withWindowSizeListener";


interface Props {
  size: string
  location: Location
  history: History
  token: string | undefined
  saveToken: (userToken: string) => void
  removeToken: () => void
  updateMessage: UpdateMessage
}


const AppLogin = (props: Props) => {

  const { size, location, history, token, saveToken, removeToken, updateMessage } = props

  return (
    <ErrorHandler removeToken={removeToken} location={location}>
      {token ? (
        <App
          size={size}
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
            <Login size={size} saveToken={saveToken} updateMessage={updateMessage}/>
          </Route>
          <Route path="*">
            <App
              size={size}
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


export default withWindowSizeListener(withMessage(withToken(AppLogin)))
