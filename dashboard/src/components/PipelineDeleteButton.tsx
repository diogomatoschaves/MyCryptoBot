import {useState} from "react";
import {Trash2} from 'lucide-react'
import {DeletePipeline, Pipeline, StopPipeline} from "../types";
import {Button, Modal} from "../ui";


interface Props {
    pipeline: Pipeline
    deletePipeline: DeletePipeline
    stopPipeline: StopPipeline
    open: boolean
    setOpen: (value: boolean) => void
    fullWidth?: boolean
}


const PipelineDeleteButton = (props: Props) => {

    const { deletePipeline, pipeline, setOpen, open, fullWidth = true } = props

    const [loading, setLoading] = useState(false)

    return (
        <>
            <Button
                variant="ghost"
                icon={<Trash2/>}
                fullWidth={fullWidth}
                disabled={pipeline.active}
                loading={loading}
                onClick={(event) => {
                    event.preventDefault()
                    event.stopPropagation();
                    setOpen(true)
                }}
            >
                Delete
            </Button>
            <Modal
                open={open}
                onClose={() => setOpen(false)}
                title="Delete trading bot"
                width="420px"
                footer={
                    <div style={{display: 'flex', gap: 10, justifyContent: 'flex-end', width: '100%'}}>
                        <Button
                            variant="ghost"
                            onClick={(event) => {
                                event.preventDefault()
                                event.stopPropagation()
                                setOpen(false)
                            }}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="danger"
                            icon={<Trash2/>}
                            onClick={(event) => {
                                setLoading(true)
                                event.preventDefault()
                                event.stopPropagation()
                                deletePipeline(pipeline.id).then(() => setLoading(false))
                                setOpen(false)
                            }}
                        >
                            Delete bot
                        </Button>
                    </div>
                }
            >
                <p style={{margin: 0, color: 'var(--text-dim)', fontSize: 13, lineHeight: 1.6}}>
                    Are you sure you want to delete <strong style={{color: 'var(--text)'}}>{pipeline.name}</strong>?
                    This will remove the bot and its configuration permanently.
                </p>
            </Modal>
        </>
    )
}

export default PipelineDeleteButton
