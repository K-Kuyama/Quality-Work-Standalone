//import React, { useState, useEffect } from 'react';

import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';

import CategoryPane3 from './CategoryPane3';
import CategoryDefEditor from './CategoryDefEditor';

/*
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
*/

function CategoryEditor(props){
	// props.data perspectuveの設定情報が渡される

//	const [def, setDef]= useState(props.data);  /* perspectiveの設定情報 */
//	const [default_c, setDefaultC]=useState(props.data["categories"][0])
//	const [tabKey, setTabKey] = useState(props.data["categories"][0].id)
//	console.log("props def : ", props.data)
	
	const setDefChange = props.handler; /* CategoryPaneに渡され、PerspectiveEditorに状態の変化を伝える。*/
	
	
//	useEffect(() =>{
//		console.log("=== props.def =>", props.data['categories']);
//	},[props])
	
	//console.log("perspective id ==>", props.data["id"]);	
	if(props.data["categories"].length > 0){
		//let categories = props.data["categories"];

		return(
			<Tabs defaultActiveKey="0" id={"category-tab"+props.data["id"]} className="mb-0" >
    			{props.data["categories"].map((c,ix)=>{
    				return(
    					<Tab eventKey={ix} title={c.name}>
    						<CategoryPane3 category={c} pid={props.data["id"]} handler={setDefChange}/>	
      					</Tab>
    				)})}
    			<Tab eventKey={props.data["categories"].length} title="＋新規追加">
    			 	<CategoryDefEditor id="0" pid={props.data["id"]} name="新規カテゴリー" color="" handler={setDefChange} /> 
    			</Tab>
    		</Tabs>
		);
	}
	else{
		return(
			<Tabs
      				defaultActiveKey="0"
      				id="category-tab"
      				className="mb-3"
    			>
    			<Tab eventKey="0" title="＋新規追加">
    			 <CategoryDefEditor id="0" pid={props.data["id"]} name="新規カテゴリー" color="" handler={setDefChange} />  
    			</Tab>
    		</Tabs>
			
		)
	}
}

export default CategoryEditor;