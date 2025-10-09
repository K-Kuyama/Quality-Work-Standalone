//import React, { useState, useEffect } from 'react';

import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';


import RegisteredActivities from './RegisteredActivities';


function CategoryTabs(props){
	// 学習モデルを使う場合にのみ使われる。
	// 登録済みアクティビティをタブを使って表示する。
	
	const setDefChange = props.handler; /* CategoryPaneに渡され、PerspectiveEditorに状態の変化を伝える。*/
	
	if(props.data["categories"].length > 0){
		//let categories = props.data["categories"];

		return(
			<Tabs defaultActiveKey="0" id={"category-tab"+props.data["id"]} className="mb-0" >
    			{props.data["categories"].map((c,ix)=>{
    				return(
    					<Tab eventKey={ix} title={c.name}>
							<div className="category_pane">
    							<RegisteredActivities no_accordion={true} activities={c.activities} handler={setDefChange} />	
							</div>
						</Tab>
    				)})}
    		</Tabs>
		);
	}
	else{
		return(<></>)
	}
}

export default CategoryTabs;