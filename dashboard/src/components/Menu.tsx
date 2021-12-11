import styled from "styled-components";
import {Menu} from "semantic-ui-react";
import {ChangeMenu, MenuOption} from "../types";


interface Props {
    menuOption: MenuOption
    changeMenu: ChangeMenu
}


const Column = styled.div`
    height: 100%;
    width: 25%;
    flex-direction: column;
    justify-content: flex-start;
    padding: 20px;
    background-color: rgb(215, 215, 215);
    box-shadow: 0px 0px 5px 3px rgba(0, 0, 0, 0.2);
`

const menuProperties = [
    {icon: 'line graph', emoji: '📈', text: 'Balance', code: "balance"},
    {icon: 'play', emoji: '🤖', text: 'Trading Bots', code: "pipelines"},
    {icon: 'list', emoji: '📒', text: 'Positions', code: "positions"},
    {icon: 'dollar', emoji: '💵', text: 'Transactions', code: "transactions"},
]


function AppMenu(props: Props) {

    const { changeMenu, menuOption } = props

    return (
        <Column>
            <Menu style={{paddingTop: '40px'}} secondary vertical>
                {menuProperties.map(menuItem => (
                    <Menu.Item
                        style={styles}
                        onClick={() => changeMenu(menuItem)}
                        active={menuOption.code === menuItem.code}
                    >
                        <div className="flex-row" style={{justifyContent: 'space-between'}}>
                            <span>{menuItem.text}</span>
                            <span>{menuItem.emoji}</span>
                        </div>
                    </Menu.Item>
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