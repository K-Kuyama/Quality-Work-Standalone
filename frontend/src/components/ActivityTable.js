import React, { useState, useEffect } from 'react';
import Pagination from "./Pagination";
import Activities from "./Activities";
import { getBothEnds } from "./utils"
//import Cookies from "universal-cookie";
import Settings from "../Settings";

function ActivityTable(props){

	const [data, setData]= useState([]);
	const [haveData, setHaveData] = useState(false); 
	const [target_date, setDate] = useState(props.target_date);
	const [item, setItem] = useState(props.item);
	
	//console.log("-----------");	
	//console.log("props");
	//console.log(props.target_date);
	//console.log(props.item);
	//console.log("State ");
	//console.log(target_date);
	//console.log(item);
	//console.log("-----------");
	
	/* propsに変更があった時に呼び出される */
	useEffect(() => {
		setDate(props.target_date);
		setItem(props.item);
		//console.log("==========");
		//console.log("State ");
		//console.log(target_date);
		//console.log(item);
		//console.log("==========");
		// 表示すべきターゲットデートがない場合は、サーバへの呼び出しをしない。
		if(target_date){		
			let date = new Date(props.target_date);
			let both_ends = getBothEnds(date);
			let d1 = both_ends[0];
			let d2 = both_ends[1];
			let params = {};
			if(props.item ==="title_list"){ /* 画面タイトル一覧の場合 */
				params = {start : d1, end : d2, pagination : 'True', merged_item: 'title', sorted_by: 'duration'};
			} else if(props.item === "app_list"){ /* アプリケーション一覧の場合 */
				params = {start : d1, end : d2, pagination : 'True', merged_item: 'app', sorted_by: 'duration'};
			}else{　/* イベント一覧の場合 */
				params = {start : d1, end : d2, pagination : 'True', sorted_by: 'time'};
			}
			let query = new URLSearchParams(params);
			//const cookies = new Cookies();
			//const token = cookies.get('csrftoken')
			fetch(Settings.HOME_PATH+'/api/Activity/merged_event/?'+ query,{
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
				setData(res);
				setHaveData(true);
			})
			.catch(error =>{
				setHaveData(false);
				console.error('----Error---');
				console.error(error);
			})
		}
	},[props]);

	// 前、もしくは次のpaginationされたデータを取得する
	// targetには、URLがセットされる
	const handleReload = (target) => {
		if (target){
			fetch(target)
			.then(response => {
				return response.json();
			})
			.then(result =>{
				const txt = JSON.stringify(result, null,' ');
				//console.log('---Success ---');
				//console.log(txt);
				let res = JSON.parse(txt);
				setData(res);
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
				<Pagination response={data} handler={handleReload} />
				<Activities response={data["results"]} /> 	
			</div>
		);
	}
}

export default ActivityTable;
