import {useState} from 'react';
import styled from "styled-components";
import {LogIn} from 'lucide-react'
import {userLogin} from "../apiCalls";
import {UpdateMessage} from "../types";
import {Button, Field, TextInput} from "../ui";


const Page = styled.div`
  width: 100vw;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background-image:
    radial-gradient(700px 380px at 50% -10%, rgba(198, 244, 50, 0.08), transparent 60%),
    radial-gradient(900px 500px at 80% 110%, rgba(79, 157, 255, 0.07), transparent 60%),
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: auto, auto, 44px 44px, 44px 44px;
`

const LoginCard = styled.div`
  width: 100%;
  max-width: 380px;
  background: var(--bg-raised);
  border: 1px solid var(--border-strong);
  border-radius: 16px;
  box-shadow: var(--shadow-pop);
  padding: 40px 36px 36px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  animation: scaleIn 0.35s ease both;
`

const Brand = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
`

const BrandName = styled.span`
  font-family: var(--font-ui);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--text);

  em {
    font-style: normal;
    color: var(--accent);
  }
`

const BrandSub = styled.span`
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--text-faint);

  &::before {
    content: '';
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 10px var(--green);
    animation: pulseGlow 2.4s ease infinite;
  }
`

interface Props {
  size: string
  saveToken: (userToken: string) => void
  updateMessage: UpdateMessage
}

function Login(props: Props) {

  const { saveToken, updateMessage } = props

  const [loginForm, setloginForm] = useState({
    username: "",
    password: ""
  })

  const [loading, setLoading] = useState(false)

  function logMeIn(event: any) {
    event.preventDefault()
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

      }).catch(() => {
        updateMessage({
            text: 'Something went wrong... Check server logs.',
            success: false
          })
        setLoading(false)
    })

    setloginForm(({
      username: "",
      password: ""}))
  }

  function handleChange(event: any) {
    const {value, name} = event.target
    setloginForm(prevNote => ({
      ...prevNote, [name]: value})
    )}

  return (
    <Page>
      <LoginCard>
        <Brand>
          <BrandName>
            MyCrypto<em>Bot</em>
          </BrandName>
          <BrandSub>Trading Terminal</BrandSub>
        </Brand>
        <form
          onSubmit={logMeIn}
          style={{display: 'flex', flexDirection: 'column', gap: 18}}
        >
          <Field label="Username">
            <TextInput
              name="username"
              value={loginForm.username}
              onChange={handleChange}
              autoComplete="username"
              autoFocus
            />
          </Field>
          <Field label="Password">
            <TextInput
              name="password"
              type="password"
              value={loginForm.password}
              onChange={handleChange}
              autoComplete="current-password"
            />
          </Field>
          <Button
            type="submit"
            variant="primary"
            fullWidth
            loading={loading}
            icon={<LogIn/>}
            style={{marginTop: 6}}
          >
            Log in
          </Button>
        </form>
      </LoginCard>
    </Page>
  );
}

export default Login;
