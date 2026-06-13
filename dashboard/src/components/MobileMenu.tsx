import {Fragment, useState} from 'react'
import styled from "styled-components";
import {Menu as MenuIcon, X} from 'lucide-react'
import {MenuOption, UpdateMessage} from "../types";
import AppMenu from "./Menu";


export const MOBILE_TOPBAR_HEIGHT = 56

const TopBar = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: ${MOBILE_TOPBAR_HEIGHT}px;
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: rgba(10, 14, 21, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
`

const TopBarBrand = styled.span`
  font-family: var(--font-ui);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--text);

  em {
    font-style: normal;
    color: var(--accent);
  }
`

const IconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-raised);
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    color: var(--text);
    border-color: var(--border-strong);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`

const Drawer = styled.div`
  position: fixed;
  inset: 0;
  z-index: 600;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.18s ease;
`

const DrawerHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 12px 16px 0;
`

const DrawerBody = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 8px 16px;
`

interface Props {
  menuOption: MenuOption | undefined
  menuProperties: MenuOption[]
  removeToken: () => void
  updateMessage: UpdateMessage
}

function MobileMenu(props: Props) {

  const { menuOption, menuProperties, removeToken, updateMessage } = props

  const [open, setOpen] = useState(false)

  return (
    <Fragment>
      <TopBar>
        <TopBarBrand>
          MyCrypto<em>Bot</em>
        </TopBarBrand>
        <IconButton onClick={() => setOpen(true)} aria-label="Open menu">
          <MenuIcon/>
        </IconButton>
      </TopBar>
      {open && (
        <Drawer>
          <DrawerHeader>
            <IconButton onClick={() => setOpen(false)} aria-label="Close menu">
              <X/>
            </IconButton>
          </DrawerHeader>
          <DrawerBody>
            <AppMenu
              menuOption={menuOption}
              menuProperties={menuProperties}
              removeToken={removeToken}
              updateMessage={updateMessage}
              onNavigate={() => setOpen(false)}
            />
          </DrawerBody>
        </Drawer>
      )}
    </Fragment>
  );
}

export default MobileMenu;
