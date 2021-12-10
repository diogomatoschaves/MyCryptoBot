import styled from "styled-components";
import {List} from "semantic-ui-react";
import {ChangeMenu} from "../types";


interface Props {
    changeMenu: ChangeMenu
}


const Column = styled.div`
    height: 100%;
    width: 25%;
    flex-direction: column;
    justify-content: flex-start;
    padding: 20px;
    //background-color: rgb(43, 105, 122);
    background-color: rgb(215, 215, 215);
    box-shadow: 0px 0px 5px 3px rgba(0, 0, 0, 0.2);
`

const menuProperties = [
    {icon: 'line graph', text: 'Balance', menuOption: "balance"},
    {icon: 'play', text: 'Trading Bots', menuOption: "pipelines"},
    {icon: 'list', text: 'Positions', menuOption: "positions"},
    {icon: 'dollar', text: 'Transactions', menuOption: "orders"},
]


function AppMenu(props: Props) {

    const { changeMenu } = props

    return (
        <Column>
            <List style={{paddingTop: '40px'}}>
                {menuProperties.map(menuItem => (
                    <List.Item as='a' style={styles} onClick={() => changeMenu(menuItem.menuOption)}>
                        {/*@ts-ignore*/}
                        <List.Icon name={menuItem.icon} />
                        <List.Content>{menuItem.text}</List.Content>
                    </List.Item>
                ))}
            </List>
        </Column>
    );
}

export default AppMenu;


const styles = {
    fontSize: '1.2em',
    paddingBottom: '20px',
    color: 'rgb(57, 57, 57)',
    fontWeight: 'bold',
}