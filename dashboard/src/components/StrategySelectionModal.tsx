import {Fragment} from "react";
import styled from "styled-components";
import {Check, SlidersHorizontal} from 'lucide-react'
import {
  UPDATE_SECOND_MODAL_OPEN,
  UPDATE_SECONDARY_MESSAGE,
  UPDATE_STRATEGY,
  UPDATE_STRATEGY_PARAMS
} from "../reducers/modalReducer";
import {validateParams} from "../utils/helpers";
import {Message, Strategy,} from "../types";
import {Button, Field, InlineMessage, Modal, Select, TextInput} from "../ui";


const Info = styled.p`
  margin: -6px 0 18px;
  font-size: 12.5px;
  line-height: 1.6;
  color: var(--text-dim);
`

const SectionLabel = styled.div`
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin-bottom: 12px;
`

const ParamsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  align-items: start;

  @media (max-width: 560px) {
    grid-template-columns: 1fr;
  }
`

const ParamsColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 14px;
`


interface Props {
  strategies: number[];
  secondModalOpen: boolean
  selectedStrategy: Strategy
  updateModal: any
  secondaryMessage: Message
  strategiesOptions: Strategy[]
}


const StrategySelectionModal = (props: Props) => {

  const {
    strategies,
    secondModalOpen,
    selectedStrategy,
    updateModal,
    secondaryMessage,
    strategiesOptions
  } = props

  const strategyIndex = selectedStrategy && selectedStrategy.value

  const cancel = () => {
    updateModal({
      type: UPDATE_STRATEGY,
      value: strategies.slice(0, -1),
      strategiesOptions
    })
  }

  const renderParamControl = (param: string, paramsDefinition: any) => {
    const definition = paramsDefinition[param]
    return definition.options ? (
      <Select
        searchable
        placeholder={param}
        value={selectedStrategy && selectedStrategy.selectedParams[param]}
        options={definition.options.map((option: any, index: number) => ({
          value: index,
          label: String(option)
        }))}
        onChange={(value: any) =>
          updateModal({
            type: UPDATE_STRATEGY_PARAMS,
            value: {
              [param]: value
            },
            strategyIndex
          })}
      />
    ) : (
      <TextInput
        placeholder={param}
        value={selectedStrategy && selectedStrategy.selectedParams[param] !== undefined
          ? selectedStrategy.selectedParams[param]
          : ''}
        onChange={(event) => {
          updateModal({
            type: UPDATE_STRATEGY_PARAMS,
            value: {
              [param]: event.target.value
            },
            strategyIndex
          })
        }}
      />
    )
  }

  return (
    <Modal
      open={secondModalOpen}
      onClose={cancel}
      width="560px"
      title={
        selectedStrategy && (
          <Fragment>
            <SlidersHorizontal size={17} color="var(--accent)"/>
            {selectedStrategy.text}
          </Fragment>
        )
      }
      footer={
        <>
          <div style={{flex: 1, minWidth: 0}}>
            {secondaryMessage.text && (
              <InlineMessage success={secondaryMessage.success}>
                {secondaryMessage.text}
              </InlineMessage>
            )}
          </div>
          <div style={{display: 'flex', gap: 10, flexShrink: 0}}>
            <Button variant="ghost" onClick={cancel}>
              Cancel
            </Button>
            <Button
              variant="primary"
              icon={<Check/>}
              onClick={() => {
                const {success, updatedParams} = validateParams(
                  selectedStrategy
                )

                if (success) {
                  updateModal({
                    type: UPDATE_SECOND_MODAL_OPEN,
                    value: false
                  })
                  updateModal({
                    type: UPDATE_STRATEGY_PARAMS,
                    value: updatedParams,
                    strategyIndex
                  })
                  updateModal({
                    type: UPDATE_SECONDARY_MESSAGE,
                    message: {text: '', success: true}
                  })
                } else {
                  updateModal({
                    type: UPDATE_SECONDARY_MESSAGE,
                    message: {text: 'Some of the specified values are not valid.', success: false}
                  })
                }
              }}
            >
              Validate
            </Button>
          </div>
        </>
      }
    >
      {selectedStrategy && (
        <Fragment>
          {selectedStrategy.info && <Info>{selectedStrategy.info}</Info>}
          <ParamsGrid>
            <ParamsColumn>
              <SectionLabel>Required</SectionLabel>
              {selectedStrategy.paramsOrder.map((param: string) => (
                <Field key={param} label={param}>
                  {renderParamControl(param, selectedStrategy.params)}
                </Field>
              ))}
            </ParamsColumn>
            {selectedStrategy.optionalParamsOrder.length > 0 && (
              <ParamsColumn>
                <SectionLabel>Optional</SectionLabel>
                {selectedStrategy.optionalParamsOrder.map((param: string) => (
                  <Field key={param} label={param}>
                    {renderParamControl(param, selectedStrategy.optionalParams)}
                  </Field>
                ))}
              </ParamsColumn>
            )}
          </ParamsGrid>
        </Fragment>
      )}
    </Modal>
  )
}

export default StrategySelectionModal
