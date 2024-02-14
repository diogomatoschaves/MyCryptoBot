import { useState } from 'react';
import {Button, Dimmer, Form, Input, Loader} from "semantic-ui-react";
import {userLogin} from "../apiCalls";
import styled from "styled-components";
import {capitalize} from "../utils/helpers";
import {UpdateMessage} from "../types";


const LoginForm = styled.div`
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
`


interface Props {
  size: string
  saveToken: (userToken: string) => void
  updateMessage: UpdateMessage
}

function Login(props: Props) {

  const { size, saveToken, updateMessage } = props

  const [loginForm, setloginForm] = useState({
    username: "",
    password: ""
  })

  const [loading, setLoading] = useState(false)

  function logMeIn(event: any) {
    setLoading(true)
    userLogin({
      username: loginForm.username,
      password: loginForm.password
    })
      .then((response) => {
        setLoading(false)
        if (response.access_token) {
          saveToken(response.access_token)
          updateMessage({
            text: "You're logged in!",
            success: true
          })
        } else if(response.status !== 200) {
          updateMessage({
            text: response.msg,
            success: false
          })
        }

      }).catch((error) => {
        updateMessage({
            text: 'Something went wrong... Check server logs.',
            success: false
          })
        setLoading(false)

        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
        }
    })

    setloginForm(({
      username: "",
      password: ""}))

    event.preventDefault()
  }

  function handleChange(event: any) {
    const {value, name} = event.target
    setloginForm(prevNote => ({
      ...prevNote, [name]: value})
    )}

  const isMobile = size === 'mobile'

  return (
    <LoginForm>
      <Dimmer active={loading}>
        <Loader indeterminate active={loading}></Loader>
      </Dimmer>
      <Form className="flex-column" style={{width: '100%', height: '100%'}}>
        {Object.keys(loginForm).map(name => (
          <Form.Field
            width={isMobile ? 8  : 5}
            onChange={handleChange}
            control={Input}
            label={capitalize(name)}
            name={name}
            type={name === "password" ? "password" : undefined}
            // @ts-ignore
            value={loginForm[name]}
          />
        ))}
        <Form.Field
          style={{alignSelf: 'flex-start'}}
          onClick={logMeIn}
          control={Button}
          type="submit"
        >
          Login
        </Form.Field>
      </Form>
      <Loader/>
    </LoginForm>
  );
}

export default Login;