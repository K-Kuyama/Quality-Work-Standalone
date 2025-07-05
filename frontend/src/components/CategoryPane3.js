import React, { useState, useEffect } from 'react';

import Button from 'react-bootstrap/Button';
//import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
//import Tooltip from 'react-bootstrap/Tooltip';
import Popover from 'react-bootstrap/Popover';
import {DndContext} from '@dnd-kit/core';

import CategoryDefEditor from './CategoryDefEditor';
import LineCategoryDefEditor from './LineCategoryDefEditor';
import RegisteredActivities from './RegisteredActivities';
import {KeyWordButton, RegisteredKeyWordButton} from './KeyWordButton';
import DroppableArea from './DroppableArea';
import KeyWordSetter from './KeyWordSetter';

import Cookies from "universal-cookie";
import 'bootstrap-icons/font/bootstrap-icons.css';
import Settings from "../Settings";

function createPositiveList(word_info_list){
	let positive_list = [];
	word_info_list.map((w) =>{
		if(w.positive)
			positive_list.push(w);
	})
	return positive_list;
}

function createNegativeList(word_info_list){
	let negative_list = [];
	word_info_list.map((w) =>{
		if(!w.positive)
			negative_list.push(w);
	})
	return negative_list;
}



function CategoryPane3(props){
	//const [category, setCategory]=useState(props.category)
	const [haveData, setHaveData] = useState(false); 
	const [c_data, setCandidate] = useState([]);
	const [text_word, setTextWord] = useState("");
	
	//const [isVisible, setVisibility] = useState(false);
	
	const setDefChange = props.handler;
	
	// 指定されたカテゴリーの登録キーワードを取得する	
	useEffect(() =>{
		if(props.category.id != 0){
			let query = new URLSearchParams({category_id : props.category.id});
			let target = Settings.HOME_PATH+'/api/user_def/candidate_words/?'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/candidate_words/?'
			}
			fetch(target + query,{
					credentials: "same-origin",
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
				//console.log(res);			
				setCandidate(res);
				setHaveData(true);
				//console.log(haveData);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}
	},[props]);

	
	const setKeyWord =(title, flag) =>{
		// キーワードをデータベースに登録する
		let request_body = {category: props.category.id , word: title, positive: flag}
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		let target = Settings.HOME_PATH+'/api/user_def/CategorizedKeyword/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/CategorizedKeyword/'
		}
		fetch(target, {
			method : "POST",
			credentials: "same-origin",
			headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				},
			body : JSON.stringify(request_body)	
			}
		)
		.then(result =>{
			setTextWord("")
			if(document.getElementById("keyword_txt") != null){
				document.getElementById("keyword_txt").value="";
			}
			setDefChange(true);
			//console.log("set defChange")
		})
		.catch(error =>{
			console.error(error);
		})
	}
	
	
	const cancelKeyWord = (id) =>{
		// キーワードをデータベースから消去する
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		let target = Settings.HOME_PATH+'/api/user_def/CategorizedKeyword/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/CategorizedKeyword/'
		}
		fetch(target+id+"/", {
			method : 'DELETE',
			credentials: "same-origin",
			headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				}
			}
		)
		.then(result =>{
			setDefChange(true);
			//console.log("set defChange")
		})
		.catch(error =>{		
			console.error(error);
		})
	}
	
	// コンポーネントから呼び出されるキーワード設定用ハンドラー
	const setNewKeyWord =(flag) =>{
		setKeyWord(text_word, flag);
	}

	

	const handleTextChange = (e)=>setTextWord(e.target.value);
	
	// カテゴリーの設定を変更するための、ポップアップメニュー
	//const popover = (
  	//	<Popover id="popover-basic">
    //		<Popover.Header as="h3">カテゴリーの変更</Popover.Header>
    //		<Popover.Body>
    //			<CategoryDefEditor id={props.category.id} pid={props.pid} name={props.category.name} color={props.category.color} handler={setDefChange} /> 
    //    	</Popover.Body>
  	//	</Popover>
	//);


	const deleteCategory = (id) => {
		//カテゴリーのデータベースからの削除
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		let target = Settings.HOME_PATH+'/api/user_def/Category/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/Category/'
		}
		fetch(target+id+"/", {
			method : 'DELETE',
			credentials: "same-origin",
			headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				}	
			}
		)
		.then(response => {
			setDefChange(0);	
		})
		.catch(error =>{
			console.error(error);
		})

	
	}


// ドラッグ&ドロップ関連コード	


	// ドロップ時の処理。ドロップしたエリアによってflagを設定し、setKeyWordを呼び出す			
	function handleDragEnd(event){
		let flag = true;
		//console.log("Drag End", event);
		if(event.over == null){
			return;
			}
		if(event.over.id === "positive_area"){
			flag = true;
		}
		else if(event.over.id === "negative_area"){
			flag = false;
		}
		else {return;}
		if(event.active.id.length > 0){
			setKeyWord(event.active.id, flag);
		}

	}


	return(
		<div className="category_pane">

			<div className="ce_header">
					{/*
	    			<OverlayTrigger trigger="click" placement="left" overlay={popover}>
						<Button type="button" className="btn btn-ppheader" data-bs-toggle="button" size="sm" value="edit" >
    							変更
    					</Button>
    				</OverlayTrigger>
    				*/}
    			<LineCategoryDefEditor id={props.category.id} pid={props.pid} name={props.category.name} color={props.category.color} handler={setDefChange} /> 
    			<Button variant="secondary" className="btn btn-dlt-ppheader" size="sm" onClick={(e)=> deleteCategory(props.category.id)} > 削除 </Button>
			</div>
			
			<DndContext onDragEnd={handleDragEnd}>
			
			<div className="w_pane">
			
				<div className="r_pane">
					<div>
					<div style={{color: "white"}}>キーワード (キーワードが含まれている場合にこのカテゴリーと判断)</div>
					<DroppableArea id="positive_area">
						<div className="word_pane" >
							{createPositiveList(props.category.key_words).map((w) => {
								return(
									<RegisteredKeyWordButton wid={w.id} title={w.word} handler={cancelKeyWord} bg={props.category.color}/>
								);
							})}
						</div> 								{/* p_word_pane */}
					</DroppableArea>
					</div>
					<KeyWordSetter set_handler={setNewKeyWord} text_handler={handleTextChange} flag={true} />
				</div> 		{/* r_pane */}
				
				<div className="r_pane">
					<div>
					<div style={{color: "white"}}>NOT キーワード(キーワードが含まれている場合にこのカテゴリーではないと判断)</div>
					<DroppableArea id="negative_area">
						<div className="word_pane" >
							{createNegativeList(props.category.key_words).map((w) => {
								return(
									<RegisteredKeyWordButton  wid={w.id}  title={w.word} handler={cancelKeyWord}  bg="#808080"/>
								);
							})}
						</div>								 {/* ne_word_pane */}
					</DroppableArea>
					</div>
				<KeyWordSetter set_handler={setNewKeyWord} text_handler={handleTextChange} flag={false} />
				</div> 		{/* r_pane */}
				
			</div> 									 {/* w_pane */}
			<div style={{color: "white"}}>キーワード候補</div>
    		<div className="candidate_box">
    			{c_data.map((cdt) => {
					return(
						<KeyWordButton word={cdt.word} title={cdt.word}  handler={setKeyWord} bg="#3b5fcc" />
					);    				
    			})}			
    		</div>
    		
    		</DndContext>
    		<RegisteredActivities activities={props.category.activities} handler={setDefChange} />					
    	</div>
	)
}

export default CategoryPane3;