import styled from 'styled-components'
import AlertsCard from './AlertsCard'


const Panel = styled.div`
  width: 100%;
  max-width: 760px;
  animation: fadeUp 0.35s ease both;
`

const AlertsPanel = () => (
  <Panel>
    <AlertsCard/>
  </Panel>
)

export default AlertsPanel
