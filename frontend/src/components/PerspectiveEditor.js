import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import ActivitySelector from "./ActivitySelector"
import TopBarControlPanel from "./TopBarControlPanel";
import CategoryEditor from "./CategoryEditor";
import CategoryTabs from "./CategoryTabs";
import EditableCategoryList from "./EditableCategoryList";
import PerspectiveModelViewSettings from "./PerspectiveModelViewSettings";
import LMTable from "./LMTable";

import Settings from "../Settings";

function PerspectiveEditor(props){

	const [p_id, setId] = useState(props.pid);
	const [def, setDef]= useState({});  /* perspectiveの設定情報 */
	const [def_change, setDefChange] = useState(false)  /* perspectiveの設定情報が変更された時のフラグ */
	const [current, setCurrent] = useState(1); /* ActivitySelectorが表示しているページ*/
	const [haveData, setHaveData] = useState(false); 

	const [target_date, setDate] = useState(new Date());
	const [item, setItem] = useState("event_list");

	const [mode, setMode] = useState(null);

	/* 編集画面の表示・非表示をコントロールするフラグ*/
	const [showA, setA] = useState(false);
	const [showC, setC] = useState(false);

		/* 上位ページから引き継がれるハンドラー */
	const handleChangePerspective = props.handler;
	const setShowModal = props.modal_handler;

	const setModel = (item)=>{
		//console.log(item);
		setMode(item);
	}

	useEffect(() =>{
		// パースペクティブと関連情報を取得する

		if(props.p_id != 0){
			let target = Settings.HOME_PATH+'/api/user_def/_Perspective/'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/_Perspective/'
			}		
			fetch(target+ props.p_id +'/',{
					credentials: "same-origin",
				}
			)
			.then(response => {
				return response.json();
			})
			.then(result =>{
				const txt = JSON.stringify(result, null,' ');
				let res = JSON.parse(txt);
				console.log(res);			
				setDef(res);
				setMode(res['categorize_model']);
				setHaveData(true);
				setDefChange(false);
				handleChangePerspective(false);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}

	},[props, p_id, def_change]);
	


	
	/* コントロールパネルに渡される日付、アイテム設定用ハンドラー */
    const setParams = (date_str, item_str) => {
    	console.log("PerspectiveEditor setParams", date_str, item_str);
        setDate(date_str.target_date);
        setItem(item_str.target_item);
    }

	const showModal = (e) =>{
		console.log("button clicked");
		setShowModal(true);
	}


	/*****************************  編集画面用　*****************************/

	const showAedit = (e) =>{
		setA(true);
		setC(false);
	}

	const showCedit = (e) =>{
		setA(false);
		setC(true);
	}

	const hideAedit = (e) =>{
		setA(false);
	}

	const hideCedit = (e) =>{
		setC(false);
	}
	
	/****  レンダリング用関数　*****/


	const editAButton = () =>{
		//if(mode != 'PerspectiveModel'){
		if(mode == 'AIPerspectiveModel' || mode == "AIPerspectiveModelHighPossibility"){
			if(showA == true){
				return (
					<Button className="btn-sm" variant="light" onClick={hideAedit}>登録済みアクティビティ　 <i class="bi bi-caret-up"></i> </Button>
				)
			} else {
				return (
					<Button className="btn-sm" variant="outline-light" onClick={showAedit}>登録済みアクティビティ　 <i class="bi bi-caret-down"></i> </Button>
				)
			}
		}
	}

	const editCButton = () =>{
		if(showC == true){
			return (
				<Button className="btn-sm" variant="light" onClick={hideCedit}>カテゴリーの編集　  <i class="bi bi-caret-up"></i> </Button>
			)
		} else {
			return (
				<Button className="btn-sm" variant="outline-light" onClick={showCedit}>カテゴリーの編集　  <i class="bi bi-caret-down"></i> </Button>
			)
		}
	}


	

	const activityList = () =>{
		if(showA == true){
			return(
				<>
					<div className="registered-pane">
						<CategoryTabs data={def} handler={setDefChange} p_kind={mode} />
					</div>
				</>
			)
		}
	}

	const categoryList = () =>{
		if(showC == true){
			return(
				<EditableCategoryList pid={props.p_id} handler={setDefChange}/>
			)
		}
	}


	const categoryEditor = () =>{
		//if(mode == 'PerspectiveModel'){
		if(mode == 'PerspectiveModel' || mode == null){
			return(
				<div className="category_field">
					<CategoryEditor data={def} handler={setDefChange} p_kind={mode} />
				</div>
			)
		}
	}

	/**********************************************/
	if(props.p_id == 0){
		return(
		<div className="perspective_editor" style={{width:"90%"}}>
			パースペクティブが定義されていません。左の「編集」ボタンを押してパースペクティブを定義してください。
		</div>
		)
	}else if (!haveData) {
		return <div>Loading...</div>
	}else{
		return(
		<div className="perspective_editor">
			<div className="perspective_top">
				<div></div>
				<div className="perspective_name"> {def['name']}</div>
				<PerspectiveModelViewSettings p_id={props.p_id} p_kind={mode} handler={setModel} />
			</div>
			<div id="controls" className="top_bar_panel">
				<div className="top_bar_control">
					<TopBarControlPanel date_handler={setDate} item_handler={setItem} page_handler={setCurrent} />
				</div>
			</div>
			<ActivitySelector data={def} target_date={target_date} item={item} handler={setDefChange} page_handler={setCurrent} p_id={props.p_id} current={current} />
			
			<div className="pe_tail">
				{editCButton()}
				{editAButton()}
			</div>
			{activityList()}
			{categoryList()}
			<hr size="8" width="100%" color="white"></hr>
			{categoryEditor()}
			<LMTable p_id={props.p_id} p_kind={mode} handler={setDefChange}/>
		</div>
		)	
	}

}

export default PerspectiveEditor;