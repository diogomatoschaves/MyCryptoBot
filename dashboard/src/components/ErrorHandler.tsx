import {ReactNode, Fragment} from "react";
import {Location} from 'history'
import {get} from 'lodash'

interface Props {
  removeToken: () => void
  location: Location
  children: ReactNode
}


const ErrorHandler = (props: Props) => {

  const {location, removeToken} = props

  switch (get(location.state, 'errorStatusCode')) {
    // @ts-ignore
    case 401:
      removeToken()
      return (
        <Fragment>
          {props.children}
        </Fragment>
      )
    default:
      return (
        <Fragment>
          {props.children}
        </Fragment>
      )
  }
}

export default ErrorHandler