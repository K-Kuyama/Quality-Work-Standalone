import React, { useState, useEffect } from 'react';
import {lowerThanDateOnly} from "./utils";
import Button from 'react-bootstrap/Button';
import DatePicker, { registerLocale } from "react-datepicker";
import ja from 'date-fns/locale/ja';
//import "react-datepicker/dist/react-datepicker.css"


function InputOperationPanel(props){


	const [date, setDate] = useState();

	const setTDate = props.date_handler;
	// const setPn = props.pn_handler;

	// このコンポーネントと親ページの両方の日時を設定
	// Datepickerの値の変更(onChange)で呼び出される
	const setTargetDate = (d) =>{
		//let sd = getBothEnds(d, props.kind_of_period);
		//console.log(d);
		setTDate(d);		
		setDate(d);
	};

	//const setParam = (d) =>{
		//let sd = getBothEnds(d, props.kind_of_period);
	//	setDate(d);
	//	setTDate(d);
	//};


	// prevボタンのクリックで呼び出される
	// 時間種別ごとに進める時間を決定する
	const setPrev = (e) =>{
		let new_date = new Date(date.getTime());
		if(props.kind_of_period ==="week"){
			new_date.setDate(new_date.getDate()-7);
		}
		else if(props.kind_of_period === "month"){
			new_date.setMonth(new_date.getMonth()-1);
		}
		else if(props.kind_of_period === "year"){
			new_date.setFullYear(new_date.getFullYear()-1);
		}
		else {
			new_date.setDate(new_date.getDate()-1);
		}
		setTargetDate(new_date);
	}
	
	
	// nextボタンのクリックで呼び出される
	// 時間種別ごとに進める時間を決定する
	const setNext = (e) =>{
		let new_date = new Date(date.getTime());
		if(props.kind_of_period === "week"){
			new_date.setDate(new_date.getDate()+7);
		}
		else if(props.kind_of_period === "month"){
			new_date.setMonth(new_date.getMonth()+1);
		}
		else if(props.kind_of_period === "year"){
			new_date.setFullYear(new_date.getFullYear()+1);
		}
		else {
			new_date.setDate(new_date.getDate()+1);
		}		
		setTargetDate(new_date);
	}


	//指定された日が過去の日付かを判定する
	//過去の日付の場合にはTrueを返す
	const existNext=(d)=>{
		let today = new Date();
		let new_date = new Date(d.getTime());
		if (props.kind_of_period === "week"){
			new_date.setDate(new_date.getDate()+6);
		}
		if (props.kind_of_period === "month"){
			new_date.setMonth(new_date.getMonth());
		}
		if (props.kind_of_period === "year"){
			new_date.setFullYear(new_date.getFullYear());
		}
		else {
			new_date.setDate(new_date.getDate());
		}
		return lowerThanDateOnly(new_date, today);
	}

								
	// Nextボタンの状態を未来には進めないようにセット。
	// target_dateが変更され、変更された日付が本日以降であればNextボタンを
	// disableする。
	// もし日付が設定されていなければ、本日に設定
	useEffect(() => {
		//console.log("date->", date);
		if(date == undefined){
			setTargetDate(new Date());
		}
		else{
			//console.log("exist? : ", existNext(date));
			let elem = document.getElementById("nxButton");
			if(existNext(date)){
				elem.disabled = false;
			}
			else{
				elem.disabled = true;
			}
		}
	},[date]);



	// DatePicker を日本語表示にするためにロケールを'ja'に設定
	registerLocale('ja', ja);

	
	
	if(props.kind_of_period ==="week"){
		return(
				<div className="date_picker_panel">
					<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} id="pvButton"> <i class="bi bi-caret-left-fill"></i> </Button>
					<DatePicker dateFormat="yyyy/MM/dd" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} showWeekPicker />
					<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} id="nxButton"> <i class="bi bi-caret-right-fill"></i> </Button>
				</div>
		)
	}
	else if(props.kind_of_period ==="month"){
		return(
				<div className="date_picker_panel">
					<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} id="pvButton"> <i class="bi bi-caret-left-fill"></i> </Button>
					<DatePicker dateFormat="yyyy/MM" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} showMonthYearPicker />
					<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} id="nxButton"> <i class="bi bi-caret-right-fill"></i> </Button>
				</div>
		)
	}
	else if(props.kind_of_period ==="year"){
		return(
				<div className="date_picker_panel">
					<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} id="pvButton"> <i class="bi bi-caret-left-fill"></i> </Button>
					<DatePicker dateFormat="yyyy" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} showYearPicker />
					<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} id="nxButton"> <i class="bi bi-caret-right-fill"></i> </Button>
				</div>
		)
	}
	else{
		return(
				<div className="date_picker_panel">
					<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} id="pvButton"> <i class="bi bi-caret-left-fill"></i> </Button>
					<DatePicker dateFormat="yyyy/MM/dd" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} />
					<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} id="nxButton"> <i class="bi bi-caret-right-fill"></i> </Button>
				</div>
		)
	}


	
/*	
	return(
			<div className="date_picker_panel">
				<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} > <i class="bi bi-caret-left-fill"></i> </Button>
				{
				!function(){
					if(props.kind_of_period =="day"){
						return(
							<DatePicker dateFormat="yyyy/MM/dd" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} />
						)
					}
					else if(props.kind_of_period =="week"){
						return(
							<DatePicker dateFormat="yyyy/MM/dd" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} showWeekPicker />
						)
					}
					else if(props.kind_of_period =="month"){
						return(
							<DatePicker dateFormat="yyyy/MM" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} showMonthYearPicker />
						)
					}
					else if(props.kind_of_period =="year"){
						return(
							<DatePicker dateFormat="yyyy" locale='ja' selected={date} className="r_datepicker" value={date} onChange={setTargetDate} showYearPicker />
						)
					}
				}()
				}
				<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} > <i class="bi bi-caret-right-fill"></i> </Button>
			</div>
	)

*/


}

export default InputOperationPanel;