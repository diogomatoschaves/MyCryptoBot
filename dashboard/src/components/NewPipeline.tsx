import React, {ReactNode, useEffect, useReducer, useRef, useState} from 'react';
import {Button, Form, Grid, Input, Modal} from 'semantic-ui-react';
import Slider, {createSliderWithTooltip} from 'rc-slider';
import 'rc-slider/assets/index.css'
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
  GET_INITIAL_STATE,
  getInitialState,
  modalReducer,
  RESET_MODAL,
  UPDATE_CHECKBOX,
  UPDATE_PARAMS,
  UPDATE_STRATEGY, UPDATE_STRATEGY_COMBINATION
} from "../reducers/modalReducer";
import StrategySelectionModal from "./StrategySelectionModal";
import {availableBalanceReducer, UPDATE_BALANCE} from "../reducers/availableBalanceReducer";


const TooltipSlider = createSliderWithTooltip(Slider)


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
  isMobile: boolean
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
    editPipeline,
    balances,
    positions,
    pipelines,
    children,
    pipeline,
    edit,
    isMobile
  } = props

  const [open, setOpen] = useState(false)

  const [{
    strategy: strategies,
    strategyCombination,
    dynamicStrategies,
    color,
    symbol,
    candleSize,
    name,
    equity,
    leverage,
    exchanges,
    secondModalOpen,
    liveTrading,
    message,
    secondaryMessage
  }, updateModal] = useReducer(modalReducer, getInitialState(
    strategiesOptions,
    symbolsOptions,
    candleSizeOptions,
    exchangeOptions,
    pipeline
  ));

  const [availableBalance, updateBalance] = useReducer(availableBalanceReducer, {
    live: balances ? balances.live.USDT.availableBalance : 0,
    test: balances ? balances.test.USDT.availableBalance : 0
  })

  const previous = useRef({positions, balances}).current;

  useEffect(() => {
    updateBalance({
      type: UPDATE_BALANCE,
      positions,
      pipelines,
      balances
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [positions, balances, previous])

  const balance = availableBalance[liveTrading ? "live" : "test"]

  const selectedStrategy = strategies &&
    dynamicStrategies.find((strategy: Strategy) => strategy.value === strategies.slice(-1)[0])

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
            !edit && updateModal({type: RESET_MODAL, strategiesOptions})
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
              <Form.Field >
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
              <div style={{width: isMobile ? '100%' : '50%', paddingBottom: isMobile ? '15px' : 0}}>
                <div className={'flex-column'} style={{
                  height: '80%',
                  justifyContent: 'space-around',
                  alignItems: 'flex-start',
                  paddingLeft: '7px'
                }}>
                  <div style={{
                    fontSize: '0.93em',
                    fontWeight: 'bold',
                    color: 'rgba(0, 0, 0, 0.65)'
                  }}>
                    Leverage
                  </div>
                  <TooltipSlider
                    style={{width: isMobile ? '76%' : '76%'}}
                    min={1}
                    max={125}
                    step={1}
                    dots
                    value={leverage}
                    onChange={(value: number | number[]) => {
                      updateModal({
                        type: UPDATE_PARAMS,
                        value: {leverage: value}
                      })
                    }}
                  />
                </div>
              </div>
              <Form.Field style={{width: '50%'}}>
                <Form.Select
                  label={'Strategy'}
                  value={strategies}
                  onChange={(e: any, {value}: {value?: any}) => updateModal({
                    type: UPDATE_STRATEGY,
                    value,
                    strategiesOptions
                  })}
                  multiple
                  search
                  selection
                  options={dynamicStrategies}
                  selectOnBlur={false}
                  style={{width: '80%'}}
                />
              </Form.Field>
            </Form.Group>
            <Form.Group widths={'equal'}>
              <Form.Checkbox
                toggle
                label={'📡 Live trading'}
                onChange={() => updateModal({type: UPDATE_CHECKBOX})}
                checked={liveTrading}
                style={{alignSelf: 'center'}}
              />
              <Form.Field>
                <Form.Checkbox
                  radio
                  label={'Majority'}
                  value={'Majority'}
                  onChange={(e, data) => updateModal({
                    type: UPDATE_STRATEGY_COMBINATION,
                    value: data.value
                  })}
                  disabled={strategies.length <= 1}
                  checked={strategyCombination === 'Majority' && strategies.length > 1}
                />
                <Form.Checkbox
                  radio
                  label={'Unanimous'}
                  value={'Unanimous'}
                  onChange={(e, data) => updateModal({
                    type: UPDATE_STRATEGY_COMBINATION,
                    value: data.value
                  })}
                  disabled={strategies.length <= 1}
                  checked={strategyCombination === 'Unanimous' && strategies.length > 1}
                />
              </Form.Field>
            </Form.Group>
          </Form>
          <StrategySelectionModal
            strategies={strategies}
            secondModalOpen={secondModalOpen}
            selectedStrategy={selectedStrategy}
            updateModal={updateModal}
            secondaryMessage={secondaryMessage}
            strategiesOptions={strategiesOptions}
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
                !edit && updateModal({type: RESET_MODAL, strategiesOptions})
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
                      strategies,
                      strategyCombination,
                      candleSize,
                      exchanges,
                      symbolsOptions,
                      dynamicStrategies,
                      candleSizeOptions,
                      exchangeOptions,
                      startPipeline,
                      editPipeline,
                      updateModal,
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