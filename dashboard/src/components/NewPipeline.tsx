import React, {useReducer, useState} from 'react';
import {Button, Checkbox, Dropdown, Form, Grid, Header, Icon, Input, Modal, TextArea} from "semantic-ui-react";
import {DropdownOptions, StartPipeline, UpdateMessage} from "../types";
import {validateParams, validatePipelineCreation} from "../utils/helpers";
import MessageComponent from "./Message";
import {COLORS_NAMES} from "../utils/constants";


interface Props {
  symbolsOptions: DropdownOptions[];
  strategiesOptions: DropdownOptions[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  startPipeline: StartPipeline;
  updateMessage: UpdateMessage;
  strategies: any;
}


const colorOptions = COLORS_NAMES.map((colorName, index) => {
  const name = colorName.toLowerCase()
  return {
    key: name,
    text: name,
    value: name,
    label: { className: `light-${name}`, empty: true, circular: true}
  }
})


const UPDATE_STRATEGY = 'UPDATE_STRATEGY'
const UPDATE_SECOND_MODAL_OPEN = 'UPDATE_SECOND_MODAL_OPEN'
const CLOSE_MODAL = 'CLOSE_MODAL'
const UPDATE_PARAMS = 'UPDATE_PARAMS'
const UPDATE_CHECKBOX = 'UPDATE_CHECKBOX'
const UPDATE_MESSAGE = 'UPDATE_MESSAGE'


const reducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_STRATEGY:
      return {
        ...state,
        secondModalOpen: action.value && state.strategy !== action.value,
        strategy: action.value
      }
    case UPDATE_SECOND_MODAL_OPEN:
      return {
        ...state,
        secondModalOpen: action.value,
      }
    case CLOSE_MODAL:
      return {
        ...state,
        strategy: undefined,
        secondModalOpen: false,
        params: {},
        liveTrading: false,
        message: {text: '', success: false}
      }
    case UPDATE_PARAMS:
      return {
        ...state,
        params: {
          ...state.params,
          ...action.value
        },
      }
    case UPDATE_CHECKBOX:
      return {
        ...state,
        liveTrading: !state.liveTrading
      }
    case UPDATE_MESSAGE:
      return {
        ...state,
        message: action.message
      }
    default:
      throw new Error();
  }
}



