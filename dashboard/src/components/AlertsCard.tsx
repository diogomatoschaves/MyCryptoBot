import {useEffect, useState} from 'react'
import styled from 'styled-components'
import {BellRing, BookOpen, Send, Settings2} from 'lucide-react'
import {getAlertsStatus, saveAlertsSettings, sendTestAlert} from '../apiCalls'
import {
  Button, Card, CardHeader, CardTitle, Field, InlineMessage, Modal, Stat, Tag, TextInput
} from '../ui'
import {theme} from '../theme'


const Row = styled.div`
  display: flex;
  align-items: center;
  gap: 28px;
  flex-wrap: wrap;
`

const Actions = styled.div`
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
`

const FormStack = styled.div`
  display: flex;
  flex-direction: column;
  gap: 18px;
`

const FormNote = styled.p`
  margin: 0;
  font-size: 12px;
  color: var(--text-faint);
  line-height: 1.6;
`

const GuideList = styled.ol`
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-dim);

  strong {
    color: var(--text);
  }

  code {
    font-family: var(--font-mono);
    font-size: 12px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1px 6px;
    color: var(--accent);
  }
`

const GuideNote = styled.p`
  margin: 18px 0 0;
  font-size: 12px;
  color: var(--text-faint);
  line-height: 1.6;
`

interface AlertsStatus {
  configured: boolean
  source: 'env' | 'database' | null
  chatId: string | null
}

const SOURCE_LABELS: Record<string, string> = {
  env: 'Environment',
  database: 'Dashboard',
}

