import React, {useState} from 'react';
import {Button, Dropdown, Grid, Header, Icon, Modal} from "semantic-ui-react";
import {DropdownOptions, StartPipeline} from "../types";


interface Props {
  symbolsOptions: DropdownOptions[];
  strategiesOptions: DropdownOptions[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  startPipeline: StartPipeline;
}


const validatePipelineCreation = (
  {
    symbol,
    symbolsOptions,
    strategy,
    strategiesOptions,
    candleSize,
    candleSizeOptions,
    exchanges,
    exchangeOptions,
    startPipeline
  }: {
    symbol: number | undefined,
    symbolsOptions: DropdownOptions[],
    strategy: number | undefined,
    strategiesOptions: DropdownOptions[],
    candleSize: number | undefined,
    candleSizeOptions: DropdownOptions[],
    exchanges: Array<number>,
    exchangeOptions: DropdownOptions[],
    startPipeline: StartPipeline
  }) => {
  if (!symbol || !strategy || !candleSize || exchanges.length == 0) {
    console.log("All parameters must be specified")
    return
  }

  startPipeline({
    // @ts-ignore
    symbol: symbolsOptions.find(option => symbol === option.value).text,
    // @ts-ignore
    strategy: strategiesOptions.find(option => strategy === option.value).text,
    // @ts-ignore
    candleSize: candleSizeOptions.find(option => candleSize === option.value).text,
    // @ts-ignore
    exchanges: exchangeOptions.find(option => exchanges[0] === option.value).text, // TODO: Generalize this for any number of exchanges
  })

}



const NewPipeline = (props: Props) => {

  const {
    symbolsOptions,
    strategiesOptions,
    candleSizeOptions,
    exchangeOptions,
    startPipeline,
  } = props

  const [open, setOpen] = useState(false)

  const [symbol, setSymbol] = useState()
  const [strategy, setStrategy] = useState()
  const [candleSize, setCandleSize] = useState()
  const [exchanges, setExchange] = useState([])


  return (
      <Modal
          onClose={() => setOpen(false)}
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
        <Modal.Header>Start a New Trading Bot</Modal.Header>
        <Modal.Content scrolling>
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
                    placeholder='Strategy'
                    value={strategy}
                    onChange={(e: any, {value}: {value?: any}) => setStrategy(value)}
                    search
                    selection
                    options={strategiesOptions}
                />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
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
            </Grid.Row>
            <Grid.Row>
              <Grid.Column>
                {/*<Form>*/}
                {/*    <TextArea placeholder='Params'/>*/}
                {/*</Form>*/}
              </Grid.Column>
              <Grid.Column style={{alignSelf: 'center'}}>

              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Modal.Content>
        <Modal.Actions>
          <Button color='black' onClick={() => setOpen(false)}>
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