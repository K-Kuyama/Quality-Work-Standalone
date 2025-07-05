import React, { useState, useEffect, useContext } from 'react';
//import ControlPanel from "./ControlPanel";
import Pagination from "./Pagination";
import ActivityCheckList from "./ActivityCheckList";
import CategoryButtonList from "./CategoryButtonList";
import { getBothEnds } from "./utils";
import { ShowPolicyContext } from '../Context';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function ActivitySelector(props){

	//const [def, setDef]= useState(props.data);  
	//const [p_id, setPid] = useState(props.p_id);
	const [ev_data, setEvData]= useState([]);
	const [haveData, setHaveData] = useState(false); 
	//const [target_date, setDate] = useState(props.target_date);
	const [item, setItem] = useState(props.item);
	const ctx = useContext(ShowPolicyContext);
	const clearCheck = props.handler;
	const setCurrent = props.page_handler;

	const setCategory = (e) =>{
		let activities = document.querySelectorAll("input[name=a_item]:checked")
		//console.log("selected =>", activities);
		//console.log("categorize =>", e.target.value);
		//console.log("selected activities=>", activities)
		let request_body = []
		for (const act of activities){
			//console.log(act)
			//console.log(act.getAttribute('data-app'))
			request_body.push({category: e.target.value, app: act.getAttribute('data-app'), title: act.getAttribute('data-title')})
		}
		console.log("request body=>", request_body)
		if(activities.length > 0){
			let cookies = new Cookies();
			let token = cookies.get('csrftoken')
			let target = Settings.HOME_PATH+'/api/user_def/bulk_c_activity/'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/bulk_c_activity/'
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
				for (const cbx of activities){cbx.checked = false}
				clearCheck(true);

			})
			.catch(error =>{
				console.error(error);
			})
		}
		
	}
	
	const cancelCategory = (e) => {
		let activities = document.querySelectorAll("input[name=a_item]:checked")
		let request_body = []
		for (const act of activities){
			request_body.push(act.value)
		}
		if(activities.length > 0){
			let cookies = new Cookies();
			let token = cookies.get('csrftoken')
			let target = Settings.HOME_PATH+'/api/user_def/delete_c_activity/'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/delete_c_activity/'
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
				for (const cbx of activities){cbx.checked = false}
				clearCheck(true);
	
			})
			.catch(error =>{
				console.error(error);
			})
		}
	}

/* アクティビティデータを取得する　*/
	useEffect(() => {
		//setDate(props.target_date);
		setItem(props.item);
		//console.log("==========");
		//console.log("State ");
		//console.log(props.target_date);
		//console.log(item);
		//console.log("==========");
		let date = new Date(props.target_date);
		let both_ends = getBothEnds(date);
		let d1 = both_ends[0];
		let d2 = both_ends[1];
		let policy = ctx.policy;
		let params = {};
		if(props.item ==="title_list"){
			params = {start : d1, end : d2, show_policy : policy, pagination : 'True', p_id : props.p_id, merged_item: 'title', sorted_by: 'duration'};
		} else if(props.item === "app_list"){
			params = {start : d1, end : d2, show_policy : policy, pagination : 'True', p_id : props.p_id, merged_item: 'app', sorted_by: 'duration'};
		}else{
			params = {start : d1, end : d2, show_policy : policy, pagination : 'True', p_id : props.p_id, sorted_by: 'time'};
		}
		//キーワード、アイテム設定時にページが変わるのを防ぐため、handleReloadの時に保持していた表示するページを指定する
		params.page = props.current; 
		
		let query = new URLSearchParams(params);
		let target = Settings.HOME_PATH+'/api/Activity/categorized_event/?'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/categorized_event/?'
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
			setEvData(res);
			//console.log('-----current---------');
			//console.log(res['current']);
			//console.log('---------------------');
			setCurrent(res['current']);
			//console.log(ev_data);
			setHaveData(true);
			//console.log(haveData);
			clearCheck(false);
		})
		.catch(error =>{
			setHaveData(false);
			console.error('----Error---');
			console.error(error);
		})
	
	},[props]);


	/* コントロールパネルに渡される日付、アイテム設定用ハンドラー */
//    const setParams = (date_str, item_str) => {
//        setDate(date_str.target_date);
//        setItem(item_str.target_item);
//    }


	/* ページネーションの「前へ」「次へ」クリック時に呼び出されるハンドラー */
	const handleReload = (target) => {
		if(target){
			fetch(target)
			.then(response => {
				return response.json();
			})
			.then(result =>{
				const txt = JSON.stringify(result, null,' ');
				//console.log('---Success ---');
				//console.log(txt);
				let res = JSON.parse(txt);
				setEvData(res);
				//console.log('-----current---------');
				//console.log(res['current']);
				//console.log('---------------------');
				setCurrent(res['current']); /* 現在のページを保存しておく*/
				setHaveData(true);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}
	}
	
	

	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
				<div className="evtable">	
					<Pagination response={ev_data} handler={handleReload} />
					<ActivityCheckList response={ev_data["results"]} /> 
					<CategoryButtonList def={props.data} handler={setCategory} c_handler={cancelCategory}/>
				</div>
//			</div>
		);
	}

}

export default ActivitySelector;