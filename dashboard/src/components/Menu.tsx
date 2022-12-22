import styled from "styled-components";
import {Divider, Grid, Icon, Menu} from "semantic-ui-react";
import {Link} from 'react-router-dom'
import {MenuOption, UpdateMessage} from "../types";


interface Props {
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

function AppMenu(props: Props) {

    const { menuOption, menuProperties, removeToken, updateMessage } = props

    const logout = () => {
        updateMessage({
            text: "You're logged out.",
            success: true
        })
        removeToken()
    }

    return (
        <Column width={4}>
            <Menu style={{paddingTop: '40px'}} secondary vertical>
                {menuProperties.map(menuItem => (
                  <Link to={menuItem.code}>
                    <Menu.Item
                        style={styles}
                        active={menuOption && menuOption.code === menuItem.code}
                    >
                        <div className="flex-row" style={{justifyContent: 'space-between'}}>
                            <span>{menuItem.text}</span>
                            <span>{menuItem.emoji}</span>
                        </div>
                    </Menu.Item>
                  </Link>
                ))}
                <Divider/>
                <Link to="/login">
                    <Menu.Item style={styles}>
                        <a onClick={logout} className="flex-row" style={{justifyContent: 'space-between'}}>
                            <span>Logout</span>
                            <span><Icon name="log out"/></span>
                        </a>
                    </Menu.Item>
                </Link>
            </Menu>
        </Column>
    );
}

export default AppMenu;


const styles = {
    fontSize: '1.1em',
    padding: '15px',
    color: 'rgb(57, 57, 57)',
    fontWeight: 'bold',
}