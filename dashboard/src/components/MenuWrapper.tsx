import styled from "styled-components";
import {MenuOption, UpdateMessage} from "../types";
import AppMenu from "./Menu";
import MobileMenu from "./MobileMenu";


export const SIDEBAR_WIDTH = 240

const Sidebar = styled.aside`
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: ${SIDEBAR_WIDTH}px;
  z-index: 400;
  background: var(--bg-raised);
  border-right: 1px solid var(--border);
`

interface Props {
    size: string
    menuOption: MenuOption | undefined
    menuProperties: MenuOption[]
    removeToken: () => void
    updateMessage: UpdateMessage
}


function MenuWrapper(props: Props) {

    const { size, menuOption, menuProperties, removeToken, updateMessage } = props

    const compact = size === 'mobile' || size === 'tablet'

    return compact ? (
      <MobileMenu
        menuOption={menuOption}
        menuProperties={menuProperties}
        removeToken={removeToken}
        updateMessage={updateMessage}
      />
    ) : (
      <Sidebar>
        <AppMenu
          menuOption={menuOption}
          menuProperties={menuProperties}
          removeToken={removeToken}
          updateMessage={updateMessage}
        />
      </Sidebar>
    );
}

export default MenuWrapper;
