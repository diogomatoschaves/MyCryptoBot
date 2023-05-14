import React, {useReducer, useState, Fragment, useEffect, useRef, ReactNode} from 'react';
import {Button, Dropdown, Grid, Header, Icon, Input, Modal, Popup, Form} from "semantic-ui-react";
import {BalanceObj, DropdownOptions, EditPipeline, Pipeline, PipelinesObject, Position, StartPipeline} from "../types";
import {validateParams, validatePipelineCreation} from "../utils/helpers";
import MessageComponent from "./Message";
import {COLORS_NAMES} from "../utils/constants";
import {
  modalReducer,
  UPDATE_STRATEGY,
  UPDATE_CHECKBOX,
  UPDATE_SECONDARY_MESSAGE,
  UPDATE_STRATEGY_PARAMS,
  RESET_MODAL,
  UPDATE_SECOND_MODAL_OPEN,
  UPDATE_PARAMS,
  getInitialState, GET_INITIAL_STATE
} from "../reducers/modalReducer";


interface Props {
  symbolsOptions: DropdownOptions[];
  strategiesOptions: DropdownOptions[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  startPipeline: StartPipeline;
  editPipeline: EditPipeline;
  strategies: any;
  balances: BalanceObj;
  pipelines: PipelinesObject;
  positions: Position[];
  children: ReactNode,
  pipeline?: Pipeline,
  edit?: boolean
}


const colorOptions = COLORS_NAMES.map((colorName) => {
  const name = colorName.toLowerCase()
  return {
    key: name,
    text: name,
    value: name,
    label: { className: `light-${name}`, empty: true, circular: true}
  }
})

const leverageOptions = Array.from({length: 20}, (x, i) => ({
  key: i,
  text: i + 1,
  value: i + 1
}))


const UPDATE_BALANCE = "UPDATE_BALANCE"

const availableBalanceReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_BALANCE:
      return {
        ...state,
        ...action.positions.reduce((accum: any, position: Position) => {
          if (position.position === 0) {
            const pipeline = action.pipelines[position.pipelineId]

            if (!pipeline) return accum

            const pipelineType = pipeline.paperTrading ? "test" : "live"
            return {
              ...accum,
              [pipelineType]: accum[pipelineType] - (pipeline.equity / pipeline.leverage)
            }
          } else {
            return accum
          }
        }, {
              live: action.balances.live.USDT.availableBalance,
              test: action.balances.test.USDT.availableBalance
            }),
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
    editPipeline,
    strategies,
    balances,
    positions,
    pipelines,
    children,
    pipeline,
    edit
  } = props

  const [open, setOpen] = useState(false)

  const [{
    strategy,
    color,
    symbol,
    candleSize,
    name,
    equity,
    leverage,
    exchanges,
    secondModalOpen,
    params,
    liveTrading,
    message,
    secondaryMessage
  }, dispatch] = useReducer(modalReducer, getInitialState(
    symbolsOptions,
    strategiesOptions,
    candleSizeOptions,
    exchangeOptions,
    pipeline
  ));

  const [availableBalance, updateBalance] = useReducer(availableBalanceReducer, {
    live: balances.live.USDT.availableBalance,
    test: balances.test.USDT.availableBalance
  })

  const previous = useRef({positions, balances}).current;

  useEffect(() => {
    updateBalance({
      type: UPDATE_BALANCE,
      positions,
      pipelines,
      balances
    })
  }, [])

  useEffect(() => {
    if (previous.balances !== balances || previous.positions !== positions) {
      updateBalance({
        type: UPDATE_BALANCE,
        positions,
        pipelines,
        balances
      })
    }
    return () => {
      previous.positions = positions
      previous.balances = balances
    };
  }, [positions, balances])

  const balance = availableBalance[liveTrading ? "live" : "test"]

  const chosenStrategy = strategy && strategies[strategiesOptions[strategy - 1].text]

