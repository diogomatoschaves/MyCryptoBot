import React, {ReactNode, useEffect, useReducer, useRef, useState} from 'react';
import styled from 'styled-components';
import {Bot, Check} from 'lucide-react';
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
import {
  Button,
  Field,
  InlineMessage,
  Modal,
  SegmentedControl,
  Select,
  Slider,
  TextInput,
  Toggle
} from "../ui";
import {BOT_COLORS, BotColorName} from "../theme";


const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;

  @media (max-width: 560px) {
    grid-template-columns: 1fr;
  }
`

const FullRow = styled.div`
  grid-column: 1 / -1;
`

const colorOptions = COLORS_NAMES.map((colorName) => {
  const name = colorName.toLowerCase()
  return {
    value: name,
    label: name,
    color: BOT_COLORS[name as BotColorName],
  }
})

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
  disabled?: boolean
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
    edit,
    disabled
  } = props

  const [open, setOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)

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
    live: balances?.live?.USDT?.availableBalance ?? 0,
    test: balances?.test?.USDT?.availableBalance ?? 0
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

  const openModal = (event: React.MouseEvent) => {
    event.preventDefault()
    event.stopPropagation()
    if (disabled) return
    updateModal({
      type: GET_INITIAL_STATE,
      symbols: symbolsOptions,
      strategies: strategiesOptions,
      candleSizes: candleSizeOptions,
      exchanges: exchangeOptions,
      pipeline: pipeline
    })
    setOpen(true)
  }

  const closeModal = () => {
    if (!edit) updateModal({type: RESET_MODAL, strategiesOptions})
    setOpen(false)
  }

  const handleSubmit = async (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation()
    setSubmitting(true)
    try {
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
        balance: balances[liveTrading ? 'live': 'test']?.USDT?.availableBalance ?? 0
      })
      if (success) setOpen(false)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <span style={{display: 'contents'}} onClick={openModal}>
        {children}
      </span>
      <Modal
        open={open}
        onClose={closeModal}
        width="640px"
        title={
          <>
            <Bot size={18} color="var(--accent)"/>
            {edit ? 'Edit Trading Bot' : 'New Trading Bot'}
          </>
        }
        footer={
          <>
            <div style={{flex: 1, minWidth: 0}}>
              {message.text && (
                <InlineMessage success={message.success}>{message.text}</InlineMessage>
              )}
            </div>
            <div style={{display: 'flex', gap: 10, flexShrink: 0}}>
              <Button variant="ghost" onClick={(event) => {
                event.preventDefault();
                event.stopPropagation()
                closeModal()
              }}>
                Cancel
              </Button>
              <Button
                variant="primary"
                icon={<Check/>}
                loading={submitting}
                onClick={handleSubmit}
              >
                {edit ? "Update parameters" : "Create trading bot"}
              </Button>
            </div>
          </>
        }
      >
        <FormGrid>
          <Field label="Name">
            <TextInput
              value={name}
              onChange={(event) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {name: event.target.value}
                })
              }}
            />
          </Field>
          <Field label="Color">
            <Select
              options={colorOptions}
              value={color}
              placeholder="Pick a color"
              onChange={(value: any) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {color: value}
                })
              }}
            />
          </Field>
          <Field label="Symbol">
            <Select
              searchable
              options={symbolsOptions.map((option) => ({value: option.value as number, label: option.text}))}
              value={symbol}
              placeholder="e.g. BTCUSDT"
              onChange={(value: any) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {symbol: value}
                })
              }}
            />
          </Field>
          <Field label="Candle Size">
            <Select
              searchable
              options={candleSizeOptions.map((option) => ({value: option.value as number, label: option.text}))}
              value={candleSize}
              placeholder="e.g. 1h"
              onChange={(value: any) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {candleSize: value}
                })
              }}
            />
          </Field>
          <Field label="Exchange">
            <Select
              multi
              options={exchangeOptions.map((option) => ({value: option.value as number, label: option.text}))}
              value={exchanges}
              placeholder="Select exchange"
              onChange={(value: any) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {exchanges: value}
                })
              }}
            />
          </Field>
          <Field label="Equity" hint={`Available: ${balance.toFixed(1)} USDT`}>
            <TextInput
              disabled={edit}
              value={equity}
              suffix="USDT"
              placeholder="0.0"
              onChange={(event) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {equity: event.target.value}
                })
              }}
            />
          </Field>
          <FullRow>
            <Field label="Strategy">
              <Select
                multi
                searchable
                options={dynamicStrategies.map((strategy: Strategy) => ({
                  value: strategy.value,
                  label: strategy.text
                }))}
                value={strategies}
                placeholder="Add one or more strategies"
                onChange={(value: any) => updateModal({
                  type: UPDATE_STRATEGY,
                  value,
                  strategiesOptions
                })}
              />
            </Field>
          </FullRow>
          <Field label="Leverage">
            <Slider
              min={1}
              max={125}
              value={leverage}
              disabled={edit}
              formatValue={(value) => `×${value}`}
              onChange={(value) => {
                updateModal({
                  type: UPDATE_PARAMS,
                  value: {leverage: value}
                })
              }}
            />
          </Field>
          <Field label="Combination" hint={strategies.length <= 1 ? 'Requires 2+ strategies' : undefined}>
            <SegmentedControl
              options={[
                {value: 'Majority', label: 'Majority'},
                {value: 'Unanimous', label: 'Unanimous'},
              ]}
              disabled={strategies.length <= 1}
              isActive={(value) => strategyCombination === value && strategies.length > 1}
              onToggle={(value) => updateModal({
                type: UPDATE_STRATEGY_COMBINATION,
                value
              })}
            />
          </Field>
          <FullRow>
            <Toggle
              checked={liveTrading}
              disabled={edit}
              onChange={() => updateModal({type: UPDATE_CHECKBOX})}
              label={
                <span>
                  Live trading{' '}
                  <span style={{color: 'var(--text-faint)', fontSize: 12}}>
                    — trades with real funds
                  </span>
                </span>
              }
            />
          </FullRow>
        </FormGrid>
        <StrategySelectionModal
          strategies={strategies}
          secondModalOpen={secondModalOpen}
          selectedStrategy={selectedStrategy}
          updateModal={updateModal}
          secondaryMessage={secondaryMessage}
          strategiesOptions={strategiesOptions}
        />
      </Modal>
    </>
  );
};

export default NewPipeline;
