import {Fragment} from 'react'
import styled from "styled-components";
import {Grid, Icon} from "semantic-ui-react";
import {MenuOption, UpdateMessage} from "../types";
import AppMenu from "./Menu";
import MobileMenu from "./MobileMenu";


interface Props {
    size: string
    menuOption: MenuOption | undefined
    menuProperties: MenuOption[]
    removeToken: () => void
    updateMessage: UpdateMessage
}


const Column = styled(Grid.Column)`
    height: 100%;
    flex-direction: column;
    justify-content: flex-start;
    padding: 20px;
    background-color: rgb(215, 215, 215);
    box-shadow: 0px 0px 5px 3px rgba(0, 0, 0, 0.2);
`

const MenuColumn = styled.div`
    position: fixed;
    left: 0;
    bottom: 0;
    top: 0;
    width: 25vw;
    max-width: 300px;
`


function MenuWrapper(props: Props) {

    const { size, menuOption, menuProperties, removeToken, updateMessage } = props

    return (
      <Fragment>
          {(size !== 'mobile' && size !== 'tablet') ? (
            <MenuColumn>
                <Column width={4} visible={false}>
                    <AppMenu
                      menuOption={menuOption}
                      menuProperties={menuProperties}
                      removeToken={removeToken}
                      updateMessage={updateMessage}
                    />
                </Column>
            </MenuColumn>
          ) : (
            <MobileMenu
              menuOption={menuOption}
              menuProperties={menuProperties}
              removeToken={removeToken}
              updateMessage={updateMessage}
            />
          )}
      </Fragment>


    );
}

export default MenuWrapper;
