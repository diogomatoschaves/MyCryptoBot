import React, {useReducer, useState, Fragment} from 'react';
import {Button, Checkbox, Dropdown, Grid, Header, Icon, Input, Modal, Popup, Form} from "semantic-ui-react";
import {BalanceObj, DropdownOptions, StartPipeline, UpdateMessage} from "../types";
import {validateParams, validatePipelineCreation} from "../utils/helpers";
import MessageComponent from "./Message";
import {COLORS_NAMES} from "../utils/constants";
import {
  modalReducer,
  UPDATE_STRATEGY,
  UPDATE_CHECKBOX,
  UPDATE_SECONDARY_MESSAGE,
  UPDATE_MESSAGE,
  UPDATE_STRATEGY_PARAMS,
  RESET_MODAL,
  UPDATE_SECOND_MODAL_OPEN,
  initialState, UPDATE_PARAMS
} from "../reducers/modalReducer";


interface Props {
  symbolsOptions: DropdownOptions[];
  strategiesOptions: DropdownOptions[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  startPipeline: StartPipeline;
  updateMessage: UpdateMessage;
  strategies: any;
  balances: BalanceObj
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


const NewPipeline = (props: Props) => {

  const {
    symbolsOptions,
    strategiesOptions,
    candleSizeOptions,
    exchangeOptions,
    startPipeline,
    strategies,
    balances
  } = props

  const [open, setOpen] = useState(false)

  const [{
    strategy,
    color,
    symbol,
    candleSize,
    name,
    allocation,
    exchanges,
    secondModalOpen,
    params,
    liveTrading,
    message,
    secondaryMessage
  }, dispatch] = useReducer(modalReducer, initialState);

  const availableBalance = liveTrading ? balances.live.USDT.availableBalance : balances.test.USDT.availableBalance

  const chosenStrategy = strategy && strategies[strategiesOptions[strategy - 1].text]

  return (
      <Modal
          closeIcon
          onClose={() => {
            dispatch({type: RESET_MODAL})
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
              <Form.Input
                label={'Equity'}
                placeholder={`${availableBalance.toFixed(1)} USDT available`}
                value={allocation}
                onChange={(e: any, {value}: {value?: any}) => {
                  dispatch({
                    type: UPDATE_PARAMS,
                    value: {allocation: value}
                  })
                }}
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
              <Form.Checkbox
                label={'📡 Live trading'}
                onChange={() => dispatch({type: UPDATE_CHECKBOX})}
                checked={liveTrading}
                style={{alignSelf: 'center'}}
              />
              <Form.Select
                label={'Color'}
                className={`light-${color}`}
                placeholder='Color'
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
                      position='right center'
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
              <Button color='black' onClick={() => {
                dispatch({type: RESET_MODAL})
                setOpen(false)
              }}>
                Cancel
              </Button>
              <Button
                  positive
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
                      liveTrading,
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