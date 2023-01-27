import {Button, Header, Icon, Modal} from "semantic-ui-react";
import {DeletePipeline, Pipeline, StopPipeline} from "../types";
import {useState} from "react";


interface Props {
    pipeline: Pipeline
    deletePipeline: DeletePipeline
    stopPipeline: StopPipeline
    open: boolean
    setOpen: (value: boolean) => void
}


const PipelineDeleteButton = (props: Props) => {

    const { deletePipeline, pipeline, setOpen, open } = props

    const [loading, setLoading] = useState(false)

    return (
        <div style={styles.buttonDiv} className='flex-column'>
            <Button
                icon
                style={{width: '80%'}}
                onClick={(event) => {
                    setOpen(true)
                    event.preventDefault()
                    event.stopPropagation();
                }}
                disabled={pipeline.active}
                loading={loading}
            >
                <span style={{marginRight: '10px', marginLeft: '-10px'}}>
                    <Icon name={'delete'}/>
                </span>
                Delete
            </Button>
            <Modal
                onClose={() => setOpen(false)}
                onOpen={() => setOpen(true)}
                open={open}
                size='small'
            >
                <Header icon>
                    <Icon name='delete' />
                    Delete trading bot
                </Header>
                <Modal.Content>
                    <p>
                        Are you sure you want to delete this trading bot?
                    </p>
                </Modal.Content>
                <Modal.Actions>
                    <Button
                        color='red'
                        inverted
                        onClick={(event) => {
                            event.preventDefault()
                            event.stopPropagation()
                            setOpen(false)
                        }}
                    >
                        <Icon name='remove'/> No
                    </Button>
                    <Button
                        color='green'
                        inverted
                        onClick={async (event) => {
                            setLoading(true)
                            event.preventDefault()
                            event.stopPropagation()
                            deletePipeline(pipeline.id).then(() => setLoading(false))
                            setOpen(false)
                        }}
                    >
                        <Icon name='checkmark' /> Yes
                    </Button>
                </Modal.Actions>
            </Modal>
        </div>
    )
}


const styles = {
    buttonDiv: {
        width: '100%',
        alignSelf: 'center'
    }
}

export default PipelineDeleteButton