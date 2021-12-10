import React, {useEffect, useReducer, useState} from 'react';
import {Button, Dropdown, Grid, Header, Icon, Input, Modal} from "semantic-ui-react";
import {DropdownOptions, StartPipeline} from "../types";
import {validateParams, validatePipelineCreation} from "../utils/helpers";


interface Props {
  symbolsOptions: DropdownOptions[];
  strategiesOptions: DropdownOptions[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  startPipeline: StartPipeline;
  strategies: any;
}


const UPDATE_STRATEGY = 'UPDATE_STRATEGY'
const UPDATE_SECOND_MODAL_OPEN = 'UPDATE_SECOND_MODAL_OPEN'
const CLOSE_MODAL = 'CLOSE_MODAL'
const UPDATE_PARAMS = 'UPDATE_PARAMS'


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
        strategy: null,
        secondModalOpen: false,
        params: {}
      }
    case UPDATE_PARAMS:
      return {
        ...state,
        params: {
          ...state.params,
          ...action.value
        },
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

  const [symbol, setSymbol] = useState()
  const [candleSize, setCandleSize] = useState()
  const [exchanges, setExchange] = useState([])

  const [{strategy, secondModalOpen, params}, dispatch] = useReducer(
      reducer, {strategy: undefined, secondModalOpen: false, params: {}}
  );

  return (
      <Modal
          onClose={() => {
            // @ts-ignore
            setExchange(undefined)
            // @ts-ignore
            setSymbol(undefined)
            // @ts-ignore
            dispatch({
              type: UPDATE_STRATEGY,
              value: undefined,
            })
            // @ts-ignore
            setCandleSize(undefined)
            setOpen(false)
          }}
          onOpen={() => setOpen(true)}
          open={open}
          dimmer={'inverted'}
          trigger={
            <Button>
              <span style={{marginRight: '10px'}}>
                  <Icon name={'plus'}/>
              </span>
              Create Trading Bot
            </Button>
          }
      >
        <Modal.Header>New Trading Bot <span>🤖</span></Modal.Header>
        <Modal.Content >
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
            {/*<Header as='h4'>Strategy Parameters</Header>*/}
            {/*? <Grid.Row>Select a strategy first!</Grid.Row>*/}
            <Modal
              onClose={() => {
                dispatch({type: CLOSE_MODAL})
              }}
              dimmer="inverted"
              open={strategy && secondModalOpen}
              size="small"
            >
              <Modal.Header>{strategy && strategiesOptions[strategy - 1].text}</Modal.Header>
              <Modal.Content scrolling>
                {strategy && (
                  <Grid columns={2}>
                    <Grid.Column>
                      <Header as='h5'>Required:</Header>
                      {/*@ts-ignore*/}
                      {strategies[strategiesOptions[strategy - 1].text].params.map(param => (
                        <Grid.Row style={{paddingBottom: '10px'}}>
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
                        <Grid.Row style={{paddingBottom: '10px'}}>
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
          <Button color='black' onClick={() => {
            // @ts-ignore
            setExchange(undefined)
            // @ts-ignore
            setSymbol(undefined)
            // @ts-ignore
            dispatch({
              type: UPDATE_STRATEGY,
              value: undefined,
            })
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
              onClick={() => {
                setOpen(false)
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
              }}
              positive
          />
        </Modal.Actions>
      </Modal>
  );
};

export default NewPipeline;