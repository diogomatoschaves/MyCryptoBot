import {Button, Dropdown, Grid, Divider, TextArea, Form} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {ActivePipeline, DropdownOptions} from "../types";
import Pipeline from './Pipeline'
import {useState} from "react";


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    activePipelines: ActivePipeline[]
}

function PipelinePanel(props: Props) {

    const {
        symbolsOptions,
        strategiesOptions,
        activePipelines,
        candleSizeOptions,
        exchangeOptions
    } = props

    const [symbol, setSymbol] = useState()
    const [strategy, setStrategy] = useState()
    const [candleSize, setCandleSize] = useState()
    const [exchange, setExchange] = useState([])

    return (
        <StyledSegment basic className="flex-column">
            <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>Bot Control Panel</Divider>
            <Grid columns={2}>
                <Grid.Row>
                    <Grid.Column>
                        <Dropdown
                            placeholder='Symbol'
                            value={symbol}
                            onChange={(e: any, {value}: {value?: any}) => setSymbol(value)}
                            search
                            selection
                            options={symbolsOptions}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <Dropdown
                            placeholder='Strategy'
                            value={strategy}
                            onChange={(e: any, {value}: {value?: any}) => setStrategy(value)}
                            search
                            selection
                            options={strategiesOptions}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                    <Grid.Column>
                        <Dropdown
                            placeholder='Candle size'
                            value={candleSize}
                            onChange={(e: any, {value}: {value?: any}) => setCandleSize(value)}
                            search
                            selection
                            options={candleSizeOptions}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <Dropdown
                            placeholder='Exchange'
                            value={exchange}
                            onChange={(e: any, {value}: {value?: any}) => setExchange(value)}
                            multiple
                            search
                            selection
                            options={exchangeOptions}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                    <Grid.Column>
                        {/*<Form>*/}
                        {/*    <TextArea placeholder='Params'/>*/}
                        {/*</Form>*/}
                    </Grid.Column>
                    <Grid.Column style={{alignSelf: 'center'}}>
                        <Button color='green'>Start Pipeline</Button>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
            <Divider horizontal style={{marginTop: '30px'}}>Active Pipelines</Divider>
            {activePipelines.map(pipeline => <Pipeline pipeline={pipeline}/>)}
        </StyledSegment>
    );
}

export default PipelinePanel;
