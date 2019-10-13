import React, {Component} from 'react'
import { Icon, Dropdown, Menu, Input, Message, Statistic, Divider, Button, List, Label, Header } from 'semantic-ui-react'
import LabelInput from './LabelInput'

class ImgBar extends Component{

    constructor(props) {
        super(props)
        this.state = {
            position: {
                top: 0,
                left: 0,
            },
        }
    }

    componentDidMount(){
        
    }
    componentDidUpdate(prevProps){

        if (this.props.svg !== prevProps.svg){
            this.setState({
                position: {...this.state.position,
                left: this.props.svg.left,
                top: this.props.svg.top,
                }
            })
        }
    }

    /*********
     * Events
     *********/
    handleLabelUpdate(label){
        console.log('ImgBar label update', label)
        if (this.props.onLabelUpdate){
            this.props.onLabelUpdate(label)
        }
    }
    
    handleClose(){
        if (this.props.onClose){
            this.props.onClose()
        }
    }

    handleMouseEnter(e){
        if (this.props.onMouseEnter){
            this.props.onMouseEnter(e)
        }
    }

    // renderImgLabelInput(){
    //     if (this.props.allowedActions.label){
    //         return <Menu.Item style={{padding: "5px"}}>
    //             <LabelInput
    //                 // multilabels={true}
    //                 multilabels={this.props.multilabels}
    //                 relatedId={this.props.annos.image.id}
    //                 visible={this.props.visible}
    //                 onLabelUpdate={label => this.handleLabelUpdate(label)}
    //                 possibleLabels={this.props.possibleLabels}
    //                 initLabelIds={this.props.imgLabelIds}
    //                 relatedId={this.props.annos.image.id}
    //                 disabled={!this.props.allowedActions.label}
    //                 />
    //         </Menu.Item>
    //     } else {
    //         return null
    //     }
    // }

    renderImgLabels(){
        let label = ''
        if (this.props.imgLabelIds && this.props.imgLabelIds.length > 0){
            // console.log('AnnoBar',this.props.anno)
            let labelObject 
            this.props.imgLabelIds.forEach((lbl, idx) => {
                labelObject = this.props.possibleLabels.find(el => {
                    return el.id === lbl
                })
                if (idx > 0) label += ', '
                label += labelObject.label
            })
            return <Menu.Item >
                    {label}
                </Menu.Item>
        } else {
            return null
        }
    }
    render(){
        if (!this.props.visible) return null
        if (!this.props.annos.image) return null
        return(
        <div style={{
            position:'fixed', 
            top: this.state.position.top, 
            left:this.state.position.left,
            width: this.props.svg.width,
            minWidth: '300px'
            }}
            onMouseEnter={e => {this.handleMouseEnter(e)}}    
        >
            <Menu inverted style={{opacity:0.9, justifyContent:'center', alignItems:'center'}}>
                    {/* {this.renderImgLabelInput()} */}
                    <Menu.Item
                    >
                    {this.props.annos.image.url.split('/').pop() +" (ID: "+this.props.annos.image.id+")"}
                    </Menu.Item>
                    <Menu.Item  
                    >
                    {this.props.annos.image.number +" / "+ this.props.annos.image.amount}
                    </Menu.Item>
                    {this.renderImgLabels()}
            </Menu>
        </div>
        )
    }
}

export default ImgBar