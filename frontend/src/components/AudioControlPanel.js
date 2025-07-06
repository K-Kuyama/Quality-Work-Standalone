import React, { useState, useEffect } from 'react';
import {getBothEnds, lowerThanDateOnly} from "./utils";
import Button from 'react-bootstrap/Button';
import DatePicker, { registerLocale } from "react-datepicker";
import ja from 'date-fns/locale/ja';

function AudioControlPanel(props){
    const c_list = [["unuse","無効"],["front","Audio優先"],["back","Window優先"],["individual","個別設定"]]; 
    const [target_date, setDate] = useState(new Date())
    const [target_item, setItem] = useState("unuse");

    // const setParams = props.handler;
    const setTDate = props.date_handler;
    //const setTItem = props.item_handler;
    
    // このコンポーネントと親ページの両方の日時を設定
    // Datepickerの値の変更(onChange)で呼び出される
    const setTargetDate = (d) =>{
        console.log('set date -->', d);
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

    // Nextボタンの状態を未来には進めないようにセット。
    // target_dateが変更され、変更された日付が本日以降であればNextボタンを
    // disableする。
    useEffect(() => {
        //console.log("date->", target_date);
        if(target_date == undefined){
            // 初回のみ本日日付を設定するつもりだったが、
            // 余分なレンダリングを引き起こすのでやめる
            //setTargetDate(new Date());
        }
        else{
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

export default AudioControlPanel;    