const AlertsCard = () => {

  const [status, setStatus] = useState<AlertsStatus | null>(null)
  const [guideOpen, setGuideOpen] = useState(false)
  const [configOpen, setConfigOpen] = useState(false)
  const [botToken, setBotToken] = useState('')
  const [chatId, setChatId] = useState('')
  const [saving, setSaving] = useState(false)
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState<{success: boolean; message: string} | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const refreshStatus = () => {
    getAlertsStatus()
      .then((response) => {
        if (response && response.success) {
          setStatus({
            configured: response.configured,
            source: response.source,
            chatId: response.chatId,
          })
        }
      })
      .catch(() => {})
  }

  useEffect(refreshStatus, [])

  const handleTestAlert = () => {
    setSending(true)
    setResult(null)
    sendTestAlert()
      .then((response) => {
        setResult({success: response.success, message: response.message})
      })
      .catch(() => {
        setResult({success: false, message: 'Could not reach the server.'})
      })
      .finally(() => setSending(false))
  }

  const handleSave = () => {
    setSaving(true)
    setFormError(null)
    saveAlertsSettings({botToken: botToken.trim(), chatId: chatId.trim()})
      .then((response) => {
        if (response.success) {
          setConfigOpen(false)
          setBotToken('')
          setChatId('')
          setResult({success: true, message: response.message})
          refreshStatus()
        } else {
          setFormError(response.message)
        }
      })
      .catch(() => {
        setFormError('Could not reach the server.')
      })
      .finally(() => setSaving(false))
  }

  const configured = status ? status.configured : null
  const envManaged = status ? status.source === 'env' : false

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <BellRing/>
          Alerts
        </CardTitle>
        {configured !== null && (
          <Tag color={configured ? theme.green : theme.yellow}>
            {configured ? 'Active' : 'Not configured'}
          </Tag>
        )}
      </CardHeader>
      <Row>
        <Stat label="Channel" value="Telegram" size="sm"/>
        <Stat
          label="Chat ID"
          value={status && status.chatId ? status.chatId : '—'}
          size="sm"
        />
        <Stat
          label="Source"
          value={status && status.source ? SOURCE_LABELS[status.source] : '—'}
          size="sm"
        />
        <Stat
          label="Coverage"
          value="Bot stops · position drift · failed orders"
          size="sm"
          color={theme.textDim}
        />
      </Row>
      <Actions>
        <Button
          size="sm"
          variant="primary"
          icon={<Settings2/>}
          disabled={envManaged}
          title={envManaged ? 'Managed through environment variables' : undefined}
          onClick={() => {
            setFormError(null)
            setConfigOpen(true)
          }}
        >
          Configure
        </Button>
        <Button
          size="sm"
          variant="success"
          icon={<Send/>}
          loading={sending}
          disabled={configured === false}
          onClick={handleTestAlert}
        >
          Send test alert
        </Button>
        <Button
          size="sm"
          variant="ghost"
          icon={<BookOpen/>}
          onClick={() => setGuideOpen(true)}
        >
          Setup guide
        </Button>
        {result && (
          <InlineMessage success={result.success}>{result.message}</InlineMessage>
        )}
      </Actions>
      {envManaged && (
        <FormNote style={{marginTop: 12}}>
          Alerts are configured through environment variables, which take
          precedence over settings saved here.
        </FormNote>
      )}
      <Modal
        open={configOpen}
        onClose={() => setConfigOpen(false)}
        width="480px"
        title={
          <>
            <Settings2 size={17} color="var(--accent)"/>
            Configure Telegram alerts
          </>
        }
        footer={
          <>
            <div style={{flex: 1, minWidth: 0}}>
              {formError && <InlineMessage success={false}>{formError}</InlineMessage>}
            </div>
            <div style={{display: 'flex', gap: 10, flexShrink: 0}}>
              <Button variant="ghost" onClick={() => setConfigOpen(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                loading={saving}
                disabled={Boolean(botToken.trim()) !== Boolean(chatId.trim())}
                onClick={handleSave}
              >
                {botToken.trim() || chatId.trim() ? 'Save settings' : 'Clear settings'}
              </Button>
            </div>
          </>
        }
      >
        <FormStack>
          <Field
            label="Bot Token"
            hint={status && status.configured && status.source === 'database'
              ? 'A token is already stored - saving replaces it.'
              : 'From @BotFather, looks like 1234567:AA...'}
          >
            <TextInput
              type="password"
              value={botToken}
              placeholder="1234567:AA..."
              autoComplete="off"
              onChange={(event) => setBotToken(event.target.value)}
            />
          </Field>
          <Field label="Chat ID" hint="Your numeric Telegram chat id (e.g. from @userinfobot)">
            <TextInput
              value={chatId}
              placeholder="987654321"
              autoComplete="off"
              onChange={(event) => setChatId(event.target.value)}
            />
          </Field>
          <FormNote>
            The token is stored on the server and never shown again in the
            dashboard. Leave both fields empty and save to clear the stored
            settings. See the setup guide for how to create the bot and find
            your chat id.
          </FormNote>
        </FormStack>
      </Modal>
      <Modal
        open={guideOpen}
        onClose={() => setGuideOpen(false)}
        width="560px"
        title={
          <>
            <BellRing size={17} color="var(--accent)"/>
            Set up Telegram alerts
          </>
        }
        footer={
          <div style={{display: 'flex', justifyContent: 'flex-end', width: '100%'}}>
            <Button variant="secondary" onClick={() => setGuideOpen(false)}>
              Done
            </Button>
          </div>
        }
      >
        <GuideList>
          <li>
            <strong>Create a bot.</strong> In Telegram, open <code>@BotFather</code>,
            send <code>/newbot</code> and follow the prompts. Copy the <strong>bot
            token</strong> it gives you (looks like <code>1234567:AA...</code>).
          </li>
          <li>
            <strong>Start a chat with your bot.</strong> Open the bot&apos;s profile
            and press <strong>Start</strong> (or send it any message) — bots can
            only message people who have messaged them first.
          </li>
          <li>
            <strong>Find your chat ID.</strong> Visit{' '}
            <code>api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</code> in a browser
            (with your token in the URL) and read the number at{' '}
            <code>"chat": {'{'}"id": ...{'}'}</code>. Alternatively, message{' '}
            <code>@userinfobot</code> and it replies with your ID.
          </li>
          <li>
            <strong>Save the credentials.</strong> Press <strong>Configure</strong> on
            this page and paste the bot token and chat ID. (Alternatively, set the{' '}
            <code>TELEGRAM_BOT_TOKEN</code> and <code>TELEGRAM_CHAT_ID</code>{' '}
            environment variables — those take precedence when present.)
          </li>
          <li>
            <strong>Verify.</strong> The badge should read <strong>Active</strong> —
            press <strong>Send test alert</strong> to confirm a message arrives.
          </li>
        </GuideList>
        <GuideNote>
          The token is a secret: it is stored server-side and never sent back to
          the browser. Alerts cover pipeline stops and deactivations, position
          mismatches, failed or unconfirmed orders, restarts, and unreachable
          services or workers.
        </GuideNote>
      </Modal>
    </Card>
  )
}

export default AlertsCard
