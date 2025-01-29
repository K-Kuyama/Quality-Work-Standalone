import React, { useState, useEffect } from 'react';
import {lowerThanDateOnly} from "./utils";
import Button from 'react-bootstrap/Button';
import DatePicker, { registerLocale } from "react-datepicker";
import ja from 'date-fns/locale/ja';




function AllGraphControlPanel(props){

	const [target_date, setDate] = useState();

	const setTDate = props.date_handler;
	//const setTItem = props.item_handler;
	
	const setTargetDate = (d) =>{
		//let sd = getBothEnds(d, props.kind_of_period);
		//console.log(d);
		setTDate(d);		
		setDate(d);
	};
	
	
	const setPrev = (e) =>{
		let new_date = new Date(target_date.getTime());
		new_date.setDate(new_date.getDate()-1);
		setTargetDate(new_date);
	}
	
	const setNext = (e) =>{
		let new_date = new Date(target_date.getTime());
		new_date.setDate(new_date.getDate()+1);
		setTargetDate(new_date);
	}




	const existNext=(d)=>{
		let today = new Date();
		let new_date = new Date(d.getTime());
		new_date.setDate(new_date.getDate());
		return lowerThanDateOnly(new_date, today);
	}



	useEffect(() => {
		//console.log("date->", target_date);
		// 初回呼び出しの場合、target_dateに本日をセットする
		if(target_date == undefined){
			setTargetDate(new Date());
		}
		else{
			// target_dateが変更になった時に、Nextボタンをdisableにするか判断
			//console.log("exist? : ", existNext(target_date));
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
		
	return(
		<>
			<div className="date_panel">
				<label className="date_title">日時</label>
				<div className="date_picker_panel">
					<Button variant="secondary" size="sm" style={{marginRight: "2px"}} onClick={setPrev} id="pvButton"> <i class="bi bi-caret-left-fill"></i> </Button>
					<DatePicker dateFormat="yyyy/MM/dd" locale='ja' selected={target_date} className="r_datepicker" value={target_date} onChange={setTargetDate} />
					<Button variant="secondary" size="sm" style={{marginLeft: "2px"}} onClick={setNext} id="nxButton"> <i class="bi bi-caret-right-fill"></i> </Button>
				</div>
			</div>
			{/* <input type="date" className="datepicker" value={target_date} onChange={handleDate}></input> */}

		</>
	);

}

export default AllGraphControlPanel;