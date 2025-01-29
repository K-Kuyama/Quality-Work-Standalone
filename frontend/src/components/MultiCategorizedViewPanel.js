import React, { useState, useEffect } from 'react';
import {lowerThanDateOnly} from "./utils";
import Button from 'react-bootstrap/Button';
import DatePicker, { registerLocale } from "react-datepicker";
import ja from 'date-fns/locale/ja';
import Settings from "../Settings";

/*
function getSelected(idx, target){
	if(idx == target){
		return "selected"
		}
}
*/

function MultiCategorizedViewPanel(props){

	const [target_date, setTDate] = useState(new Date());
	const [data, setData]= useState([]);
	const [haveData, setHaveData] = useState(false); 
	const [target_pid, setTPid] = useState();
	const [target_spid, setTSPid] = useState();

	const setDate = props.date_handler;
	const setPid = props.pid_handler;
	const setSubPid = props.spid_handler;
	
//	const getSelected = (idx, target) =>{
//		if(idx == target){
//			return "selected"
//		}
//	}

/*
	const handleDate =(e)=>{
		setDate(e.target.value);
	}

	const handlePid =(e)=>{
		setPid([e.target.value, getTitle(e.target.value)]);
	}
	const handleSubPid =(e)=>{
		setSubPid([e.target.value, getTitle(e.target.value)]);
	}
*/

	const getTitle = (n) => {
		for (const p of data){
			if(p['id'] == n){
				return p['name'];
			}	
		}
	};

	// パースペクティブ１の設定
	const setTargetPid = (d) =>{
		let p = d.target.value
		//console.log('set pid -->', p);
		setTPid(p);
		setPid([p, getTitle(p)]);
	};

	// パースペクティブ２の設定
	const setTargetSPid = (d) =>{
		let p = d.target.value
		//console.log('set pid -->', p);
		setTSPid(p);
		setSubPid([p, getTitle(p)]);
	};

	// このコンポーネントと親ページの両方の日時を設定
	// Datepickerの値の変更(onChange)で呼び出される	
	const setTargetDate = (d) =>{
		//console.log('set date -->', d);
		setTDate(d);		
		setDate(d);
	};
	
	// 日付を前日に設定する
	// prevボタンのクリックで呼び出される
	const setPrev = (e) =>{
		let new_date = new Date(target_date.getTime());
		new_date.setDate(new_date.getDate()-1);
		setTargetDate(new_date);
	}
	
	//日付を翌日に設定する
	// nextボタンのクリックで呼び出される
	const setNext = (e) =>{
		let new_date = new Date(target_date.getTime());
		new_date.setDate(new_date.getDate()+1);
		setTargetDate(new_date);
	}

	//指定された日が過去の日付かを判定する
	//過去の日付の場合にはTrueを返す
	const existNext=(d)=>{
		let today = new Date();
		let new_date = new Date(d.getTime());
		new_date.setDate(new_date.getDate());
		return lowerThanDateOnly(new_date, today);
	}



	useEffect(() => {
		// 初回の呼び出しでのみ、パースペクティブの一覧を取得する	
		if(!haveData){
			fetch(Settings.HOME_PATH+'/api/user_def/Perspective/',{
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
				setDate(new Date());
				//console.log("set pid =>",res[0]['id'] );
				setTPid(res[0]['id']);
				setPid([res[0]['id'], res[0]['name']]);
				//console.log("set sub pid =>",res[1]['id'] );
				setTSPid(res[1]['id']);
				setSubPid([res[1]['id'], res[1]['name']]);
				setHaveData(true);
			})
			.catch(error =>{
				console.error('----Error---');
				console.error(error);
			})
		}
		// 未来の日付にならないようにNextボタンをdisableにする処理
		// 日付がセットされており、かつすでにレンダリングがされている場合にのみ実行
		if(target_date != undefined && haveData){
			//onsole.log("exist? : ", existNext(target_date));
			let elem = document.getElementById("nxButton");
			if(existNext(target_date)){
				elem.disabled = false;
			}
			else{
				elem.disabled = true;
			}
		}
	},[target_date]);


	// DatePicker を日本語表示にするためにロケールを'ja'に設定
	registerLocale('ja', ja);

	if (!haveData) {
		return <div>Loading...</div>
	}else {
		return(
			<div className="categorized_view_panel">
			
				<div className="date_panel">
					<label className="date_title">日時</label>
					<div className="date_picker_panel">
						<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} id="pvButton"> <i class="bi bi-caret-left-fill"></i> </Button>
						<DatePicker dateFormat="yyyy/MM/dd" locale='ja' selected={target_date} className="r_datepicker" value={target_date} onChange={setTargetDate} />
						<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} id="nxButton"> <i class="bi bi-caret-right-fill"></i> </Button>
					</div>
				</div>

				<div className="item_panel">
					<label className="date_title" key="item_title-1">ビュー 1</label>
					<div className="c_select">
						{data.map((p, idx) =>{
							return(
								<label><input type="radio" name="perspectives1" id={"ps1-"+idx} value={p['id']} checked={p['id'] == target_pid} onChange={setTargetPid} />
						 		&nbsp;{p['name']} </label>
							)
						})}
					</div>	
				</div>

				<div className="item_panel">
					<label className="date_title" key="item_title-1">ビュー 2</label>
					<div className="c_select">
						{data.map((p, idx) =>{
							return(
								<label><input type="radio" name="perspectives2" id={"ps2-"+idx} value={p['id']} checked={p['id'] == target_spid} onChange={setTargetSPid} />
						 		&nbsp;{p['name']} </label>
							)
						})}
					</div>	
				</div>
	
			</div>
		)
	}
	
	
}

export default MultiCategorizedViewPanel;