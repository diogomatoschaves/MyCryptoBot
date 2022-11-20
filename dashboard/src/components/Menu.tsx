import styled from "styled-components";
import {Grid, Menu} from "semantic-ui-react";
import {Link} from 'react-router-dom'
import {ChangeMenu, MenuOption} from "../types";


interface Props {
    menuOption: MenuOption | undefined
    changeMenu: ChangeMenu
    menuProperties: MenuOption[]
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

    const { menuOption, menuProperties } = props

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