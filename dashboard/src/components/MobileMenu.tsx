import {Fragment, useState} from 'react'
import styled from "styled-components";
import {Icon} from "semantic-ui-react";
import {MenuOption, UpdateMessage} from "../types";
import AppMenu from "./Menu";


interface Props {
  menuOption: MenuOption | undefined
  menuProperties: MenuOption[]
  removeToken: () => void
  updateMessage: UpdateMessage
}

const MenuIcon = styled.div`
    position: absolute;
    right: 20px;
    top: 20px;
    z-index: 100;
`

const FullPage = styled.div`
    width: 100vw;
    height: 100vh;
    background-color: white;
    z-index: 100;
`

const FlexyDiv = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`

function MenuWrapper(props: Props) {

  const { menuOption, menuProperties, removeToken, updateMessage } = props

  const [mobileMenuVisible, setMobileMenuVisibility] = useState(false)

  return (
    <Fragment>
      {!mobileMenuVisible ? (
        <MenuIcon onClick={() => setMobileMenuVisibility(true)}>
          <Icon color='grey' name={'th'} size={'big'}/>
        </MenuIcon>
      ) : (
          <FullPage>
            {/*<Transition.Group animation={'slide down'} duration={500}>*/}
            <MenuIcon onClick={() => setMobileMenuVisibility(false)}>
              <Icon color='grey' name={'close'} size={'big'}/>
            </MenuIcon>
            <FlexyDiv>
              <AppMenu
                size={'massive'}
                setMobileMenuVisibility={setMobileMenuVisibility}
                menuOption={menuOption}
                menuProperties={menuProperties}
                removeToken={removeToken}
                updateMessage={updateMessage}
              />
            </FlexyDiv>
          {/*</Transition.Group>*/}
        </FullPage>
      )}
    </Fragment>
  );
}

export default MenuWrapper;
