import {Button, Dropdown, Grid, Divider, TextArea, Form} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {ActivePipeline, DropdownOptions, StartPipeline, StopPipeline} from "../types";
import Pipeline from './Pipeline'
import {useState} from "react";


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    activePipelines: ActivePipeline[];
    startPipeline: StartPipeline;
    stopPipeline: StopPipeline
}


const validatePipelineCreation = ({
    symbol,
    symbolsOptions,
    strategy,
    strategiesOptions,
    candleSize,
    candleSizeOptions,
    exchanges,
    exchangeOptions,
    startPipeline
}: {
    symbol: number | undefined,
    symbolsOptions: DropdownOptions[],
    strategy: number | undefined,
    strategiesOptions: DropdownOptions[],
    candleSize: number | undefined,
    candleSizeOptions: DropdownOptions[],
    exchanges: Array<number>,
    exchangeOptions: DropdownOptions[],
    startPipeline: StartPipeline
}) => {
    if (!symbol || !strategy || !candleSize || exchanges.length == 0) {
        console.log("All parameters must be specified")
        return
    }

    startPipeline({
        // @ts-ignore
        symbol: symbolsOptions.find(option => symbol === option.value).text,
        // @ts-ignore
        strategy: strategiesOptions.find(option => strategy === option.value).text,
        // @ts-ignore
        candleSize: candleSizeOptions.find(option => candleSize === option.value).text,
        // @ts-ignore
        exchanges: exchangeOptions.find(option => exchanges[0] === option.value).text, // TODO: Generalize this for any number of exchanges
    })

}


function PipelinePanel(props: Props) {

    const {
        symbolsOptions,
        strategiesOptions,
        activePipelines,
        candleSizeOptions,
        exchangeOptions,
        startPipeline,
        stopPipeline
    } = props

    const [symbol, setSymbol] = useState()
    const [strategy, setStrategy] = useState()
    const [candleSize, setCandleSize] = useState()
    const [exchanges, setExchange] = useState([])

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
                            value={exchanges}
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
                        <Button
                            onClick={() =>
                                validatePipelineCreation({
                                    symbol,
                                    strategy,
                                    candleSize,
                                    exchanges,
                                    symbolsOptions,
                                    strategiesOptions,
                                    candleSizeOptions,
                                    exchangeOptions,
                                    startPipeline
                                })
                            }
                            color='green'
                        >
                            Start Pipeline
                        </Button>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
            <Divider horizontal style={{marginTop: '30px'}}>Active Pipelines</Divider>
            {activePipelines.map((pipeline: ActivePipeline) => <Pipeline stopPipeline={stopPipeline} {...pipeline}/>)}
        </StyledSegment>
    );
}

export default PipelinePanel;
