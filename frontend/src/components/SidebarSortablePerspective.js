import React, { useState, useEffect } from 'react';
import {useSortable} from '@dnd-kit/sortable';
import {CSS} from '@dnd-kit/utilities';
import Badge from 'react-bootstrap/Badge';
import Button from 'react-bootstrap/Badge';
import ToggleButton from 'react-bootstrap/ToggleButton';

function SidebarSortablePerspective(props){

    const updateText = props.update_text;
    const setDelete = props.set_delete;
    //const setDeleteLabel = props.set_delete_label;

    const [showInput, setShowInput] = useState(false);

    const {attributes, listeners, setNodeRef, transform, transition, isDragging, setActivatorNodeRef,} = useSortable({id: props.obj.index});

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

	const setColor = (o) =>{
		// 削除ボタンが押されたものはバックグラウンドカラーを変更する
		//console.log("item", obj);
		let state = o["delete_flag"];

		//console.log(" delete : ", state);
		if(state){
			return "#696969";
		} else{
			return "#575977";
		}
	}
	
	const setTextColor = (o) =>{
		// 削除ボタンが押されたものはバックグラウンドカラーを変更する
		let state = o["delete_flag"];
		if(state){
			return "#696969";
		} else{
			return "#fffafa";
		}

	}


    const setBadge = (id) =>{
        // 新規追加されたものはnewマークを付ける
        if(id== null) {
            return(<Badge bg="primary">New</Badge>) ;
        }
    }

    const setDeleteLabel = (flag) =>{
		//削除ボタンの表示を変更。削除状態の場合には表示を「解除」に
		if(flag){return ("解除");}
		else {return("削除");}
	}

    useEffect(() => {
        if(props.active != null){
            setShowInput(false);
        } 
	},[props]);


    const perspectiveInput = () =>{
        if(showInput){
            return(
                <>
                     <Button type="button" variant="secondary" size="sm" value="false" onClick={(e)=>{setShowInput(false)}}>
                            <i class="bi bi-box-arrow-left"></i>
                    </Button>
                    <input type="text" id={"perspective-id-"+props.obj['index']} 
                                style={{width: "150px", height: "26px", fontSize: "14px", backgroundColor: setTextColor(props.obj)}}
                                readOnly={props.obj['delete_flag']}
                                defaultValue={props.obj['name']}  onChange={(e) => updateText(props.obj['index'], e)} 
                                ></input>
                </>
            )
            
        } else {
            return (
                <>
                    <Button type="button" variant="secondary" size="sm" value="false" onClick={(e)=>{setShowInput(true)}}>
                        <i class="bi bi-pencil-square"></i>
                    </Button>
                    <div style={{width: "150px", height: "26px", fontSize: "14px",}}>{props.obj['name']}</div>
                </>
            )

        }
    }


    return (

        <div className="perspective-item" name="perspective-item-" 
            ref={setNodeRef}
            style={{backgroundColor: setColor(props.obj), 
                    border: "1px solid rgba(0, 0, 0, 0.12)",
                    transform: CSS.Transform.toString(transform),
                    transition,
                }}>
              
            <div className="perspective-input gap-2">
                <div className="drag-handle" 
                    ref={setActivatorNodeRef}
                    {...attributes}
                    {...listeners}
                    style={{cursor: isDragging ? "grabbing" : "grab",}}
                >
                    <i class="bi-grip-horizontal"></i> 
                </div>   
                {perspectiveInput()}
                {setBadge(props.obj['id'])}
                
            </div>
 
            <div>
                <ToggleButton type="checkbox" id={"delete-btn-"+props.obj['index']} className="btn btn-secondaryr" variant="secondary" data-bs-toggle="button" size="x-sm" value={props.obj['id']} onClick={(e) => setDelete(props.obj['index'],props.obj['id'], e)}>
                    {setDeleteLabel(props.obj['delete_flag'])	}
                </ToggleButton>
            </div> 
        </div>

    );
}

export default SidebarSortablePerspective;