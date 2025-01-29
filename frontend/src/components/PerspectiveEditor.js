import React, { useState, useEffect } from 'react';
import ActivitySelector from "./ActivitySelector"
import TopBarControlPanel from "./TopBarControlPanel";
import CategoryEditor from "./CategoryEditor";
/* import PerspectiveDefEditor from "./PerspectiveDefEditor"; */
//import Tab from 'react-bootstrap/Tab';
//import Tabs from 'react-bootstrap/Tabs';
import Settings from "../Settings";

function PerspectiveEditor(props){

	const [p_id, setId] = useState(props.pid);
	const [def, setDef]= useState({});  /* perspectiveの設定情報 */
	const [def_change, setDefChange] = useState(false)  /* perspectiveの設定情報が変更された時のフラグ */
	const [current, setCurrent] = useState(1); /* ActivitySelectorが表示しているページ*/
	const [haveData, setHaveData] = useState(false); 

	const [target_date, setDate] = useState(new Date());
	const [item, setItem] = useState("event_list");


	useEffect(() =>{
		//console.log(" p_id set .........")
		//console.log(p_id)
		if(props.p_id != 0){
			fetch(Settings.HOME_PATH+'/api/user_def/_Perspective/'+ props.p_id +'/',{
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
				setDef(res);
				//console.log("set def",def);
				setHaveData(true);
				//console.log(haveData);
				setDefChange(false);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}

	},[props, p_id, def_change]);
	

	/* 上位ページから引き継がれるハンドラー */
	const handleChangePerspective = props.handler;
	
	/* コントロールパネルに渡される日付、アイテム設定用ハンドラー */
    const setParams = (date_str, item_str) => {
    	console.log("PerspectiveEditor setParams", date_str, item_str);
        setDate(date_str.target_date);
        setItem(item_str.target_item);
    }


	if(props.p_id == 0){
		return(
		<div className="perspective_editor" style={{width:"90%"}}>
			{/*<PerspectiveDefEditor p_id="0" name="新規パースペクティブ" color="" handler={handleChangePerspective} />*/}
			パースペクティブが定義されていません。左の「編集」ボタンを押してパースペクティブを定義してください。
		</div>
		)
	}else if (!haveData) {
		return <div>Loading...</div>
	}else{
		return(
		<div className="perspective_editor">
			<div className="perspective_name"> {def['name']}</div>
			{/* <PerspectiveDefEditor p_id={def['id']} name={def['name']} color={def['color']} handler={handleChangePerspective} /> */}
			<div id="controls" className="top_bar_panel">
				<div className="top_bar_control">
					<TopBarControlPanel date_handler={setDate} item_handler={setItem} page_handler={setCurrent} />
				</div>
			</div>
			{/*console.log("test def value", def)*/}
			<ActivitySelector data={def} target_date={target_date} item={item} handler={setDefChange} page_handler={setCurrent} p_id={props.p_id} current={current} />
			<div className="category_field">
				{/* console.log("test def value", def)*/}
				<CategoryEditor data={def} handler={setDefChange}/>
			</div>			
		</div>
		)	
	}

}

export default PerspectiveEditor;