//import React, { useState, useEffect } from 'react';

import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';

import CategoryPane3 from './CategoryPane3';


function CategoryEditor(props){
	// タブを使ったカテゴリー分類のための情報を設定する画面
	// props.data perspectiveの設定情報が渡される

	const setDefChange = props.handler; /* CategoryPaneに渡され、PerspectiveEditorに状態の変化を伝える。*/
	
	
	if(props.data["categories"].length > 0){
		//let categories = props.data["categories"];

		return(
			<Tabs defaultActiveKey="0" id={"category-tab"+props.data["id"]} className="mb-0" >
    			{props.data["categories"].map((c,ix)=>{
    				return(
    					<Tab eventKey={ix} title={c.name}>
    						<CategoryPane3 category={c} pid={props.data["id"]} p_kind={props.p_kind} handler={setDefChange}/>	
      					</Tab>
    				)})}
    		</Tabs>
		);
	}
	else{
		return(
			<div className="editor-message-line">
				<label className="editor-message">カテゴリーはまだ設定されていません</label>
			</div>
		)
	}
}

export default CategoryEditor;