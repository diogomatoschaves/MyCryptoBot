import {Button, Dropdown, Grid, Header, Icon, Input, Modal, Popup} from "semantic-ui-react";
import React, {Fragment, ReactNode} from "react";
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
  strategy: any
  strategiesOptions: Strategy[];
  secondModalOpen: boolean
  selectedStrategy: Strategy
  updateModal: any
  params: any
  secondaryMessage: Message
}


const StrategySelectionModal = (props: Props) => {

  const {
    strategy,
    strategiesOptions,
    secondModalOpen,
    selectedStrategy,
    updateModal,
    params,
    secondaryMessage,
  } = props
  
  return (
    <Modal
      onClose={() => {
        // updateModal({type: CLOSE_MODAL})
      }}
      open={strategy && secondModalOpen}
      size="small"
    >
      <Modal.Header>
        {strategy && (
          <Fragment>
            {strategiesOptions[strategy - 1].text}
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
        {strategy && (
          <Grid columns={2}>
            <Grid.Column>
              <Header as='h5'>Required:</Header>
              {strategy &&  selectedStrategy.paramsOrder.map((param: string) => (
                <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                  <Grid.Column>
                    {selectedStrategy.params[param].options ?
                      (
                        <Dropdown
                          placeholder={param}
                          value={params[param]}
                          onChange={(e: any, {value}: {value?: any}) =>
                              updateModal({
                                type: UPDATE_STRATEGY_PARAMS,
                                value: {
                                  [param]: value
                                },
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
              {selectedStrategy.optionalParamsOrder.map(param => (
                <Grid.Row key={param} style={{paddingBottom: '10px'}}>
                  <Grid.Column>
                    {selectedStrategy.optionalParams[param].options ?
                      (
                        <Dropdown
                          placeholder={param}
                          value={params[param]}
                          onChange={(e: any, {value}: {value?: any}) =>
                              updateModal({
                                type: UPDATE_STRATEGY_PARAMS,
                                value: {
                                  [param]: value
                                },
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
              updateModal({
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
                  selectedStrategy
                )

                if (success) {
                  updateModal({
                    type: UPDATE_SECOND_MODAL_OPEN,
                    value: false
                  })
                  updateModal({
                    type: UPDATE_STRATEGY_PARAMS,
                    value: updatedParams
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
