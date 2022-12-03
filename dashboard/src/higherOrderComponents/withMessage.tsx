import {Fragment, Component} from "react";
import MessageComponent from "../components/Message";
import {StyledBox} from "../styledComponents";
import {Message, UpdateMessage} from "../types";


interface State {
  message: Message
}


const withMessage = (WrappedComponent: any) => {

  class MessageWrapper extends Component<any, State> {

    messageTimeout: any

    state = {
      message: {show: false, bottomProp: "-300px", text: null, color: "#000000", success: true},
    }

    updateMessage: UpdateMessage = (newMessage) => {
      this.setState(state => ({
        message: {
          ...state.message,
          show: true,
          ...newMessage,
        }
      }))
    }

    componentDidUpdate(prevProps: Readonly<any>, prevState: Readonly<State>, snapshot?: any) {

      const { message } = this.state

      if (prevState.message.show !== message.show && message.show) {
        this.setState({message: {...message, bottomProp: "40px", show: false}})

        if (this.messageTimeout) {
          clearTimeout(this.messageTimeout)
        }
        this.messageTimeout = setTimeout(() => {
          this.setState((state) =>
              ({
                message: {
                  ...state.message,
                  bottomProp: "-300px"
                }
              }),
            () => {
              if (this.messageTimeout) {
                clearTimeout(this.messageTimeout)
              }
            }
          )
        }, 4200)
      }
    }

    render() {

      const {message} = this.state

      return (
        <Fragment>
          <WrappedComponent updateMessage={this.updateMessage} {...this.props}/>
          {message.text && (
            <StyledBox
              align="center"
              bottom={message.bottomProp}
              left="50%"
              position="absolute"
              padding="0px"
              className="message-container"
            >
              <MessageComponent success={message.success} message={message.text} color={message.color}/>
            </StyledBox>
          )}
        </Fragment>
      )

    }
  }

  return MessageWrapper
}


export default withMessage