import React from 'react';
import Button from 'react-bootstrap/Button';
import {useDraggable} from '@dnd-kit/core';
import {CSS} from '@dnd-kit/utilities';
import 'bootstrap-icons/font/bootstrap-icons.css';

function KeyWordButton(props){
	// キーワード候補を表示するボタン
	
	const {attributes, listeners, setNodeRef, transform} = useDraggable({
    	id: props.word,
  	});
  
  	const style = {
    	transform: CSS.Translate.toString(transform),
  	}; 
  
 	return(
		<div className="keyword_button" style={style} ref={setNodeRef} {...listeners} {...attributes}>

			<label> {props.title} </label>

		</div>
	)
	 
//	return(
//		<div className="keyword_button" style={style} ref={setNodeRef} {...listeners} {...attributes}>
//			<Button  className="btn btn-circle" style={{padding: "0px"}} onClick={(e) => setKeyWord(props.word, true)} 
//				style={{backgroundColor: props.bg, borderColor: props.bg}}> <i class="bi bi-plus-circle"></i> </Button>
//			<label> {props.title} </label>
//			<Button className="btn btn-circle" style={{padding: "0px"}} onClick={(e) => setKeyWord(props.word, false)} 
//				style={{backgroundColor: props.bg, borderColor: props.bg}}> <i class="bi bi-dash-circle"></i> </Button>
//		</div>
//	)
	
}

function RegisteredKeyWordButton(props){
	// 登録されたキーワードを表示するボタン
	// 右側に削除用のxボタンを付ける
	const cancelKeyWord = props.handler;	
	
	return(
		<div className="registered_keyword_button" style={{backgroundColor: props.bg, borderColor: props.bg}}>
			<label style={{marginLeft: "6px"}}> {props.title} </label>
			<Button className="btn registered_btn-circle"  onClick={(e) => cancelKeyWord(props.wid)} 
				style={{padding: "0px", backgroundColor: props.bg, borderColor: props.bg}}> <i class="bi bi-x-circle"></i> </Button>
		</div>
	)
	
}


export {KeyWordButton, RegisteredKeyWordButton};