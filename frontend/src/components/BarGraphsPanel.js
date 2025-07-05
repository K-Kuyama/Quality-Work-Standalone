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

//バーグラフ用の操作パネル
// 日付選択とパースペクティブ選択の機能を持つ

function BarGraphsPanel(props){

	const [target_date, setTDate] = useState(new Date());
	const [target_pid, setTPid] = useState();
	const [data, setData]= useState([]);
	const [haveData, setHaveData] = useState(false); 

	const setDate = props.date_handler;
	const setPid = props.pid_handler;
	const setSubPid = props.spid_handler;
	
//	const getSelected = (idx, target) =>{
//		if(idx == target){
//			return "selected"
//		}
//	}

	// このコンポーネントと親ページの両方の日時を設定
	// Datepickerの値の変更(onChange)で呼び出される
	
	const setTargetDate = (d) =>{
		//let sd = getBothEnds(d, props.kind_of_period);
		console.log('set date -->', d);
		setTDate(d);		
		setDate(d);
	};
	
	const setTargetPid = (d) =>{
		let p = d.target.value
		console.log('set pid -->', p);
		setTPid(p);
		setPid([p, getTitle(p)]);
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

//	const handleDate =(e)=>{
//		setDate(e.target.value);
//	}

//	const handlePid =(e)=>{
//		setPid([e.target.value, getTitle(e.target.value)]);
//	}
//	const handleSubPid =(e)=>{
//		setSubPid([e.target.value, getTitle(e.target.value)]);
//	}


	const getTitle = (n) => {
		for (const p of data){
			if(p['id'] == n){
				return p['name'];
			}	
		}
	};


	useEffect(() => {
		// 初回の呼び出しでのみ、パースペクティブの一覧を取得する	
		if(!haveData){
			let target = Settings.HOME_PATH+'/api/user_def/Perspective/'
			if(Settings.DEVELOP){
				target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/Perspective/'
			}
			fetch(target,{
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
				//console.log(res[0]['id'] );
				//console.log(res[1]['id'] );
				//console.log(res[2]['id'] );
				//setTargetPid(res[0]['id']);
				setPid([res[0]['id'], res[0]['name']]);
				setTPid(res[0]['id']);
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
			//console.log("exist? : ", existNext(target_date));
			let elem = document.getElementById("nxButton");
			if(existNext(target_date)){
				elem.disabled = false;
			}
			else{
				elem.disabled = true;
			}
		}
	},[target_date, target_pid]);
	
	
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
					<label className="date_title" key="item_title-1">ビュー</label>
					<div className="c_select">
						{data.map((p, idx) =>{
							return(
								<label><input type="radio" name="perspectives" id={"ps-"+idx} value={p['id']} checked={p['id'] == target_pid} onChange={setTargetPid} />
						 		&nbsp;{p['name']} </label>
							)
						})}
					</div>
				</div>

			</div>
		)
	}
	
	
}

export default BarGraphsPanel;