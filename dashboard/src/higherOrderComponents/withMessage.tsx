import {Component, Fragment} from "react";
import {UpdateMessage} from "../types";
import {Toast} from "../ui";


interface State {
  text: string | null
  success: boolean
  visible: boolean
}


const withMessage = (WrappedComponent: any) => {

  class MessageWrapper extends Component<any, State> {

    hideTimeout: any

    state: State = {
      text: null,
      success: true,
      visible: false,
    }

    updateMessage: UpdateMessage = (newMessage: any) => {
      this.setState({
        text: newMessage.text,
        success: newMessage.success !== undefined ? newMessage.success : true,
        visible: true,
      })

      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout)
      }
      this.hideTimeout = setTimeout(() => {
        this.setState({visible: false})
      }, 4200)
    }

    componentWillUnmount() {
      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout)
      }
    }

    render() {

      const {text, success, visible} = this.state

      return (
        <Fragment>
          <WrappedComponent updateMessage={this.updateMessage} {...this.props}/>
          {text && <Toast visible={visible} success={success} message={text}/>}
        </Fragment>
      )

    }
  }

  return MessageWrapper
}


export default withMessage
