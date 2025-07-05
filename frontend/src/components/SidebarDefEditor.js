import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import ToggleButton from 'react-bootstrap/ToggleButton';
import Badge from 'react-bootstrap/Badge';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function SidebarDefEditor(props){

	const createInitialItems = (data) =>{
		// propsで渡されたperspective情報データから表示用データを作成する
		// 特殊なカテゴライズモデルを持つものは除外
		/* id name color delete_flag  */
		let ret_data =[]
		//console.log("data:", data);
		if(data){
			let r_data = data.filter(function(item){
				return item['categorize_model']==null;
			});
			r_data.map((obj, idx) =>{
				ret_data.push({index: idx, id: obj['id'], name: obj['name'], color: obj['color'], delete_flag: false});
			})
		}
		return ret_data;
	}


	const [items, setItems] = useState([]);
	const setMenueChanged = props.handler;
	
	const saveInfo = (e) =>{
		// 設定保存用ハンドラー
		// データベースにperspectiveの変更を反映する
		console.log(items);
		const cookies = new Cookies();
		const token = cookies.get('csrftoken')
		let target = Settings.HOME_PATH+'/api/user_def/perspective_editor/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/perspective_editor/'
		}
		fetch(target,
			{
				method: "POST",
				credentials: "same-origin",
				headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				},
				body: JSON.stringify(items)
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
			setMenueChanged(true);
		})
		.catch(error =>{
			console.error('----Error---');
			console.error(error);
		})

	}

	//const handleColor =()=>{}
	
	const setColor = (obj) =>{
		// 削除ボタンが押されたものはバックグラウンドカラーを変更する
		//console.log("item", obj);
		let state = obj["delete_flag"];

		//console.log(" delete : ", state);
		if(state){
			return "#696969";
		} else{
			return "#575977";
		}
	}
	
	const setTextColor = (obj) =>{
		// 削除ボタンが押されたものはバックグラウンドカラーを変更する
		let state = obj["delete_flag"];
		if(state){
			return "#696969";
		} else{
			return "#fffafa";
		}

	}
		
		

	
		
	//const setNewItem = (e) =>{
	//	
	//}
	
	
	const addNewItem = (e)=>{
		// パースペクティブの新規追加ハンドラー
		setItems([...items, {index: items.length, id: null, name: "", color: "#fff", delete_flag: false}]);
	}


	
	
	const updateText = (idx, e)=>{
		// タイトルの変更ハンドラー
		console.log(e.target);
		setItems(
			items.map((item, index) => {
				if(index == idx){
					return{...item, name: e.target.value};
				} else {
					return item;
				}
			}))
	}


	const setDelete = (idx, id, e)=>{
		//削除ボタンが押された時のハンドラー
		if(id){updateState(idx, e);}
		else{deleteItem(idx);}
	}


	const deleteItem = (idx)=>{
		setItems(items.filter((item) => (item['index'] !== idx)));
	}	
	
	const updateState = (idx, e)=>{
		//console.log(e);
		//console.log("updateState",items);
		let sts = e.target.checked;
		setItems(
			items.map((item, index) => {
				if(index == idx){
					return{...item, delete_flag: !(item.delete_flag)};
				} else {
					return item;
				}
			}))
		//console.log("update items",items);
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
	
	/* 使われなくなった */
	//const setReadOnly = (flag) =>{
	//	if(flag){ return ("readonly");}
	//	else { return("");}
	//}
	
	useEffect(() => {
		setItems(createInitialItems(props.data));
	},[props]);
	
	
	return(
		<div calssName="sidebar_def_editor">
			<div className="pp_header">
				<Button type="button" className="btn btn-ppheader" data-bs-toggle="button" variant="primary" size="sm" value="save" 
					onClick={(e)=>saveInfo(e)}>
    					保存
    			</Button>
    		</div>
			<div className="d-grid gap-2">
				{items.map((obj) =>{if(obj){
					return(
						<div className="perspective-item" name="perspective-item-" style={{backgroundColor: setColor(obj)}}>
							<div className="perspective-input gap-2">
        						{/* <input type="color" id={"perspective_color-"+obj['index']} readOnly={obj['delete_flag']}
        							defaultValue={obj['color']} onChange={handleColor} style={{width: "30px"}}></input>		*/}			
								<input type="text" id={"perspective-id-"+obj['index']} 
								style={{width: "150px", height: "26px", fontSize: "14px", backgroundColor: setTextColor(obj)}} readOnly={obj['delete_flag']}
        								defaultValue={obj['name']}  onChange={(e) => updateText(obj['index'], e)} 
        								></input>
        						{setBadge(obj['id'])}
        					</div>
        					<ToggleButton type="checkbox" id={"delete-btn-"+obj['index']} className="btn btn-secondaryr" variant="secondary" data-bs-toggle="button" size="x-sm" value={obj['id']} onClick={(e) => setDelete(obj['index'],obj['id'], e)}>
    							{setDeleteLabel(obj['delete_flag'])	}
    						</ToggleButton>
						</div>
					)}						
				})}

				<Button type="button" class="btn btn-secondary"  variant="dark" size="sm" 
    					value="0" onClick={(e) => addNewItem(e)}  style={{width: "34%"}}>
    							+ 新規追加
    			</Button>
			</div> {/* d-grid */}
		</div>	
	)

}




export default SidebarDefEditor;