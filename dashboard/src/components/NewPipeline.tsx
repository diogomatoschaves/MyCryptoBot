import React, {useReducer, useState, useEffect, useRef, ReactNode} from 'react';
import {Button, Grid, Input, Modal, Form} from "semantic-ui-react";
import {
  BalanceObj,
  DropdownOptions,
  EditPipeline,
  Pipeline,
  PipelinesObject,
  Position,
  StartPipeline,
  Strategy
} from "../types";
import {validatePipelineCreation} from "../utils/helpers";
import MessageComponent from "./Message";
import {COLORS_NAMES} from "../utils/constants";
import {
  modalReducer,
  UPDATE_STRATEGY,
  UPDATE_CHECKBOX,
  RESET_MODAL,
  UPDATE_PARAMS,
  getInitialState, GET_INITIAL_STATE
} from "../reducers/modalReducer";
import StrategySelectionModal from "./StrategySelectionModal";


interface Props {
  symbolsOptions: DropdownOptions[];
  strategiesOptions: Strategy[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  startPipeline: StartPipeline;
  editPipeline: EditPipeline;
  balances: BalanceObj;
  pipelines: PipelinesObject;
  positions: Position[]
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
              [pipelineType]: accum[pipelineType] - (pipeline.equity)
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
  }, updateModal] = useReducer(modalReducer, getInitialState(
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

  console.log(strategy)

  const selectedStrategy = strategiesOptions[strategy - 1]

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
            !edit && updateModal({type: RESET_MODAL})
            setOpen(false)
          }}
          onOpen={() => {
            updateModal({
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
                  updateModal({
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
                  updateModal({
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
                  updateModal({
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
                  updateModal({
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
                  updateModal({
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
                onChange={(e: any, {value}: {value?: any}) => updateModal({
                  type: UPDATE_STRATEGY,
                  value,
                })}
                // multiple
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
                  updateModal({
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
                    updateModal({
                      type: UPDATE_PARAMS,
                      value: {equity: value}
                    })
                  }}
                  style={{width: '80%'}}
                  value={equity}
                  placeholder={
                    `Avbl: ${balance.toFixed(1)} USDT
                  `}
                />
              </Form.Field>
            </Form.Group>
            <Form.Group widths={'equal'}>
              <Form.Checkbox
                label={'📡 Live trading'}
                onChange={() => updateModal({type: UPDATE_CHECKBOX})}
                checked={liveTrading}
                style={{alignSelf: 'center'}}
              />
            </Form.Group>
          </Form>
          <StrategySelectionModal
            strategy={strategy}
            strategiesOptions={strategiesOptions}
            secondModalOpen={secondModalOpen}
            selectedStrategy={selectedStrategy}
            updateModal={updateModal}
            params={params}
            secondaryMessage={secondaryMessage}
          />
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
                !edit && updateModal({type: RESET_MODAL})
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
                      updateModal,
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