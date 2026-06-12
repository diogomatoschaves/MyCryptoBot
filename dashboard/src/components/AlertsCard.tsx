import {useEffect, useState} from 'react'
import styled from 'styled-components'
import {BellRing, BookOpen, Send} from 'lucide-react'
import {getAlertsStatus, sendTestAlert} from '../apiCalls'
import {Button, Card, CardHeader, CardTitle, InlineMessage, Modal, Stat, Tag} from '../ui'
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
  chatId: string | null
}

const AlertsCard = () => {

  const [status, setStatus] = useState<AlertsStatus | null>(null)
  const [guideOpen, setGuideOpen] = useState(false)
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState<{success: boolean; message: string} | null>(null)

  useEffect(() => {
    getAlertsStatus()
      .then((response) => {
        if (response && response.success) {
          setStatus({configured: response.configured, chatId: response.chatId})
        }
      })
      .catch(() => {})
  }, [])

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

  const configured = status ? status.configured : null

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
        <Stat
          label="Channel"
          value="Telegram"
          size="sm"
        />
        <Stat
          label="Chat ID"
          value={status && status.chatId ? status.chatId : '—'}
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
            <strong>Configure the services.</strong> Set{' '}
            <code>TELEGRAM_BOT_TOKEN</code> and <code>TELEGRAM_CHAT_ID</code> as
            environment variables (in your <code>.env</code> file for
            docker-compose, or in your deployment&apos;s config), then restart the
            services.
          </li>
          <li>
            <strong>Verify.</strong> Reload this page — the badge should read{' '}
            <strong>Active</strong> — and press <strong>Send test alert</strong>.
          </li>
        </GuideList>
        <GuideNote>
          The token is a secret: it is only ever read from the server&apos;s
          environment and is never stored in the database or shown in this
          dashboard. Alerts cover pipeline stops and deactivations, position
          mismatches, failed or unconfirmed orders, restarts, and unreachable
          services or workers.
        </GuideNote>
      </Modal>
    </Card>
  )
}

export default AlertsCard
