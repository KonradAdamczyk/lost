import { Observable } from 'l3p-frontend'
import BaseNodeModel from '../../BaseNodeModel'


export default class AnnoTaskRunningModel extends BaseNodeModel {
    constructor(params) {
		const { peN, peOut, id, state, annoTask } = params

		super({ peN, peOut })

		this.id = id
		this.annoTask = annoTask
		// for progress bar updates
		this.state = new Observable(state)
		this.progress = new Observable(annoTask.progress ? annoTask.progress : 0)
    }
}