import {Divider, Icon, Menu} from "semantic-ui-react";
import {Link} from 'react-router-dom'
import {MenuOption, UpdateMessage} from "../types";
import {useEffect, useRef} from "react";


interface Props {
  size?: string
  menuOption: MenuOption | undefined
  menuProperties: MenuOption[]
  removeToken: () => void
  updateMessage: UpdateMessage
  setMobileMenuVisibility?: (toggle: boolean) => void
}


function AppMenu(props: Props) {

  const { size, menuOption, menuProperties, removeToken, updateMessage } = props

  const logout = () => {
    updateMessage({
      text: "You're logged out.",
      success: true
    })
    removeToken()
  }

  const previous = useRef({menuOption}).current;

  useEffect(() => {

    const {setMobileMenuVisibility, menuOption} = props

    if (previous.menuOption !== menuOption) {
      setMobileMenuVisibility && setMobileMenuVisibility(false)
    }

    return () => {
      previous.menuOption = menuOption
    };
  }, [menuOption]);

  return (
    <Menu style={{paddingTop: '50px', width: size ? '70%' : undefined}} secondary vertical size={size as any}>
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
  );
}

export default AppMenu;


const styles = {
  fontSize: '1.1em',
  padding: '15px',
  color: 'rgb(57, 57, 57)',
  fontWeight: 'bold',
}