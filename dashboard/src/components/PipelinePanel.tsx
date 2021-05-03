import {Button, Dropdown, Grid, Divider} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {ActivePipeline, DropdownOptions} from "../types";
import Pipeline from './Pipeline'


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    activePipelines: ActivePipeline[]
}

function PipelinePanel(props: Props) {

    const { symbolsOptions, strategiesOptions, activePipelines } = props

    return (
        <StyledSegment basic className="flex-column">
            <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>Bot Control Panel</Divider>
            <Grid columns={2}>
                <Grid.Row>
                    <Grid.Column>
                        <Dropdown placeholder='Symbol' search selection options={symbolsOptions} />
                    </Grid.Column>
                    <Grid.Column>
                        <Dropdown placeholder='Strategy' search selection options={strategiesOptions} />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                    <Grid.Column>
                        <Dropdown placeholder='Strategy' search selection options={strategiesOptions} />
                    </Grid.Column>
                    <Grid.Column>
                        <Button color='green'>Start Bot</Button>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
            <Divider horizontal style={{marginTop: '30px'}}>Active Pipelines</Divider>
            {activePipelines.map(pipeline => <Pipeline pipeline={pipeline}/>)}
        </StyledSegment>
    );
}

export default PipelinePanel;
