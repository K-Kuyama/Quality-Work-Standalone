import React, { useState, useEffect } from 'react';

import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Badge from 'react-bootstrap/Badge';
import ToggleButton from 'react-bootstrap/ToggleButton';


import Cookies from "universal-cookie";
import Settings from "../Settings";
//import SidebarSortablePerspective from "./SidebarSortablePerspective";

import {DragOverlay,DndContext} from '@dnd-kit/core';
import {SortableContext, arrayMove} from '@dnd-kit/sortable';
import {useSortable} from '@dnd-kit/sortable';
import {CSS} from '@dnd-kit/utilities';


function EditableCategoryList(props){
    // 順序設定ができるカテゴリー編集画面を表示する
    const [items, setItems] = useState([]);
    const [selected, setSelected] = useState(0);
    const [pid, setPid] = useState(0);
    const [activeId, setActiveId] = useState(null); // for dragging
 
    const setDefChange = props.handler;

	const createInitialItems = (data) =>{
		// propsで渡されたcategories情報データから表示用データを作成する
		// delete_flagを追加する
		/* id name color delete_flag  */
		let ret_data =[]
		if(data){
			data.map((obj, idx) =>{
				ret_data.push({index: idx, id: obj['id'], perspective: obj['perspective'], name: obj['name'], color: obj['color'], delete_flag: false});
			})
		}
		console.log(ret_data);
		return ret_data;
	}

    const addNewItem = (e)=>{
		// カテゴリーの新規追加ハンドラー
		setItems([...items, {index: items.length, id: null, perspective: pid, name: "", color: "#fff", delete_flag: false}]);
	}

    const handleDragEnd =(event) => {
        // カテゴリーをドラッグして移動させた後の処理。新しい並び順を返す
        const {active, over} = event;

        if (active.id !== over.id) {
            setItems(items => {
            const oldIndex = items.findIndex(item => item.index === active.id);
            const newIndex = items.findIndex(item => item.index === over.id);
            const nitems = arrayMove(items, oldIndex, newIndex);
            return nitems;
            });
        }
        setActiveId(null);
        //syncTextValue();
    }


    useEffect(()=>{
        setPid(props.pid);

        if(props.pid != 0){
            let target = Settings.HOME_PATH+'/api/user_def/_Category/?'
            if(Settings.DEVELOP){
                target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/_Category/?'
            }			
            let query = new URLSearchParams({p_id: props.pid})
            fetch(target + query, {
                        credentials: "same-origin",
                    }
            )
            .then(response => {
                return response.json();
            })
            .then(result =>{
                const txt = JSON.stringify(result, null,' ');
                //console.log('---Success ---');
                console.log(txt);
                let res = JSON.parse(txt);
                setItems(createInitialItems(res));
            })
            .catch(error =>{
                console.error('----Error---');
                console.error(error);
            })            

            }
        
    },[props])

    const setOrder = (items) =>{
        // 並び替えのためのindexを設定。編集画面で表示されている順にindexを振る
        let n_items = items.slice(); //itemsのコピーを新しい配列として生成
        for (let i = 0; i < n_items.length; i++) {
            n_items[i]['index'] = i;
        }
        return n_items;
    }
    
    const saveInfo = (e) =>{
        // 設定保存用ハンドラー
        // データベースにカテゴリー情報の変更を反映する
        //console.log("items",items);
        const n_items = setOrder(items);
        const cookies = new Cookies();
        const token = cookies.get('csrftoken')
        let target = Settings.HOME_PATH+'/api/user_def/category_editor/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/category_editor/'
        }
        fetch(target,
            {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': token,
                },
                body: JSON.stringify(n_items)
            }
        )
        .then(response => {
            return response.json();
        })
        .then(result =>{
            const txt = JSON.stringify(result, null,' ');
            //console.log('---Success ---');
            //console.log(txt);
            let res = JSON.parse(txt);
            setItems(res);
            setDefChange(true);
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
        })

    }


    
    const updateText = (idx, e)=>{
		// タイトルの変更ハンドラー
		console.log(e.target);
		setItems(
			//items.map((item, index) => {
			items.map((item) => {
				//if(index == idx){
				if(item['index'] == idx){
					return{...item, name: e.target.value};
				} else {
					return item;
				}
			}))
	}

    const updateColor = (idx, e)=>{
		// 色の変更ハンドラー
		console.log(e.target);
		setItems(
			//items.map((item, index) => {
			items.map((item) => {
				//if(index == idx){
				if(item['index'] == idx){
					return{...item, color: e.target.value};
				} else {
					return item;
				}
			}))
	}        

    const setDelete = (idx, id, e)=>{
		//削除ボタンが押された時のハンドラー
        /*
		items.map((item)=>{
			if(item['index'] == idx){
				const str = "input[id='perspective-id-"+idx+"']"
				const el = document.querySelector(str);
				if(el){
					console.log("index", idx, "text",el.value);
				}

			}
		})*/
		if(id){updateState(idx, e);}
		else{deleteItem(idx);}
	}

    const deleteItem = (idx)=>{
		setItems(items.filter((item) => (item['index'] !== idx)));
	}	
	
	const updateState = (idx, e)=>{
		let sts = e.target.checked;
		setItems(
			items.map((item) =>{
				if(item['index'] == idx){
					return{...item, delete_flag: !(item.delete_flag)};
				} else {
					return item;
				}
			}))
	}



    return(
        <div className="category_defs">
            <div className="pp_tail">
				<Button type="button" className="btn btn-ppheader" data-bs-toggle="button" variant="primary" size="sm" value="save" 
					onClick={(e)=>saveInfo(e)}>
    					保存
    			</Button>
    		</div> 
            <div className="d-grid gap-2">
                <div >
                    <DndContext onDragEnd={handleDragEnd} onDragStart={({active}) => setActiveId(active.id)}>
                        <SortableContext items={items.map(item => item.index)}>
                            <ButtonGroup className="category-list">
                                {items.map(((obj, idx) =>{
                                    return(
                                        <SortableCategory obj={obj}
                                            idx={idx}
                                            active={activeId} 
                                            update_text={updateText} 
                                            update_color={updateColor}
											set_delete={setDelete} 
                                            />
                                    )
                                }))}
                            </ButtonGroup>
                        </SortableContext>
                    </DndContext>
                </div>
                <Button type="button" class="btn btn-secondary"  variant="dark" size="sm" 
                        value="0" onClick={(e) => addNewItem(e)}  style={{width: "100px"}}>
                                + 新規追加
                </Button>
            </div>

        </div>
    )

}



