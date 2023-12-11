import {Button, Dropdown, Grid, Header, Icon, Input, Modal, Popup} from "semantic-ui-react";
import React, {Fragment} from "react";
import {
  UPDATE_SECOND_MODAL_OPEN,
  UPDATE_SECONDARY_MESSAGE,
  UPDATE_STRATEGY,
  UPDATE_STRATEGY_PARAMS
} from "../reducers/modalReducer";
import MessageComponent from "./Message";
import {validateParams} from "../utils/helpers";
import {Message, Strategy,} from "../types";


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

  return (
    <Modal
      onClose={() => {
        // updateModal({type: CLOSE_MODAL})
      }}
      open={secondModalOpen}
      size="small"
    >
      <Modal.Header>
        {selectedStrategy && (
          <Fragment>
            {selectedStrategy.text}
            <Popup
              content={selectedStrategy.info}
              header={`${selectedStrategy.name} Strategy`}
              position='bottom left'
              trigger={<Icon name='info circle' style={{marginLeft: '10px'}}/>}
            />
          </Fragment>
        )}
      </Modal.Header>
      <Modal.Content scrolling>
        {selectedStrategy && (
          <Grid columns={2}>
            <Grid.Column>
              <Header as='h5'>Required:</Header>
              {selectedStrategy.paramsOrder.map((param: string) => (
                <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                  <Grid.Column>
                    {selectedStrategy.params[param].options ?
                      (
                        <Dropdown
                          placeholder={param}
                          value={selectedStrategy && selectedStrategy.selectedParams[param]}
                          onChange={(e: any, {value}: {value?: any}) =>
                              updateModal({
                                type: UPDATE_STRATEGY_PARAMS,
                                value: {
                                  [param]: value
                                },
                                strategyIndex
                              })}
                          search
                          selection
                          selectOnBlur={false}
                          options={selectedStrategy.params[param].options.map(
                              (p: any, index: number) => ({key: index, text: p, value: index})
                          )}
                        />
                      ) : (
                        <Input
                          onChange={(e, {value}) => {
                            updateModal({
                              type: UPDATE_STRATEGY_PARAMS,
                              value: {
                                [param]: value
                              },
                              strategyIndex
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
              {selectedStrategy.optionalParamsOrder.length > 0 && (
                <Fragment>
                  <Header as='h5'>Optional:</Header>
                  {/*@ts-ignore*/}
                  {selectedStrategy.optionalParamsOrder.map(param => (
                    <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                      <Grid.Column>
                        {selectedStrategy.optionalParams[param].options ?
                          (
                            <Dropdown
                              placeholder={param}
                              value={selectedStrategy && selectedStrategy.selectedParams[param]}
                              onChange={(e: any, {value}: {value?: any}) =>
                                  updateModal({
                                    type: UPDATE_STRATEGY_PARAMS,
                                    value: {
                                      [param]: value
                                    },
                                    strategyIndex
                                  })}
                              search
                              selection
                              selectOnBlur={false}
                              options={selectedStrategy.optionalParams[param].options.map(
                                  (p:  any, index: number) => ({key: index, text: p, value: index})
                              )}
                            />
                          ) : (
                            <Input
                              onChange={(e, {value}) => {
                                updateModal({
                                  type: UPDATE_STRATEGY_PARAMS,
                                  value: {
                                    [param]: value
                                  },
                                  strategyIndex
                                })
                              }}
                              placeholder={param}/>
                            )}
                      </Grid.Column>
                    </Grid.Row>
                  ))}
                </Fragment>
              )}
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
              updateModal({
                type: UPDATE_STRATEGY,
                value: strategies.slice(0,-1),
                strategiesOptions
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
            />
          </div>
        </div>
      </Modal.Actions>
    </Modal>
  )
}

export default StrategySelectionModal