  return (
      <Modal
          closeIcon
          onClick={(event: any) => {
            event.preventDefault();
            event.stopPropagation()
          }}
          onClose={(event) => {
            event.preventDefault();
            event.stopPropagation()
            !edit && dispatch({type: RESET_MODAL})
            setOpen(false)
          }}
          onOpen={() => {
            dispatch({
              type: GET_INITIAL_STATE,
              symbols: symbolsOptions,
              strategies: strategiesOptions,
              candleSizes: candleSizeOptions,
              exchanges: exchangeOptions,
              pipeline: pipeline
            })
            setOpen(true)
          }}
          open={open}
          size="small"
          trigger={children}
      >
        <Modal.Header>New Trading Bot <span>🤖</span></Modal.Header>
        <Modal.Content >
          <Form>
            <Form.Group widths={'equal'}>
              <Form.Input
                label={'Name'}
                // placeholder='Name'
                value={name}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {name: value}
                  })
                }}
                style={{width: '80%'}}
              />
              <Form.Select
                label={'Color'}
                className={`light-${color}`}
                value={color}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {color: value}
                  })
                }}
                selection
                options={colorOptions}
                selectOnBlur={false}
                style={{width: '80%'}}
              />
            </Form.Group>
            <Form.Group widths={'equal'}>
              <Form.Select
                label={'Symbol'}
                // placeholder='Symbol'
                value={symbol}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {symbol: value}
                  })
                }}
                search
                selection
                options={symbolsOptions}
                selectOnBlur={false}
                style={{width: '80%'}}
              />
              <Form.Select
                label={'Candle Size'}
                // placeholder='Candle size'
                value={candleSize}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {candleSize: value}
                  })
                }}
                search
                selection
                options={candleSizeOptions}
                selectOnBlur={false}
                style={{width: '80%'}}
              />
            </Form.Group>
            <Form.Group widths={'equal'}>
              <Form.Select
                label={'Exchange'}
                value={exchanges}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {exchanges: value}
                  })
                }}
                multiple
                search
                selection
                options={exchangeOptions}
                selectOnBlur={false}
                style={{width: '80%'}}
              />
              <Form.Select
                label={'Strategy'}
                value={strategy}
                onChange={(e: any, {value}: {value?: any}) => dispatch({
                  type: UPDATE_STRATEGY,
                  value,
                })}
                search
                selection
                options={strategiesOptions}
                selectOnBlur={false}
                style={{width: '80%'}}
              />
            </Form.Group>
            <Form.Group widths={'equal'}>
              <Form.Select
                label={'Leverage'}
                value={leverage}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {leverage: value}
                  })
                }}
                selection
                options={leverageOptions}
                selectOnBlur={false}
                style={{width: '80%'}}
              />
              <Form.Field>
                <label>Equity</label>
                <Input
                  onChange={(e: any, {value}: {value?: any}) => {
                    dispatch({
                      type: UPDATE_PARAMS,
                      value: {equity: value}
                    })
                  }}
                  style={{width: '80%'}}
                  value={equity}
                  placeholder={
                    `Avbl: ${balance.toFixed(1)} USDT Max: ${(balance * leverage).toFixed(1)} USDT
                  `}
                />
              </Form.Field>
            </Form.Group>
            <Form.Group widths={'equal'}>
              <Form.Checkbox
                label={'📡 Live trading'}
                onChange={() => dispatch({type: UPDATE_CHECKBOX})}
                checked={liveTrading}
                style={{alignSelf: 'center'}}
              />
            </Form.Group>
          </Form>
            <Modal
              onClose={() => {
                // dispatch({type: CLOSE_MODAL})
              }}
              open={strategy && secondModalOpen}
              size="small"
            >
              <Modal.Header>
                {strategy && (
                  <Fragment>
                    {strategiesOptions[strategy - 1].text}
                    <Popup
                      content={chosenStrategy.info}
                      header={`${chosenStrategy.name} Strategy`}
                      position='bottom left'
                      trigger={<Icon name='info circle' style={{marginLeft: '10px'}}/>}
                    />
                  </Fragment>
                )}
              </Modal.Header>
              <Modal.Content scrolling>
                {strategy && (
                  <Grid columns={2}>
                    <Grid.Column>
                      <Header as='h5'>Required:</Header>
                      {strategy &&  chosenStrategy.paramsOrder.map((param: string) => (
                        <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                          <Grid.Column>
                            {chosenStrategy.params[param].options ?
                              (
                                <Dropdown
                                  placeholder={param}
                                  value={params[param]}
                                  onChange={(e: any, {value}: {value?: any}) =>
                                      dispatch({
                                        type: UPDATE_STRATEGY_PARAMS,
                                        value: {
                                          [param]: value
                                        },
                                      })}
                                  search
                                  selection
                                  selectOnBlur={false}
                                  options={chosenStrategy.params[param].options.map(
                                      (p: any, index: number) => ({key: index, text: p, value: index})
                                  )}
                                />
                              ) : (
                                <Input
                                  onChange={(e, {value}) => {
                                    dispatch({
                                      type: UPDATE_STRATEGY_PARAMS,
                                      value: {
                                        [param]: value
                                      }
                                    })
                                  }}
                                  placeholder={param}
                                />
                              )}
                          </Grid.Column>
                        </Grid.Row>
                      ))}
                    </Grid.Column>
                    <Grid.Column>
                      <Header as='h5'>Optional:</Header>
                      {/*@ts-ignore*/}
                      {chosenStrategy.optionalParamsOrder.map(param => (
                        <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                          <Grid.Column>
                            {chosenStrategy.optionalParams[param].options ?
                              (
                                <Dropdown
                                  placeholder={param}
                                  value={params[param]}
                                  onChange={(e: any, {value}: {value?: any}) =>
                                      dispatch({
                                        type: UPDATE_STRATEGY_PARAMS,
                                        value: {
                                          [param]: value
                                        },
                                      })}
                                  search
                                  selection
                                  selectOnBlur={false}
                                  options={chosenStrategy.optionalParams[param].options.map(
                                      (p:  any, index: number) => ({key: index, text: p, value: index})
                                  )}
                                />
                              ) : (
                                <Input
                                  onChange={(e, {value}) => {
                                    dispatch({
                                      type: UPDATE_STRATEGY_PARAMS,
                                      value: {
                                        [param]: value
                                      }
                                    })
                                  }}
                                  placeholder={param}/>
                                )}
                          </Grid.Column>
                        </Grid.Row>
                      ))}
                    </Grid.Column>
                  </Grid>
                )}
              </Modal.Content>
              <Modal.Actions>
                <div className="flex-row" style={{justifyContent: secondaryMessage.text ? 'space-between' : 'flex-end'}}>
                  {secondaryMessage.text && (
                    <div>
                      <Grid.Row>
                        <Grid.Column>
                          <MessageComponent success={secondaryMessage.success} message={secondaryMessage.text}/>
                        </Grid.Column>
                      </Grid.Row>
                    </div>
                  )}
                  <div>
                    <Button color='black' onClick={() => {
                      dispatch({
                        type: UPDATE_STRATEGY,
                        value: null
                      })
                    }}>
                      Cancel
                    </Button>
                    <Button
                      positive
                      icon='check'
                      content='Validate'
                      onClick={() => {
                        const {success, updatedParams} = validateParams (
                          params,
                          strategies[strategiesOptions[strategy - 1].text]
                        )

                        if (success) {
                          dispatch({
                            type: UPDATE_SECOND_MODAL_OPEN,
                            value: false
                          })
                          dispatch({
                            type: UPDATE_STRATEGY_PARAMS,
                            value: updatedParams
                          })
                          dispatch({
                            type: UPDATE_SECONDARY_MESSAGE,
                            message: {text: '', success: true}
                          })
                        } else {
                          dispatch({
                            type: UPDATE_SECONDARY_MESSAGE,
                            message: {text: 'Some of the specified values are not valid.', success: false}
                          })
                        }
                      }}
                    />
                  </div>
                </div>
              </Modal.Actions>
            </Modal>
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
              <Button color='black' onClick={(event) => {
                event.preventDefault();
                event.stopPropagation()
                !edit && dispatch({type: RESET_MODAL})
                setOpen(false)
              }}>
                Cancel
              </Button>
              <Button
                  positive
                  content={edit ? "Update parameters" : "Create trading bot"}
                  labelPosition='right'
                  icon='checkmark'
                  onClick={async (event) => {
                    event.preventDefault();
                    event.stopPropagation()
                    const success = await validatePipelineCreation({
                      name,
                      equity,
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
                      editPipeline,
                      dispatch,
                      params,
                      liveTrading,
                      leverage,
                      edit,
                      pipelineId: pipeline && pipeline.id,
                      balance: balances[liveTrading ? 'live': 'test'].USDT.availableBalance
                    })
                    if (success) setOpen(false)
                  }}
              />
            </div>
          </div>
        </Modal.Actions>
      </Modal>
  );
};

export default NewPipeline;