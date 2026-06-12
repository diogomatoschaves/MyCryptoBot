import styled from 'styled-components'
import {Link} from 'react-router-dom'
import {Activity, ArrowLeftRight, Bell, Bot, Layers, LogOut} from 'lucide-react'
import {MenuOption, UpdateMessage} from "../types";


const NAV_ICONS: Record<string, React.ComponentType<any>> = {
  '/dashboard': Activity,
  '/pipelines': Bot,
  '/positions': Layers,
  '/trades': ArrowLeftRight,
  '/alerts': Bell,
}

const Nav = styled.nav`
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px 14px;
`

const Brand = styled(Link)`
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px 12px 28px;
`

const BrandName = styled.span`
  font-family: var(--font-ui);
  font-size: 17px;
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
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text-faint);

  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulseGlow 2.4s ease infinite;
  }
`

const NavList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
`

const NavItem = styled(Link)<{$active?: boolean}>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 12px;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: ${({$active}) => ($active ? 700 : 500)};
  color: ${({$active}) => ($active ? 'var(--accent)' : 'var(--text-dim)')};
  background: ${({$active}) => ($active ? 'var(--accent-dim)' : 'transparent')};
  transition: all 0.15s ease;

  &:hover {
    color: ${({$active}) => ($active ? 'var(--accent)' : 'var(--text)')};
    background: ${({$active}) => ($active ? 'var(--accent-dim)' : 'rgba(255, 255, 255, 0.04)')};
  }

  svg {
    width: 17px;
    height: 17px;
    flex-shrink: 0;
  }
`

const LogoutButton = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 12px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  font-family: var(--font-ui);
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-faint);
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;

  &:hover {
    color: var(--red);
    background: var(--red-dim);
  }

  svg {
    width: 17px;
    height: 17px;
  }
`

interface Props {
  menuOption: MenuOption | undefined
  menuProperties: MenuOption[]
  removeToken: () => void
  updateMessage: UpdateMessage
  onNavigate?: () => void
}


function AppMenu(props: Props) {

  const { menuOption, menuProperties, removeToken, updateMessage, onNavigate } = props

  const logout = () => {
    updateMessage({
      text: "You're logged out.",
      success: true
    })
    removeToken()
  }

  return (
    <Nav>
      <Brand to="/dashboard" onClick={onNavigate}>
        <BrandName>
          MyCrypto<em>Bot</em>
        </BrandName>
        <BrandSub>Trading Terminal</BrandSub>
      </Brand>
      <NavList>
        {menuProperties.map((menuItem) => {
          const Icon = NAV_ICONS[menuItem.code] || Activity
          return (
            <NavItem
              key={menuItem.code}
              to={menuItem.code}
              $active={menuOption && menuOption.code === menuItem.code}
              onClick={onNavigate}
            >
              <Icon/>
              {menuItem.text}
            </NavItem>
          )
        })}
      </NavList>
      <LogoutButton onClick={logout}>
        <LogOut/>
        Logout
      </LogoutButton>
    </Nav>
  );
}

export default AppMenu;