const NewPipeline = (props: Props) => {

  const {
    symbolsOptions,
    strategiesOptions,
    candleSizeOptions,
    exchangeOptions,
    startPipeline,
    strategies
  } = props

  const [open, setOpen] = useState(false)

  const [color, setColor] = useState()
  const [symbol, setSymbol] = useState()
  const [candleSize, setCandleSize] = useState()
  const [name, setName] = useState()
  const [allocation, setAllocation] = useState()
  const [exchanges, setExchange] = useState([])

  const [{strategy, secondModalOpen, params, liveTrading, message}, dispatch] = useReducer(
      reducer, {
        strategy: undefined,
        secondModalOpen: false,
        params: {},
        liveTrading: false,
        message: {text: '', success: false}
      }
  );

  return (
      <Modal
          closeIcon
          onClose={() => {
            // @ts-ignore
            setExchange(undefined)
            // @ts-ignore
            setSymbol(undefined)
            // @ts-ignore
            setColor(undefined)
            dispatch({type: CLOSE_MODAL})
            // @ts-ignore
            setCandleSize(undefined)
            setOpen(false)
          }}
          onOpen={() => setOpen(true)}
          open={open}
          size="small"
          trigger={
            <Button inverted secondary>
              <span style={{marginRight: '10px'}}>
                  <Icon name={'plus'}/>
              </span>
              New Trading Bot
            </Button>
          }
      >
        <Modal.Header>New Trading Bot <span>🤖</span></Modal.Header>
        <Modal.Content >
          <Grid columns={2}>
            <Grid.Row >
              <Grid.Column>
                <Input
                    placeholder='Name'
                    value={name}
                    onChange={(e: any, {value}: {value?: any}) => setName(value)}
                />
              </Grid.Column>
              <Grid.Column>
                <Input
                    placeholder='Allocated capital'
                    value={allocation}
                    onChange={(e: any, {value}: {value?: any}) => setAllocation(value)}
                />
              </Grid.Column>
            </Grid.Row>
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
                    placeholder='Candle size'
                    value={candleSize}
                    onChange={(e: any, {value}: {value?: any}) => setCandleSize(value)}
                    search
                    selection
                    options={candleSizeOptions}
                />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
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
              <Grid.Column>
                <Dropdown
                    placeholder='Strategy'
                    value={strategy}
                    onChange={(e: any, {value}: {value?: any}) => dispatch({
                      type: UPDATE_STRATEGY,
                      value,
                    })}
                    search
                    selection
                    options={strategiesOptions}
                />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
              <Grid.Column>
                <Checkbox
                  label={'📡 Live trading'}
                  onChange={() => dispatch({type: UPDATE_CHECKBOX})}
                  checked={liveTrading}
                />
              </Grid.Column>
              <Grid.Column>
                <Dropdown
                    className={`light-${color}`}
                    placeholder='Color'
                    value={color}
                    onChange={(e: any, entry: any) => setColor(entry.value)}
                    selection
                    options={colorOptions}
                />
              </Grid.Column>
            </Grid.Row>
            <Modal
              onClose={() => {
                dispatch({type: CLOSE_MODAL})
              }}
              open={strategy && secondModalOpen}
              size="small"
            >
              <Modal.Header>{strategy && strategiesOptions[strategy - 1].text}</Modal.Header>
              <Modal.Content scrolling>
                {strategy && (
                  <Grid columns={2}>
                    <Grid.Column>
                      <Header as='h5'>Required:</Header>
                      {strategy &&  strategies[strategiesOptions[strategy - 1].text].params.map((param: string) => (
                        <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                          <Grid.Column>
                            <Input
                              onChange={(e, {value}) => {
                                dispatch({
                                  type: UPDATE_PARAMS,
                                  value: {
                                    [param]: value
                                  }
                                })
                              }}
                              placeholder={param}/>
                          </Grid.Column>
                        </Grid.Row>
                      ))}
                    </Grid.Column>
                    <Grid.Column>
                      <Header as='h5'>Optional:</Header>
                      {/*@ts-ignore*/}
                      {strategies[strategiesOptions[strategy - 1].text].optional_params.map(param => (
                        <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                          <Grid.Column>
                            <Input
                              onChange={(e, {value}) => {
                                dispatch({
                                  type: UPDATE_PARAMS,
                                  value: {
                                    [param]: value
                                  }
                                })
                              }}
                              placeholder={param}/>
                          </Grid.Column>
                        </Grid.Row>
                      ))}
                    </Grid.Column>
                  </Grid>
                )}
              </Modal.Content>
              <Modal.Actions>
                <Button
                    icon='check'
                    content='Validate'
                    onClick={() => {
                      new Promise((resolve, reject) => {
                        validateParams(
                            resolve,
                            reject,
                            params,
                            strategies[strategiesOptions[strategy - 1].text]
                        )
                      })
                        .then(() => {
                          dispatch({
                            type: UPDATE_SECOND_MODAL_OPEN,
                            value: false
                          })
                        })
                        .catch(() => {})
                    }}
                />
              </Modal.Actions>
            </Modal>
          </Grid>
        </Modal.Content>
        <Modal.Actions>
          <div className="flex-row" style={{justifyContent: message.text ? 'space-between' : 'flex-end'}}>
            {message.text && (
                <div>
                  <Grid.Row>
                    <Grid.Column>
                      <MessageComponent success={message.success} message={message.text}/>
                    </Grid.Column>
                  </Grid.Row>
                </div>
            )}
            <div>
              <Button color='black' onClick={() => {
                // @ts-ignore
                setExchange(undefined)
                // @ts-ignore
                setSymbol(undefined)
                // @ts-ignore
                dispatch({
                  type: CLOSE_MODAL,
                })
                // @ts-ignore
                setColor(undefined)
                // @ts-ignore
                setCandleSize(undefined)
                setOpen(false)
              }}>
                Cancel
              </Button>
              <Button
                  content="Create trading bot"
                  labelPosition='right'
                  icon='checkmark'
                  onClick={async () => {
                    const success = await validatePipelineCreation({
                      name,
                      allocation,
                      color,
                      symbol,
                      strategy,
                      candleSize,
                      exchanges,
                      symbolsOptions,
                      strategiesOptions,
                      candleSizeOptions,
                      exchangeOptions,
                      startPipeline,
                      dispatch,
                      params,
                      liveTrading
                    })
                    if (success) setOpen(false)
                  }}
                  positive
              />
            </div>
          </div>
        </Modal.Actions>
      </Modal>
  );
};

export default NewPipeline;