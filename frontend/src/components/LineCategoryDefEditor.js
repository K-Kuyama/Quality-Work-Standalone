import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
//import Accordion from 'react-bootstrap/Accordion';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function LineCategoryDefEditor(props){
	const [isVisible, setVisibility] = useState(false);
	//const [c_id, setCid] = useState(props.id);
	const [c_name, setName] = useState(props.name);
	const [c_color, setColor] = useState(props.color);
	//const [pid, setPerspective] = useState(props.pid)

	const handleText = (e) => setName(e.target.value);
	const handleColor = (e) => setColor(e.target.value);
	
	const handleChangeCategory = props.handler;
	
	// 保存ボタンが押された時のハンドラー
	const setCategoryInfo =()=>{
		console.log("perspective id -->",props.pid);
		if(props.id == '0'){
			// 新規カテゴリーの場合
			setCategory(props.pid, c_name, c_color, true);
		}
		else{
			setCategory(props.pid, c_name, c_color, false);
		}
		// setVisibility(false);
	};

	const setCategory = (p_id, c_name, c_color,  c_new) => {
		// カテゴリー情報をデータベースに保存
		// カテゴリー新規追加の場合はPOST、既存カテゴリー更新の場合はPATCHでサーバにアクセス
		let additional_str ="" ;
		let method_str = "POST";
		if(!c_new){
			additional_str =props.id+"/";
			method_str = "PATCH";
		}
		let request_body = {perspective: p_id, name: c_name, color: c_color};
		console.log(request_body);
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		fetch(Settings.HOME_PATH+"/api/user_def/Category/"+additional_str, {
			method : method_str,
			credentials: "same-origin",
			headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				},
			body : JSON.stringify(request_body)		
			}
		)
		.then(response => response.json())
		.then(result =>{
			//console.log("Category set result ", result);
			//console.log("res id=", result['id']);
			handleChangeCategory(result['id']);	
		})
		.catch(error =>{
			console.error(error);
		})
	}

/*
	const deleteCategory = (id) => {
		fetch("http://127.0.0.1:8000/api/user_def/Category/"+id+"/", {
			method : 'DELETE',
			headers: {'Content-Type' : 'application/json',}	
			}
		)
		.then(response => {
			handleChangeCategory(0);	
		})
		.catch(error =>{
			console.error(error);
		})

	
	}


	const setDeleteButton = ()=>{
		if(props.c_id == '0'){

			return(<></>);
		}
		else{
			return(
				<Button variant="primary" size="sm" style={{marginLeft: "20px"}} onClick={(e)=> deleteCategory(props.id)} > 削除 </Button>
			)
		}
	}
*/
	if(isVisible){
		return(
        					<div className="line_perspective_def_body">
        						<div className="p_info_setter">
        							<label style={{width: "24px"}}> 名称 </label>
        							<input type="text" id="perspective_name" style={{marginLeft: "10px", width: "160px"}} 
        								defaultValue={props.name} 
        								onChange={handleText} ></input>
        						</div> {/* p_info_setter */}
        						<div className="p_info_setter">
        							<div style={{marginLeft: "20px"}}> 色 </div>
        								<input type="color" id="perspective_color" defaultValue={props.color}
        									onChange={handleColor} style={{marginLeft: "10px", width: "80px"}}></input>
        						</div> {/* p_info_setter */}
        						<div className="p_info_middle">
        							<Button variant="secondary" size="x-sm" style={{margin: "6px", width: "50px", marginLeft: "20px"}} onClick={(e)=> setCategoryInfo()}> 
        								保存 </Button>
        						</div>
        						
        						<div className="lp_info_tail">
        							<Button variant="outline-light" size="x-sm" style={{margin: "6px", width: "80px"}} onClick={(e)=> setVisibility(false)}> <i class="bi bi-x-lg"></i> 閉じる</Button>
        						</div> 
        						{/* setDeleteButton() */}
        					</div>
		)
	} else {
		return(
			
				<Button type="button" className="btn btn-ppheader" data-bs-toggle="button" size="sm" onClick={(e)=> setVisibility(true)} >
    				変更
    			</Button>
    	
		)
	}


}

export default LineCategoryDefEditor;