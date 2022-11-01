import {Button, Divider, Header, Message} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {
    DropdownOptions,
    StartPipeline,
    StopPipeline,
    Pipeline,
    MenuOption,
    UpdateMessage,
    DeletePipeline
} from "../types";
import PipelineItem from './Pipeline'
import NewPipeline from "./NewPipeline";
import styled from "styled-components";
import {useEffect, useReducer, useRef} from "react";


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    pipelines: Pipeline[];
    startPipeline: StartPipeline;
    stopPipeline: StopPipeline;
    deletePipeline: DeletePipeline;
    updateMessage: UpdateMessage;
    menuOption: MenuOption;
    strategies: any
}


const ButtonWrapper = styled.div`
    margin-bottom: 40px;
    width: 100%;
    justify-content: space-around;
`

const FILTER_PIPELINES = 'FILTER_PIPELINES'
const TOGGLE_OPTIONS = 'TOGGLE_OPTIONS'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_PIPELINES:
            const { pipelines, options: {active, stopped, live, test} } = action

            return {
                ...state,
                filteredPipelines: pipelines.filter((pipeline: Pipeline) => {
                    return ((pipeline.active === active && active) || (pipeline.active === !stopped && stopped))
                    && ((pipeline.paperTrading === test && test) || (pipeline.paperTrading === !live && live))
                })
            }
        case TOGGLE_OPTIONS:
            return {
                ...state,
                options: {
                    live: action.live !== undefined ? action.live : state.options.live,
                    test: action.test !== undefined ? action.test : state.options.test,
                    active: action.active !== undefined ? action.active : state.options.active,
                    stopped: action.stopped !== undefined ? action.stopped : state.options.stopped,
                }
            }
        default:
            throw new Error();
    }
}


const initialOptions = {
    live: true,
    test: true,
    active: true,
    stopped: true
}

function PipelinePanel(props: Props) {

    const {
        symbolsOptions,
        strategiesOptions,
        pipelines,
        strategies,
        candleSizeOptions,
        exchangeOptions,
        startPipeline,
        stopPipeline,
        deletePipeline,
        updateMessage,
        menuOption
    } = props

    const [
        {
            filteredPipelines,
            options
        }, dispatch
    ] = useReducer(
        reducer, {
            filteredPipelines: pipelines,
            options: initialOptions
        }
    );

    const previous = useRef({ pipelines, options }).current;

    useEffect(() => {
        if (pipelines !== previous.pipelines || options !== previous.options) {
            dispatch({
                type: FILTER_PIPELINES,
                pipelines,
                options
            })
        }
        return () => {
            previous.pipelines = pipelines
            previous.options = options
        };
    }, [pipelines, options]);

    return (
        <StyledSegment basic className="flex-column">
            <Header size={'large'} dividing>
                <span style={{marginRight: 10}}>{menuOption.emoji}</span>
                {menuOption.text}
            </Header>
            <ButtonWrapper className="flex-row">
                <Button.Group size="mini" style={{alignSelf: 'center'}}>
                    {['live', 'test'].map((option, index) => (
                        <Button key={index} onClick={() => dispatch({
                            type: TOGGLE_OPTIONS,
                            [option]: !options[option]
                        })} color={options && options[option] && 'grey'}>
                            {option}
                        </Button>
                    ))}
                </Button.Group>
                <Button.Group size="mini" style={{alignSelf: 'center'}}>
                    {['active', 'stopped'].map((option, index) => (
                      <Button key={index} onClick={() => dispatch({
                          type: TOGGLE_OPTIONS,
                          [option]: !options[option]
                      })} color={options && options[option] && 'grey'}>
                          {option}
                      </Button>
                    ))}
                </Button.Group>
                <NewPipeline
                    strategies={strategies}
                    symbolsOptions={symbolsOptions}
                    strategiesOptions={strategiesOptions}
                    candleSizeOptions={candleSizeOptions}
                    exchangeOptions={exchangeOptions}
                    startPipeline={startPipeline}
                    updateMessage={updateMessage}
                />
            </ButtonWrapper>
            {filteredPipelines.map((pipeline: Pipeline, index: number) => (
                <PipelineItem
                    key={index}
                    startPipeline={startPipeline}
                    stopPipeline={stopPipeline}
                    deletePipeline={deletePipeline}
                    pipeline={pipeline}
                />
            ))}
            {filteredPipelines.length === 0 && (
                <Message>
                    <Message.Header>
                        There are no trading bots matching the chosen filters.
                    </Message.Header>
                </Message>
            )}
        </StyledSegment>
    );
}

export default PipelinePanel;