/******************* 
  ソート可能なカテゴリー設定タグ
  ************************/


function SortableCategory(props){
    const updateText = props.update_text;
    const updateColor = props.update_color;
    const setDelete = props.set_delete;
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
            //return "#474963";
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
        //console.log(props.obj['name'],props.active);
        if(props.active != null){
            setShowInput(false);
        } 
    },[props]);

    const categoryInput = () =>{
        if(showInput){
            return(
                <>
                     <Button type="button" variant="secondary" size="sm" value="false" onClick={(e)=>{setShowInput(false)}}>
                            <i class="bi bi-box-arrow-left"></i>
                    </Button>
                    <label style={{fontSize:"10pt"}}>名称</label>
                    <input type="text" id={"category-id-"+props.obj['index']} 
                                style={{width: "120px", height: "26px", fontSize: "14px", marginRight:"30px", backgroundColor: setTextColor(props.obj)}}
                                readOnly={props.obj['delete_flag']}
                                defaultValue={props.obj['name']}  onChange={(e) => updateText(props.obj['index'], e)} 
                                ></input>
                    <label style={{fontSize:"10pt"}}>色</label>
                    <input type="color" id={"category_color"+props.obj['index']} defaultValue={props.obj['color']}
        					onChange={(e) => updateColor(props.obj['index'], e)} style={{marginLeft: "10px", width: "50px"}}></input>
                </>
            )
            
        } else {
            return (
                <>
                    <Button type="button" variant="secondary" size="sm" value="false" onClick={(e)=>{setShowInput(true)}}>
                        <i class="bi bi-pencil-square"></i>
                    </Button>
                    <div style={{width: "150px", height: "26px", fontSize: "14px",color: props.obj['color'],}}>{props.obj['name']}</div>
                </>
            )

        }
    }

    return(
        <div className="category-item"
            ref={setNodeRef}
            style={{backgroundColor: setColor(props.obj), 
                border: "1px solid rgba(0, 0, 0, 0.12)",
                transform: CSS.Transform.toString(transform),
                transition,
            }}
        >
            <div className="perspective-input gap-2">
                <div className="drag-handle" 
                    ref={setActivatorNodeRef}
                    {...attributes}
                    {...listeners}
                    style={{cursor: isDragging ? "grabbing" : "grab",}}
                >
                    <i class="bi-grip-horizontal"></i> 
                </div> 
                {categoryInput()}
                {setBadge(props.obj['id'])}
            </div>
            <ToggleButton type="checkbox" id={"delete-btn-"+props.obj['index']} className="btn btn-secondaryr"
                variant="secondary" data-bs-toggle="button" 
                size="x-sm" value={props.obj['id']} 
                onClick={(e) => setDelete(props.obj['index'],props.obj['id'], e)}
            >
                {setDeleteLabel(props.obj['delete_flag'])}
            </ToggleButton>


        </div>
    )
}





export default EditableCategoryList;