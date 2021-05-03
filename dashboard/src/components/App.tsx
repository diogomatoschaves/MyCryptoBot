import '../App.css';
import {Component} from 'react'
import styled from 'styled-components'
import {Header} from "semantic-ui-react";
import ControlPanel from "./ControlPanel";
import {ActivePipeline, DropdownOptions, Order} from "../types";
import OrderCard from "./Order";


const AppDiv = styled.div`
  text-align: center;
  width: 100vw;
  height: 100vh;
  position: absolute;
  justify-content: flex-start;
  padding: 20px;
`

interface State {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    orders: Order[];
    activePipelines: ActivePipeline[]
}


class App extends Component<any, State> {

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        orders: [],
        activePipelines: []
    }

    componentDidMount() {
        let orders = require('../apiCalls/mock_orders.json')

        orders = [0, 1, 2, 3, 4].reduce((accum: Order[], item: Number) => {
            return [...accum, orders[0]]
        }, [])

        const activePipelines = [{
            symbol: 'BTCUSDT',
            strategy: 'MovingAverageCrossover',
            params: {"sma_s": 12, "sma_l": 30},
            candleSize: '1h',
            exchange: 'Binance'
        }] as any

        this.setState({orders, activePipelines})
    }

    render(){

        const { symbolsOptions, strategiesOptions, orders, activePipelines } = this.state

        return (
            <AppDiv className="flex-column">
                <Header size='huge' style={{marginBottom: '20px'}}>Crypto Bot Dashboard</Header>
                <ControlPanel
                    symbolsOptions={symbolsOptions}
                    strategiesOptions={strategiesOptions}
                    orders={orders}
                    activePipelines={activePipelines}
                />
            </AppDiv>
        );
    }
}

export default App;
